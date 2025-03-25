import uuid
import os
from fastapi import APIRouter
from pydantic import BaseModel
from app.common import success_response, error_response, ResponseCode
from app.service.manus_service import (
    generate_conversation_plan as generate_plan_service,
)
from app.controller.runtime import create_container

router = APIRouter(prefix="/api/manus", tags=["manus"])


class ManusRequest(BaseModel):
    query: str
    container_id: str


@router.post("/create-container")
async def create_runtime():
    try:
        container = await create_container()
        return success_response(data=container.id)
    except Exception as e:
        return error_response(code=ResponseCode.INTERNAL_ERROR, msg=str(e))


# 执行命令
# !todo: 修改为 wobsocket 或 sse
@router.post("/generate-plan")
async def generate_conversation_plan(request: ManusRequest):
    try:
        # 创建唯一标识符
        unique_id = str(uuid.uuid4())
        # 在当前目录下创建结果目录
        result_path = os.path.join("results", unique_id)
        # 确保目录存在
        os.makedirs(result_path, exist_ok=True)

        print(f"已创建结果目录: {result_path}")

        prompt = request.query
        # 调用服务层函数处理请求
        result = await generate_plan_service(prompt, result_path, request.container_id)

        return success_response(data=dict(result))
    except Exception as e:
        import traceback

        error_detail = str(e) + "\n" + traceback.format_exc()
        return error_response(
            data={"error": error_detail}, code=ResponseCode.INTERNAL_ERROR
        )
