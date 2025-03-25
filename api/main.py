from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.middreware.exception_handler import register_exception_handlers
from app.controller import chat
from app.controller import manus
from app.core.setting import get_settings
from app.core.logger import setup_logging, logger

# 获取设置
settings = get_settings()


# 定义生命周期上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    await setup_logging()
    logger.info("日志系统已初始化")
    logger.info("应用程序已启动")

    yield

    # 关闭事件（如果有需要）
    logger.info("应用程序已关闭")


# 创建应用
app = FastAPI(
    title=settings.app.NAME,
    description=settings.app.DESCRIPTION,
    version=settings.app.VERSION,
    openapi_tags=[{"name": "系统", "description": "系统相关接口"}],
    docs_url=settings.api.DOCS_URL,
    redoc_url=settings.api.REDOC_URL,
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(chat.router)
app.include_router(manus.router)
