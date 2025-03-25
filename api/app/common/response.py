from typing import TypeVar, Generic, Optional, Any, Callable
from pydantic import BaseModel, ConfigDict
from fastapi.responses import JSONResponse
from functools import partial
from .enums import ResponseCode, get_message

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: int
    msg: str
    data: Optional[T] = None


def create_response(
    *,
    code: ResponseCode,
    msg: Optional[str] = None,
    data: Optional[Any] = None,
) -> JSONResponse:
    """
    创建统一响应
    """
    return JSONResponse(
        status_code=200,
        content=ResponseModel(
            code=code, msg=msg or get_message(code), data=data
        ).model_dump(),
    )


# 使用偏函数创建特定类型的响应
success_response: Callable = partial(create_response, code=ResponseCode.SUCCESS)

error_response: Callable = partial(create_response, data=None)

# 预定义常用错误响应
param_error: Callable = partial(error_response, code=ResponseCode.PARAM_ERROR)

unauthorized_error: Callable = partial(error_response, code=ResponseCode.UNAUTHORIZED)

forbidden_error: Callable = partial(error_response, code=ResponseCode.FORBIDDEN)

not_found_error: Callable = partial(error_response, code=ResponseCode.NOT_FOUND)

internal_error: Callable = partial(error_response, code=ResponseCode.INTERNAL_ERROR)
