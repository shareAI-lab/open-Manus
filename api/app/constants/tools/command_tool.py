from typing import TypedDict, Literal
from dataclasses import dataclass

_BASH_DESCRIPTION = """在持久化的shell会话中执行bash命令。

### 命令执行
* 单次执行：每次只能执行一条bash命令。需要顺序执行多条命令时，使用`&&`或`;`连接。
* 会话持久化：环境变量、虚拟环境和工作目录在命令之间保持不变。
* 超时：命令有120秒的软超时限制。

### 进程管理
* 长时间运行：对于可能无限期运行的命令，使用后台运行并重定向输出，例如：`python3 app.py > server.log 2>&1 &`。
* 进程交互：当命令返回退出码`-1`时，可通过设置`is_input`为`true`来：
  - 发送空`command`获取更多日志
  - 发送文本到进程的STDIN
  - 发送控制命令如`C-c`、`C-d`或`C-z`中断进程

### 最佳实践
* 目录验证：创建新目录或文件前，先验证父目录存在且位置正确。
* 路径管理：尽量使用绝对路径，避免过度使用`cd`。

### 输出处理
* 输出截断：超出最大长度的输出将被截断。

### 如果是python相关的环境，使用uv进行虚拟环境等管理
### 如果是nodejs相关的环境，使用nvm进行nodejs版本管理
"""


class BashCommandParameters(TypedDict):
    command: str
    is_input: Literal["true", "false"]


@dataclass(frozen=True)
class CommandFunction:
    name: str
    description: str
    parameters: dict


@dataclass(frozen=True)
class CommandTool:
    type: str
    function: CommandFunction


def create_bash_parameters() -> dict:
    return {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute. Can be empty string to view additional logs when previous exit code is `-1`. Can be `C-c` (Ctrl+C) to interrupt the currently running process. Note: You can only execute one bash command at a time. If you need to run multiple commands sequentially, you can use `&&` or `;` to chain them together.",
            },
            "is_input": {
                "type": "string",
                "description": "If True, the command is an input to the running process. If False, the command is a bash command to be executed in the terminal. Default is False.",
                "enum": ["true", "false"],
            },
        },
        "required": ["command"],
    }


def create_command_tool(description: str) -> CommandTool:
    return CommandTool(
        type="function",
        function=CommandFunction(
            name="execute_bash",
            description=description,
            parameters=create_bash_parameters(),
        ),
    )


CmdRunTool = create_command_tool(_BASH_DESCRIPTION)
