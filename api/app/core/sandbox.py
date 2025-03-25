from typing import Optional, Dict, Any
from functools import partial
from contextlib import asynccontextmanager
import aiodocker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class SandboxConfig(BaseModel):
    image: str = "ubuntu:latest"
    memory_limit: str = "512m"
    cpu_limit: float = 0.5
    timeout: int = 30  # 秒
    command: Optional[str] = None
    working_dir: str = "/sandbox"


class SandboxManager:
    def __init__(self):
        self.docker = None

    async def __aenter__(self):
        self.docker = aiodocker.Docker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.docker:
            await self.docker.close()

    @staticmethod
    def create_container_config(config: SandboxConfig) -> Dict[str, Any]:
        """创建容器配置"""
        return {
            "Image": config.image,
            "Cmd": config.command.split() if config.command else None,
            "WorkingDir": config.working_dir,
            "HostConfig": {
                "Memory": int(
                    float(config.memory_limit[:-1]) * 1024 * 1024
                ),  # 转换为字节
                "CpuPeriod": 100000,
                "CpuQuota": int(config.cpu_limit * 100000),
                "NetworkMode": "none",  # 禁用网络
                "SecurityOpt": ["no-new-privileges"],
                "ReadonlyRootfs": True,  # 只读文件系统
                "CapDrop": ["ALL"],  # 移除所有权限
            },
        }

    async def run_sandbox(self, config: SandboxConfig) -> Dict[str, Any]:
        """运行沙箱环境"""
        container_config = self.create_container_config(config)

        try:
            container = await self.docker.containers.create(config=container_config)

            await container.start()

            # 等待容器执行完成或超时
            try:
                await container.wait(timeout=config.timeout)
            except TimeoutError:
                await container.kill()
                raise HTTPException(
                    status_code=408, detail="Sandbox execution timed out"
                )

            # 获取日志
            logs = await container.log(stdout=True, stderr=True)

            # 清理容器
            await container.delete(force=True)

            return {"status": "success", "logs": "".join(logs)}

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Sandbox execution failed: {str(e)}"
            )


app = FastAPI()


@asynccontextmanager
async def get_sandbox_manager():
    """异步上下文管理器获取沙箱管理器"""
    async with SandboxManager() as manager:
        yield manager


@app.post("/sandbox/run")
async def run_in_sandbox(config: SandboxConfig):
    """在沙箱中运行命令"""
    async with get_sandbox_manager() as manager:
        return await manager.run_sandbox(config)


# 示例使用
@app.post("/sandbox/execute")
async def execute_command(command: str):
    """执行简单的命令"""
    config = SandboxConfig(command=command, timeout=10)
    async with get_sandbox_manager() as manager:
        return await manager.run_sandbox(config)
