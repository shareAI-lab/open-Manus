import json
from app.agent.base import BaseAgent
from app.core.logger import log_info, log_error
from typing import List, Dict
from app.schema import AgentState
from dataclasses import asdict

from app.constants.tools.command_tool import CmdRunTool
from app.runtime.base import execute_command


class CommandAgent(BaseAgent):
    def __init__(
        self,
        name: str = "CommandAgent",
        query: str = "",
        purpose: str = "",
        target: str = "",
        result_path: str = "",
        container_id: str = "",
    ):
        super().__init__(name=name)
        self.state = AgentState.IDLE
        self.query = query
        self.purpose = purpose
        self.target = target
        self.tools = CmdRunTool
        self.result_path = result_path
        self.container_id = container_id
        self.max_retries = 5
        self.retry_count = 0
        self.is_retry = False

    async def build_prompt(self, query: str, purpose: str) -> str:
        # 使用函数式编程风格构建提示信息
        format_info = lambda label, content: (
            f"{label}：{content}" if content else f"没有提供{label}"
        )

        # 修复工具名称获取方式，处理单一工具对象
        get_tool_name = lambda tool: (
            tool.function.name
            if hasattr(tool, "function") and hasattr(tool.function, "name")
            else str(tool)
        )

        tool_info = get_tool_name(self.tools) if self.tools else ""

        info_parts = [
            format_info("用户的提问", query),
            format_info("用户的目的", purpose),
            format_info("可用工具", tool_info),
            format_info("当前的文件路径", self.result_path),
        ]

        return "\n".join(info_parts)

    async def build_retry_prompt(self, command: str, result: str) -> str:
        return f"""
        你是一个命令行专家，请分析以下命令执行结果，并提供修正：

        原始命令：
        {command}

        执行结果：
        {result}

        请根据执行结果来判断原始命令是否正确，如果执行结果表示命令错误，则调用  execute_bash 工具生成修正后的命令。
        如果是正确的，则返回原命令
        """

    async def step(self) -> str:
        self.retry_count = 0
        try:
            # 构建提示并获取响应
            user_prompt = await self.build_prompt(self.query, self.purpose)
            messages = [{"role": "user", "content": user_prompt}]

            # 获取工具字典并调用LLM
            tool_dict = asdict(self.tools)
            response = await self.llm.ask_tool(messages=messages, tools=[tool_dict])

            # 提取工具调用信息
            extract_command = lambda tool_call: (
                tool_call.function.arguments
                if hasattr(tool_call, "function")
                and hasattr(tool_call.function, "arguments")
                else "{}"
            )

            if (
                response
                and isinstance(response, list)
                and len(response) > 0
                and hasattr(response[0], "tool_calls")
                and response[0].tool_calls
            ):
                results = []
                for tool_call in response[0].tool_calls:
                    if hasattr(tool_call, "function"):
                        command_json = extract_command(tool_call)
                        result = await self._execute_command_in_path(command_json)
                        results.append(result)

                return "\n".join(filter(None, results))
            # 检查非列表形式的响应对象
            elif hasattr(response, "tool_calls") and response.tool_calls:
                results = []
                for tool_call in response.tool_calls:
                    if hasattr(tool_call, "function"):
                        command_json = extract_command(tool_call)
                        result = await self._execute_command_in_path(command_json)
                        results.append(result)

                return "\n".join(filter(None, results))
            else:
                return "没有找到可执行的命令"
        except Exception as e:
            log_error(f"执行步骤失败: {e}")
            import traceback

            log_error(f"错误详情: {traceback.format_exc()}")
            return f"执行步骤失败: {e}"

    async def need_retry(self, command: str, result: str) -> bool:
        messages = [
            {
                "role": "user",
                "content": await self.build_retry_prompt(command, result),
            }
        ]

        tool_dict = asdict(self.tools)
        response = await self.llm.ask_tool(messages=messages, tools=[tool_dict])

        if (
            response
            and hasattr(response, "tool_calls")
            and response.tool_calls
            and hasattr(response.tool_calls[0], "function")
        ):

            new_command_json = response.tool_calls[0].function.arguments
            new_command = json.loads(new_command_json).get("command", "")

        log_info(f"修正后的命令: {new_command}")
        if new_command == command:
            return True
        else:
            return False

    async def _execute_command_in_path(self, arguments_json: str) -> str:
        """在指定路径下执行命令"""
        import json

        try:
            args = json.loads(arguments_json)
            command = args.get("command", "")

            if not command:
                return "未提供命令"

            result = await execute_command(self.container_id, command)

            if (
                await self.need_retry(command, result)
                and self.retry_count < self.max_retries
            ):
                self.retry_count += 1
                return await self._execute_command_in_path(result)
            else:
                return result

        except json.JSONDecodeError:
            error_msg = f"解析命令参数失败: {arguments_json}"
            log_error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"执行命令时发生错误: {str(e)}"
            log_error(error_msg)
            return error_msg

    async def run(self) -> List[Dict]:
        user_prompt = await self.build_prompt(self.query, self.purpose)
        messages = [{"role": "user", "content": user_prompt}]
        try:
            tool_dict = asdict(self.tools)
            response = await self.llm.ask_tool(messages=messages, tools=[tool_dict])

            # 执行step方法并获取结果
            result = await self.step()
            log_info(f"执行步骤结果: {result}")

            # 返回包含响应和执行结果的列表
            return [{"response": response, "result": result}]
        except Exception as e:
            log_error(f"执行命令失败: {e}")
            return [{"error": f"执行命令失败: {e}"}]
