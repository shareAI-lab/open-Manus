from app.runtime.base import create_container, delete_container, execute_command
from fastapi import APIRouter
from app.common.response import success_response, error_response, ResponseCode

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.post("/create")
async def create_runtime():
    try:
        container = await create_container()
        return success_response(data=container.id)
    except Exception as e:
        return error_response(code=ResponseCode.INTERNAL_ERROR, msg=str(e))


@router.post("/execute")
async def execute_runtime(container_id: str, command: str):
    try:
        result = await execute_command(container_id, command)
        return success_response(data=result)
    except Exception as e:
        return error_response(code=ResponseCode.INTERNAL_ERROR, msg=str(e))


@router.delete("/delete")
async def delete_runtime(container_id: str):
    try:
        await delete_container(container_id)
        return success_response()
    except Exception as e:
        return error_response(code=ResponseCode.INTERNAL_ERROR, msg=str(e))
