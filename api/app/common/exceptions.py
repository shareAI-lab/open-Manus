from typing import Any, Optional
from fastapi import status
from .enums import ResponseCode, get_message


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        code: ResponseCode,
        msg: Optional[str] = None,
        data: Any = None,
    ):
        self.code = code
        self.msg = msg or get_message(code)
        self.data = data
