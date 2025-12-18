"""
LangGraph state machine definition.

This module builds the agent graph wiring planner → executor.
"""

from typing import Any

from langgraph.graph import END, StateGraph

from app.agent.executor import executor_node
from app.agent.planner import planner_node
from app.agent.state import AgentState


def build_agent_graph() -> StateGraph:
    """
    Build the agent state graph.

    Creates a LangGraph StateGraph with the following flow:
    START → planner → executor → END

    Returns:
        A compiled LangGraph StateGraph.
    """
    # Create the graph with our state type
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)

    # Define edges
    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", END)

    # Compile and return
    return graph.compile()


# Create the compiled graph instance
agent_graph = build_agent_graph()


async def run_agent(
    input_text: str,
    session_id: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run the agent with the given input.

    This is the main entry point for executing the agent graph.

    Args:
        input_text: The user input to process.
        session_id: Session identifier for the conversation.
        config: Optional configuration for the graph run.

    Returns:
        A dictionary containing the final agent state.
    """
    # Initialize the state
    initial_state: AgentState = {
        "input": input_text,
        "session_id": session_id,
        "plan": None,
        "output": "",
        "messages": [],
        "metadata": {},
        "error": None,
    }

    # Run configuration
    run_config = config or {}

    # TODO: Add checkpointing for state persistence
    # from langgraph.checkpoint.memory import MemorySaver
    # checkpointer = MemorySaver()
    # graph = build_agent_graph().compile(checkpointer=checkpointer)

    # Execute the graph
    final_state = await agent_graph.ainvoke(initial_state, config=run_config)

    return {
        "plan": final_state.get("plan"),
        "output": final_state.get("output", ""),
        "metadata": final_state.get("metadata", {}),
    }

