from typing import TypedDict, Dict
from dataclasses import dataclass, asdict


class FileEditParameters(TypedDict):
    path: str
    content: str
    start: int
    end: int


@dataclass(frozen=True)
class EditFunction:
    name: str
    description: str
    parameters: dict


@dataclass(frozen=True)
class EditTool:
    type: str
    function: EditFunction

    def to_dict(self) -> Dict:
        """将 EditTool 转换为字典格式"""
        return {
            "type": self.type,
            "function": {
                "name": self.function.name,
                "description": self.function.description,
                "parameters": self.function.parameters,
            },
        }


def create_edit_parameters() -> dict:
    return {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The absolute path to the file to be edited.",
            },
            "content": {
                "type": "string",
                "description": "A draft of the new content for the file being edited. Note that the assistant may skip unchanged lines.",
            },
            "start": {
                "type": "integer",
                "description": "The starting line number for the edit (1-indexed, inclusive). Default is 1.",
            },
            "end": {
                "type": "integer",
                "description": "The ending line number for the edit (1-indexed, inclusive). Default is -1 (end of file).",
            },
        },
        "required": ["path", "content"],
    }


def create_edit_tool(description: str) -> EditTool:
    return EditTool(
        type="function",
        function=EditFunction(
            name="edit_file",
            description=description,
            parameters=create_edit_parameters(),
        ),
    )


# 保持原有的文件编辑描述
_FILE_EDIT_DESCRIPTION = """Edit a file in plain-text format.
* The assistant can edit files by specifying the file path and providing a draft of the new file content.
* The draft content doesn't need to be exactly the same as the existing file; the assistant may skip unchanged lines using comments like `# unchanged` to indicate unchanged sections.
* IMPORTANT: For large files (e.g., > 300 lines), specify the range of lines to edit using `start` and `end` (1-indexed, inclusive). The range should be smaller than 300 lines.
* To append to a file, set both `start` and `end` to `-1`.
* If the file doesn't exist, a new file will be created with the provided content.

**Example 1: general edit for short files**
For example, given an existing file `/path/to/file.py` that looks like this:
(this is the end of the file)
1|class MyClass:
2|    def __init__(self):
3|        self.x = 1
4|        self.y = 2
5|        self.z = 3
6|
7|print(MyClass().z)
8|print(MyClass().x)
(this is the end of the file)
```
"""

# 修改最终实例的创建方式，确保它可以被序列化
LLMBasedFileEditTool = create_edit_tool(_FILE_EDIT_DESCRIPTION).to_dict()
