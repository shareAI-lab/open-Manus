from app.agent.base import BaseAgent
from app.constants.prompts.plan_prompt import build_plan_prompt
from app.core.logger import log_info
from app.constants.tools.manus_tools import get_manus_tools
from typing import List, Dict
from app.schema import AgentState
from json import loads
from app.agent.comman_agent import CommandAgent
from app.agent.edit_file_agent import EditFileAgent
from app.agent.str_replace_edit_agent import StrReplaceEditAgent


class PlanAgent(BaseAgent):
    def __init__(
        self, name: str = "PlanAgent", result_path: str = "", container_id: str = ""
    ):
        super().__init__(name=name)
        self.plan = []
        self.current_step = 0
        self.query = ""
        self.context = ""
        self.tools = []
        self.state = AgentState.IDLE
        self.result_path = result_path
        self.container_id = container_id

    async def make_plan(self) -> str:
        tools_str = str(self.tools)
        prompt = build_plan_prompt(
            self.query, tools_str, self.context, self.result_path
        )
        messages = [{"role": "user", "content": prompt}]

        response = await self.llm.ask(messages)

        return response

    async def build_tools_list(self) -> List[Dict]:
        tools_list = get_manus_tools()
        return tools_list

    async def step(self) -> str:
        if not self.plan or self.current_step >= len(self.plan):
            self.state = AgentState.FINISHED
            return "计划已完成"

        current_action = self.plan[self.current_step]

        query = self.query
        purpose = current_action.get("purpose", "")
        target = current_action.get("expected_result", "")

        if current_action["tool"] == "execute_bash":
            command_agent = CommandAgent(
                query=query,
                purpose=purpose,
                target=target,
                result_path=self.result_path,
                container_id=self.container_id,
            )
            result = await command_agent.run()
            self.current_step += 1
            return result
        elif current_action["tool"] == "edit_file":
            # 获取编辑文件所需的特定参数
            target_file = current_action.get("target_file", "")
            edit_instructions = current_action.get("edit_instructions", "")

            edit_file_agent = EditFileAgent(
                query=query,
                purpose=purpose,
                target_file=target_file,
                edit_instructions=edit_instructions,
                result_path=self.result_path,
                container_id=self.container_id,
            )
            result = await edit_file_agent.run()
            self.current_step += 1
            return result
        elif current_action["tool"] == "str_replace_editor":
            str_replace_edit_agent = StrReplaceEditAgent(
                query=query,
                purpose=purpose,
                result_path=self.result_path,
            )
            result = await str_replace_edit_agent.run()
            self.current_step += 1
        return f"执行步骤: {current_action}"

    async def run(self, user_query: str) -> List[Dict]:
        self.state = AgentState.RUNNING
        self.query = user_query
        self.tools = await self.build_tools_list()
        plans = await self.make_plan()

        try:
            if not plans or not plans.strip():
                self.plan = []
            else:
                # 尝试提取JSON部分
                json_start = plans.find("{")
                json_end = plans.rfind("}") + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = plans[json_start:json_end]
                    parsed_plans = loads(json_str)

                    # 检查是否包含 plan 键
                    if isinstance(parsed_plans, dict) and "plan" in parsed_plans:
                        self.plan = parsed_plans["plan"]
                    else:
                        # 如果返回的直接是列表，则使用它
                        self.plan = (
                            parsed_plans if isinstance(parsed_plans, list) else []
                        )
                else:
                    self.plan = []
        except Exception as e:
            log_info(f"解析计划时出错: {str(e)}")
            # 发生错误时使用空计划
            self.plan = []

        while self.state != AgentState.FINISHED:
            step_result = await self.step()
            log_info(f"执行步骤结果: {step_result}")

        return self.plan
