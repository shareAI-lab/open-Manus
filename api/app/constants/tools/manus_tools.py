from typing import Dict, List, Any
from dataclasses import dataclass
from .command_tool import CmdRunTool, CommandTool
from .edit_tool import LLMBasedFileEditTool
from .str_replace_tool import StrReplaceEditorTool


# * 将工具实例转换为统一的字典格式
def convert_tool_to_dict(tool: Any) -> Dict:
    if isinstance(tool, CommandTool):
        return {
            "name": tool.function.name,
            "description": tool.function.description,
            "parameters": tool.function.parameters["properties"],
        }
    elif isinstance(tool, dict):
        return tool
    else:
        raise ValueError(f"Unsupported tool type: {type(tool)}")


# * 注册工具实例到列表
def register_tools(*tools: Any) -> List[Dict]:
    return [convert_tool_to_dict(tool) for tool in tools]


# 基础工具列表
BASE_TOOLS = [
    {
        "name": "chat",
        "description": "聊天工具，可以与用户进行对话",
        "parameters": {"query": "string"},
    },
]


MANUS_TOOLS: List[Dict] = register_tools(
    *BASE_TOOLS,
    CmdRunTool,
    LLMBasedFileEditTool,
    StrReplaceEditorTool,
)


def get_manus_tools() -> List[Dict]:
    """
    获取所有可用的工具列表

    Returns:
        List[Dict]: 包含所有工具定义的列表
    """
    return MANUS_TOOLS


def get_tool_by_name(name: str) -> Dict | None:
    """
    根据工具名称获取工具定义

    Args:
        name: 工具名称

    Returns:
        Dict | None: 工具定义，如果未找到则返回 None
    """
    return next((tool for tool in MANUS_TOOLS if tool["name"] == name), None)


def get_tools_by_capability(required_params: List[str]) -> List[Dict]:
    """
    根据参数需求筛选工具

    Args:
        required_params: 需要的参数列表

    Returns:
        List[Dict]: 符合参数要求的工具列表
    """
    return [
        tool
        for tool in MANUS_TOOLS
        if all(param in tool["parameters"] for param in required_params)
    ]
