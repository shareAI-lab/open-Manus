def build_plan_prompt(
    user_query: str, tools_str: str, context_str: str, result_path: str
) -> str:
    plan_prompt = """You are an AI assistant tasked with generating an execution plan based on user input and available tools. Please carefully analyze the user query and select appropriate tools to complete the task.

    User Query:
    {user_query}

    Available Tools:
    {tools_str}

    Context Information:
    {context_str}

    Result Path (current path exists):
    {result_path}

    Please generate a concise execution plan with the following requirements:
    1. Analyze user intent and select appropriate tools
    2. Arrange tool calls in the correct order
    3. Only provide tool names and call purposes, without specific parameters
    4. Specific parameters will be generated when executing each step
    5. If you need to use some environment variables, first determine if they exist, if not, return an error message
    
    Please return the plan in the following JSON format:
    {{
        "plan": [
            {{
                "tool": "tool_name",
                "purpose": {{
                    "description": "Description of this step's purpose",
                    "expected_result": "Description of the expected result from this step",
                    "fallback": "Alternative response if the tool call fails",
                    "status": "pending"
                }}
            }}
        ],
        "expected_result": "Description of the expected result from the entire plan",
        "fallback": {{
            "message": "Alternative response if the entire plan execution fails"
        }}
    }}

    Note:
    - Only return content in JSON format
    - Ensure all tool names exactly match the tool definitions
    - Do not provide specific parameters, as they will be dynamically generated when executing each step
    - Try to break down tasks into smaller parts, and make each purpose description concise and relevant to the main task.
    - Return results in English.
    """
    return plan_prompt.format(
        user_query=user_query,
        tools_str=tools_str,
        context_str=context_str,
        result_path=result_path,
    )
