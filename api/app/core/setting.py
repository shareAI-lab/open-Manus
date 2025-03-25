from functools import lru_cache
from typing import Dict, Any, Optional, List
from pydantic import Field, ConfigDict

# * 使用 pydantic_settings 替代 pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class EnvironmentType(str, Enum):
    """环境类型枚举"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class AppConfig(BaseSettings):
    """应用基本配置"""

    NAME: str = "FastAPI项目"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI项目描述"
    ENVIRONMENT: EnvironmentType = Field(
        default=EnvironmentType.DEVELOPMENT, env="ENVIRONMENT"
    )

    model_config = SettingsConfigDict(env_prefix="APP_")


class ServerConfig(BaseSettings):
    """服务器配置"""

    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=True, env="RELOAD")

    model_config = SettingsConfigDict(env_prefix="SERVER_")


class PostgresConfig(BaseSettings):
    """PostgreSQL 配置"""

    HOST: str = Field(default="localhost", env="HOST")
    PORT: int = Field(default=5432, env="PORT")
    USER: str = Field(default="postgres", env="USER")
    PASSWORD: str = Field(default="postgres", env="PASSWORD")
    DB: str = Field(default="postgres", env="DB")

    model_config = SettingsConfigDict(env_prefix="PG_")


class APIConfig(BaseSettings):
    """API 配置"""

    PREFIX: str = "/api"
    DOCS_URL: str = "/api/docs"
    REDOC_URL: str = "/api/redoc"

    model_config = SettingsConfigDict(env_prefix="API_")


class CORSConfig(BaseSettings):
    """跨域配置"""

    ORIGINS: List[str] = Field(default=["*"], env="ORIGINS")

    model_config = SettingsConfigDict(env_prefix="CORS_")


class LOGGERConfig(BaseSettings):
    """日志配置"""

    BASE_DIR: str = Field(default="logs", env="BASE_DIR")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_ROTATION: str = Field(default="00:00", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", env="LOG_RETENTION")
    LOG_COMPRESSION: str = Field(default="zip", env="LOG_COMPRESSION")
    model_config = SettingsConfigDict(env_prefix="LOGGER_")


class ChatConfig(BaseSettings):
    """聊天配置"""

    # 聊天代理配置
    base_url: str = Field(default="https://openai.super2brain.com/v1", env="BASE_URL")
    api_key: str = Field(
        default="sk-OSqhqCm1DoE24Kf0E2796eAeE75b484d9f08CbD779E7870a", env="API_KEY"
    )
    model: str = Field(default="gpt-4o-mini", env="MODEL")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    max_tokens: int = Field(default=4096, env="MAX_TOKENS")
    temperature: float = Field(default=1.0, env="TEMPERATURE")
    api_type: str = Field(default="openai", env="API_TYPE")
    api_version: str = Field(default="v1", env="API_VERSION")


class SandboxConfig(BaseSettings):
    """沙盒配置"""

    image: str = "ubuntu:latest"
    memory_limit: str = "512m"
    cpu_limit: float = 0.5
    timeout: int = 30  # 秒
    command: Optional[str] = "bash"
    working_dir: str = "/sandbox"


class Settings(BaseSettings):
    """组合所有配置的主类"""

    app: AppConfig = AppConfig()
    server: ServerConfig = ServerConfig()
    pg: PostgresConfig = PostgresConfig()
    api: APIConfig = APIConfig()
    cors: CORSConfig = CORSConfig()
    logger: LOGGERConfig = LOGGERConfig()
    chat: ChatConfig = ChatConfig()  # 聊天代理配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置单例"""
    return Settings()


settings = get_settings()
