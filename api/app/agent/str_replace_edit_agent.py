from app.constants.tools.str_replace_tool import StrReplaceEditorTool
from app.core.logger import log_info, log_error
from typing import Dict, List
from dataclasses import asdict
from app.agent.base import BaseAgent
from app.core.llm import LLM


class StrReplaceEditAgent(BaseAgent):
    def __init__(
        self,
        name: str = "StrReplaceEditAgent",
        query: str = "",
        purpose: str = "",
        result_path: str = "",
    ):
        super().__init__()
        self.name = name
        self.query = query
        self.purpose = purpose
        self.target_str = ""
        self.replace_instructions = ""
        self.tools = StrReplaceEditorTool
        self.result_path = result_path

    async def build_prompt(self, *args, **kwargs) -> str:
        # 使用函数式编程风格构建提示信息
        format_info = lambda label, content: (
            f"{label}：{content}" if content else f"没有提供{label}"
        )

        info_parts = [
            format_info("用户的提问", self.query),
            format_info("替换目的", self.purpose),
            format_info("目标字符串", self.target_str),
            format_info("替换说明", self.replace_instructions),
            format_info("当前的文件路径", self.result_path),
        ]

        # 使用函数式方法组合最终提示
        return "\n".join(info_parts)

    async def step(self, *args, **kwargs) -> str:
        pass

    async def run(self, *args, **kwargs) -> List[Dict]:
        prompt = await self.build_prompt(*args, **kwargs, result_path=self.result_path)
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.ask_tool(messages=messages, tools=[self.tools])
        return response
