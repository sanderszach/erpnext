"""
Tool interfaces for the agent.

This package contains LangChain-compatible tools that can be
invoked by the agent executor.
"""

from app.tools.example_tool import example_tool

# List of all available tools
AVAILABLE_TOOLS = [
    example_tool,
]


def get_available_tools() -> list:
    """
    Get all available tools for the agent.

    Returns:
        A list of LangChain-compatible tools.
    """
    return AVAILABLE_TOOLS


__all__ = ["example_tool", "get_available_tools", "AVAILABLE_TOOLS"]

