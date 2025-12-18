"""
Example tool demonstrating the tool interface pattern.

This module shows how to create LangChain-compatible tools
for use with the agent executor.
"""

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ExampleToolInput(BaseModel):
    """
    Input schema for the example tool.

    Using Pydantic models for tool inputs provides:
    - Type validation
    - Documentation generation
    - LLM-friendly schema descriptions
    """

    query: str = Field(
        ...,
        description="The query to process",
    )
    options: dict[str, str] | None = Field(
        default=None,
        description="Optional configuration options",
    )


class ExampleToolOutput(BaseModel):
    """
    Output schema for the example tool.

    Structured output helps with downstream processing
    and provides clear contracts for tool consumers.
    """

    result: str
    success: bool
    metadata: dict[str, str] = Field(default_factory=dict)


@tool(args_schema=ExampleToolInput)
def example_tool(query: str, options: dict[str, str] | None = None) -> dict:
    """
    An example tool that demonstrates the tool interface.

    This tool accepts a query and optional configuration,
    then returns a mock result. Replace with actual implementation.

    Args:
        query: The query to process.
        options: Optional configuration options.

    Returns:
        A dictionary with the result, success status, and metadata.
    """
    # Mock implementation - replace with actual logic
    result = ExampleToolOutput(
        result=f"Processed query: {query}",
        success=True,
        metadata={
            "tool": "example_tool",
            "query_length": str(len(query)),
            **(options or {}),
        },
    )

    return result.model_dump()

