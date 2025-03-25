import sys
import logging
import asyncio
import os
import uuid
import functools
from datetime import datetime
from pathlib import Path
from loguru import logger
from typing import Callable, Any, Dict, Optional
from app.core.setting import get_settings

from contextvars import ContextVar

settings = get_settings()

# 添加上下文变量存储请求UUID
request_uuid: ContextVar[Optional[str]] = ContextVar("request_uuid", default=None)


def get_request_uuid() -> Optional[str]:
    """获取当前请求的UUID"""
    return request_uuid.get()


def set_request_uuid(uuid_str: Optional[str]) -> None:
    """设置当前请求的UUID"""
    request_uuid.set(uuid_str)


# 修改装饰器，使其更加函数式，并确保所有日志都包含UUID
def log_request(
    url: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    level: str = "INFO",
) -> Callable:
    """
    记录请求信息的装饰器，自动为请求生成UUID并绑定到所有日志

    Args:
        url: 请求的URL
        params: 请求参数
        level: 日志级别

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成UUID并设置到上下文
            req_uuid = str(uuid.uuid4())
            set_request_uuid(req_uuid)

            # 获取当前日期，格式为YYYYMMDD
            date_str = datetime.now().strftime("%Y%m%d")

            # 记录请求信息
            log_data = {
                "uuid": req_uuid,
                "date": date_str,
                "url": url,
                "params": params or kwargs,
            }

            # 使用绑定的logger记录请求开始
            logger.bind(request_uuid=req_uuid).log(level, f"请求开始: {log_data}")

            try:
                result = await func(*args, **kwargs)
                # 使用绑定的logger记录请求成功
                logger.bind(request_uuid=req_uuid).log(
                    level, f"请求成功完成: {req_uuid}"
                )
                return result
            except Exception as e:
                # 使用绑定的logger记录请求异常
                logger.bind(request_uuid=req_uuid).error(
                    f"请求异常: {req_uuid}, 错误: {str(e)}"
                )
                raise
            finally:
                # 清除上下文中的UUID
                set_request_uuid(None)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 生成UUID并设置到上下文
            req_uuid = str(uuid.uuid4())
            set_request_uuid(req_uuid)

            # 获取当前日期，格式为YYYYMMDD
            date_str = datetime.now().strftime("%Y%m%d")

            # 记录请求信息
            log_data = {
                "uuid": req_uuid,
                "date": date_str,
                "url": url,
                "params": params or kwargs,
            }

            # 使用绑定的logger记录请求开始
            logger.bind(request_uuid=req_uuid).log(level, f"请求开始: {log_data}")

            try:
                result = func(*args, **kwargs)
                # 使用绑定的logger记录请求成功
                logger.bind(request_uuid=req_uuid).log(
                    level, f"请求成功完成: {req_uuid}"
                )
                return result
            except Exception as e:
                # 使用绑定的logger记录请求异常
                logger.bind(request_uuid=req_uuid).error(
                    f"请求异常: {req_uuid}, 错误: {str(e)}"
                )
                raise
            finally:
                # 清除上下文中的UUID
                set_request_uuid(None)

        # 根据函数是否为协程函数返回对应的包装器
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# 替换原有的log_with_uuid函数，使用更函数式的方法
def get_logger():
    """
    获取带有当前请求UUID的logger实例

    Returns:
        绑定了当前请求UUID的logger实例
    """
    uuid_str = get_request_uuid()
    return logger.bind(request_uuid=uuid_str if uuid_str else "无UUID")


# 定义常用日志级别的快捷函数
def log_info(message: str, **kwargs):
    """记录INFO级别日志，自动附带当前请求UUID"""
    get_logger().bind(**kwargs).info(message)


def log_error(message: str, **kwargs):
    """记录ERROR级别日志，自动附带当前请求UUID"""
    get_logger().bind(**kwargs).error(message)


def log_debug(message: str, **kwargs):
    """记录DEBUG级别日志，自动附带当前请求UUID"""
    get_logger().bind(**kwargs).debug(message)


def log_warning(message: str, **kwargs):
    """记录WARNING级别日志，自动附带当前请求UUID"""
    get_logger().bind(**kwargs).warning(message)


class InterceptHandler(logging.Handler):
    """
    日志拦截处理器：将所有 Python 标准日志重定向到 Loguru

    工作原理：
    1. 继承自 logging.Handler
    2. 重写 emit 方法处理日志记录
    3. 将标准库日志转换为 Loguru 格式
    """

    def emit(self, record: logging.LogRecord) -> None:
        # 尝试获取日志级别名称
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 获取调用帧信息
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 获取当前请求UUID并绑定到日志
        uuid_str = get_request_uuid()
        log_instance = logger.bind(request_uuid=uuid_str if uuid_str else "无UUID")

        # 使用 Loguru 记录日志
        log_instance.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# 使用更函数式的方法重构setup_logging
async def setup_logging():
    """
    配置日志系统

    功能：
    1. 控制台彩色输出
    2. 文件日志轮转
    3. 错误日志单独存储
    4. 异步日志记录
    5. 请求UUID跟踪
    """
    # 步骤1：移除默认处理器
    logger.remove()

    # 步骤2：定义日志格式，添加UUID信息
    log_format = (
        # 时间信息
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        # 日志级别，居中对齐
        "<level>{level: ^8}</level> | "
        # 进程和线程信息
        "process [<cyan>{process}</cyan>]:<cyan>{thread}</cyan> | "
        # 请求UUID
        "<magenta>{extra[request_uuid]}</magenta> | "
        # 文件、函数和行号
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        # 日志消息
        "<level>{message}</level>"
    )

    # 定义更安全的 filter 函数
    def ensure_request_uuid(record):
        if "request_uuid" not in record["extra"]:
            record["extra"]["request_uuid"] = "无UUID"
        return True

    # 步骤3：配置控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.logger.DEBUG else "INFO",
        enqueue=True,  # 启用异步写入
        backtrace=True,  # 显示完整的异常回溯
        diagnose=True,  # 显示变量值等诊断信息
        colorize=True,  # 启用彩色输出
        filter=ensure_request_uuid,
    )

    # 使用函数式方法创建目录
    async def async_makedirs(path: str, exist_ok: bool = True) -> None:
        """
        异步创建目录。

        Args:
            path (str): 要创建的目录路径
            exist_ok (bool): 如果目录已存在，是否忽略错误
        """
        await asyncio.to_thread(os.makedirs, path, exist_ok=exist_ok)

    # 步骤4：创建日志目录
    log_dir = Path(settings.logger.BASE_DIR) / "logs"
    await async_makedirs(str(log_dir))

    # 创建 info 和 error 子目录
    info_dir = log_dir / "info"
    error_dir = log_dir / "error"
    await async_makedirs(str(info_dir))
    await async_makedirs(str(error_dir))

    # 步骤5：配置常规日志文件
    logger.add(
        str(info_dir / "{time:YYYY-MM-DD}_info.log"),
        format=log_format,
        level="INFO",
        rotation=settings.logger.LOG_ROTATION,  # 每天轮转
        retention=settings.logger.LOG_RETENTION,  # 保留30天
        compression=settings.logger.LOG_COMPRESSION,  # 压缩旧日志
        encoding="utf-8",
        enqueue=True,  # 异步写入
        filter=ensure_request_uuid,
    )

    # 步骤6：配置错误日志文件
    logger.add(
        str(error_dir / "{time:YYYY-MM-DD}_error.log"),
        format=log_format,
        level="ERROR",
        rotation=settings.logger.LOG_ROTATION,
        retention=settings.logger.LOG_RETENTION,
        compression=settings.logger.LOG_COMPRESSION,
        encoding="utf-8",
        enqueue=True,
        filter=ensure_request_uuid,
    )

    # 步骤7：首先配置标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 步骤8：确保拦截所有第三方库日志
    for _log in logging.Logger.manager.loggerDict.values():
        if isinstance(_log, logging.Logger):
            _log.handlers = [InterceptHandler()]
            _log.propagate = False
            _log.level = 0

    # 步骤9：特别处理 Uvicorn 相关日志器
    for logger_name in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "uvicorn.asgi",
        "fastapi",
        "fastapi.error",
    ]:
        _logger = logging.getLogger(logger_name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False
        _logger.level = 0

    # 禁用 Uvicorn 的默认日志配置
    logging.getLogger("uvicorn.access").disabled = True

    logger.info("日志系统初始化完成")
