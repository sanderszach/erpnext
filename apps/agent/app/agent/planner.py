"""
Planner node for the agent graph.

This module contains the planner node which takes user input
and generates a plan for execution.
"""

from app.agent.state import AgentState
from app.config import settings


async def planner_node(state: AgentState) -> AgentState:
    """
    Plan the execution based on user input.

    This node analyzes the user input and creates a plan for the executor.
    Currently uses mock logic - replace with actual LLM calls when ready.

    Args:
        state: The current agent state containing user input.

    Returns:
        Updated state with the generated plan.
    """
    user_input = state.get("input", "")

    # TODO: Replace with actual LLM planning call
    # Example with LangChain:
    #
    # from langchain_openai import ChatOpenAI
    # from langchain_core.messages import HumanMessage, SystemMessage
    #
    # llm = ChatOpenAI(
    #     model=settings.llm_model,
    #     api_key=settings.openai_api_key,
    # )
    #
    # messages = [
    #     SystemMessage(content="You are a planner. Create a step-by-step plan."),
    #     HumanMessage(content=user_input),
    # ]
    #
    # response = await llm.ainvoke(messages)
    # plan = response.content

    # Mock planning logic for demonstration
    plan = f"Plan for: '{user_input}'\n1. Analyze the request\n2. Determine required actions\n3. Execute and return results"

    # Log the planning step (in production, use proper logging)
    if settings.app_env == "development":
        print(f"[Planner] Generated plan for input: {user_input[:50]}...")

    return {
        **state,
        "plan": plan,
        "metadata": {
            **state.get("metadata", {}),
            "planner": {
                "model": settings.llm_model,
                "provider": settings.llm_provider,
            },
        },
    }

