from app.agent import PlanAgent
from typing import Dict


async def generate_conversation_plan(
    query: str, result_path: str, container_id: str
) -> Dict[str, str]:
    """
    生成对话计划的服务函数

    Args:
        query: 用户查询字符串

    Returns:
        包含生成计划的字典
    """
    # 调用 plan_agent 生成计划
    plan_agent = PlanAgent(result_path=result_path, container_id=container_id)

    execution_result = await plan_agent.run(query)

    # 将字符串结果包装成字典返回
    return {"plan": execution_result}
