import json
import os
from app.agent.base import BaseAgent
from app.core.logger import log_info, log_error
from app.constants.tools.edit_tool import LLMBasedFileEditTool
from typing import List, Dict
from app.schema import AgentState
from dataclasses import asdict
from pathlib import Path
from app.runtime.base import execute_command


class EditFileAgent(BaseAgent):
    def __init__(
        self,
        name: str = "EditFileAgent",
        query: str = "",
        purpose: str = "",
        target_file: str = "",
        edit_instructions: str = "",
        result_path: str = "",
        container_id: str = "",
    ):
        super().__init__(name=name)
        self.state = AgentState.IDLE
        self.query = query
        self.purpose = purpose
        self.target_file = target_file
        self.edit_instructions = edit_instructions
        self.tools = LLMBasedFileEditTool
        self.result_path = result_path
        self.container_id = container_id

    async def build_prompt(self) -> str:
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
            format_info("用户的提问", self.query),
            format_info("编辑目的", self.purpose),
            format_info("目标文件", self.target_file),
            format_info("编辑说明", self.edit_instructions),
            format_info("可用工具", tool_info),
            format_info("当前的文件路径", self.result_path),
        ]

        # 使用函数式方法组合最终提示
        return "\n".join(info_parts)

    async def step(self) -> str:
        try:
            # 获取工具调用结果
            tool_calls = (
                self.llm.last_response.tool_calls
                if hasattr(self.llm, "last_response")
                and hasattr(self.llm.last_response, "tool_calls")
                else []
            )

            # 使用函数式方法处理工具调用
            results = []

            for tool_call in tool_calls:
                if tool_call.function.name == "edit_file":
                    args = json.loads(tool_call.function.arguments)
                    file_path = args.get("path", "")
                    content = args.get("content", "")

                    # 如果有容器ID，则在容器中执行文件写入
                    if self.container_id:
                        write_command = f'echo "{content}" > {file_path}'
                        result = await execute_command(self.container_id, write_command)
                        results.append(
                            f"在容器 {self.container_id} 中写入文件: {file_path}"
                        )
                        log_info(f"容器文件写入结果: {result}")
                    else:
                        # 原有的本地文件写入逻辑
                        ensure_dir = lambda path: Path(path).parent.mkdir(
                            parents=True, exist_ok=True
                        )
                        ensure_dir(file_path)

                        write_file = lambda path, content: Path(path).write_text(
                            content
                        )
                        write_file(file_path, content)

                        results.append(f"已成功写入本地文件: {file_path}")
                        log_info(f"已成功写入本地文件: {file_path}")

            return "\n".join(results) if results else "没有执行文件写入操作"
        except Exception as e:
            error_msg = f"文件写入过程中出错: {str(e)}"
            log_error(error_msg)
            return error_msg

    async def run(self) -> List[Dict]:
        prompt = await self.build_prompt()
        messages = [{"role": "user", "content": prompt}]
        try:
            if isinstance(self.tools, type):
                # 如果是类，创建实例
                tool_instance = self.tools()
                tool_dict = asdict(tool_instance)
            elif isinstance(self.tools, dict):
                # 如果已经是字典，直接使用
                tool_dict = self.tools
            else:
                # 如果是 dataclass 实例，使用 asdict
                tool_dict = asdict(self.tools)

            response = await self.llm.ask_tool(messages=messages, tools=[tool_dict])
            log_info(f"编辑文件的响应: {response}")

            await self.step()
            return response
        except Exception as e:
            log_error(f"文件编辑失败: {e}")
            return f"文件编辑失败: {e}"
