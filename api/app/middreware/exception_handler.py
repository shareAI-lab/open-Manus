from typing import Callable
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.common import BusinessException, error_response, ResponseCode


async def handle_business_exception(
    request: Request, exc: BusinessException
) -> JSONResponse:
    """处理业务异常"""
    return error_response(code=exc.code, msg=exc.msg, data=exc.data)


async def handle_validation_exception(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理请求参数验证异常"""
    return error_response(code=ResponseCode.PARAM_ERROR, msg=str(exc))


async def handle_general_exception(request: Request, exc: Exception) -> JSONResponse:
    """处理通用异常"""
    return error_response(code=ResponseCode.INTERNAL_ERROR, msg=str(exc))


def register_exception_handlers(app) -> None:
    """注册异常处理器"""
    handlers = [
        (BusinessException, handle_business_exception),
        (RequestValidationError, handle_validation_exception),
        (Exception, handle_general_exception),
    ]

    for exc, handler in handlers:
        app.add_exception_handler(exc, handler)
