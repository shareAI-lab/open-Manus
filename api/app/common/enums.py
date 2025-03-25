from enum import IntEnum
from typing import Dict


# 使用 IntEnum 枚举类型，并使用不可变字典存储状态码消息
# 根据具体的业务需求，在大类下面添加细分的状态码
class ResponseCode(IntEnum):
    """响应状态码枚举"""
    SUCCESS = 20000
    PARAM_ERROR = 40000
    UNAUTHORIZED = 40100
    FORBIDDEN = 40300
    NOT_FOUND = 40400
    METHOD_NOT_ALLOWED = 40500
    INTERNAL_ERROR = 50000
    SERVICE_BUSY = 50300
    GATEWAY_ERROR = 50400

# 部分状态码在生产环境中不应该有日志
# 如参数错误，或者成功的请求，不应该有日志
RESPONSE_MESSAGE: Dict[ResponseCode, str] = {
    ResponseCode.SUCCESS: "请求成功",
    ResponseCode.PARAM_ERROR: "参数错误",
    ResponseCode.UNAUTHORIZED: "未授权",
    ResponseCode.FORBIDDEN: "禁止访问",
    ResponseCode.NOT_FOUND: "资源不存在",
    ResponseCode.METHOD_NOT_ALLOWED: "方法不允许",
    ResponseCode.INTERNAL_ERROR: "服务器内部错误",
    ResponseCode.SERVICE_BUSY: "服务繁忙",
    ResponseCode.GATEWAY_ERROR: "网关错误"
}

def get_message(code: ResponseCode) -> str:
    """获取状态码对应的消息"""
    return RESPONSE_MESSAGE.get(code, "未知错误") 