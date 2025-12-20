"""
Chat agent using LangChain ReAct pattern with tools.

This module provides a simple chat interface that uses an LLM
with access to ERPNext tools.
"""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.tools import get_erpnext_tools

# System prompt for the ERPNext agent
SYSTEM_PROMPT = """You are an intelligent assistant with access to an ERPNext system.

You can help users:
- Discover available document types (DocTypes) in the system
- List, search, and filter documents
- Get details about specific documents
- Create new documents
- Update existing documents
- Run reports

When asked about ERPNext data:
1. First understand what the user needs
2. Use the appropriate tools to fetch or modify data
3. Present the results in a clear, helpful way

Always be helpful and explain what you're doing. If you encounter errors,
explain them clearly and suggest alternatives.

Important: Before creating or updating documents, always confirm the action
with the user and show them what data will be written."""


async def chat_with_agent(
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Chat with the ERPNext agent.

    Args:
        message: The user's message.
        conversation_history: Optional list of previous messages.

    Returns:
        Dictionary with the agent's response and metadata.
    """
    # Validate configuration
    if not settings.openai_api_key:
        return {
            "response": "Error: OpenAI API key is not configured. Please set OPENAI_API_KEY in your environment.",
            "tool_calls": [],
            "error": True,
        }

    # Initialize the LLM
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    # Get ERPNext tools
    tools = get_erpnext_tools()

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Build message history
    messages: list[Any] = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    # Add the current message
    messages.append(HumanMessage(content=message))

    # Track tool calls made
    tool_calls_made: list[dict[str, Any]] = []

    # Execute with tool calling loop
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get LLM response
        response = await llm_with_tools.ainvoke(messages)

        # Check if we need to call tools
        if not response.tool_calls:
            # No more tool calls, return the final response
            return {
                "response": response.content,
                "tool_calls": tool_calls_made,
                "error": False,
            }

        # Process tool calls
        messages.append(response)

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Find and execute the tool
            tool_result = None
            for tool in tools:
                if tool.name == tool_name:
                    try:
                        # Execute the tool (tools are async)
                        tool_result = await tool.ainvoke(tool_args)
                    except Exception as e:
                        tool_result = f"Error executing {tool_name}: {str(e)}"
                    break

            if tool_result is None:
                tool_result = f"Unknown tool: {tool_name}"

            # Record the tool call
            tool_calls_made.append({
                "tool": tool_name,
                "args": tool_args,
                "result_preview": str(tool_result)[:200] + "..." if len(str(tool_result)) > 200 else str(tool_result),
            })

            # Add tool result to messages
            from langchain_core.messages import ToolMessage
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    # If we hit max iterations, return what we have
    return {
        "response": "I've made several tool calls but haven't reached a final answer. Here's what I found so far.",
        "tool_calls": tool_calls_made,
        "error": False,
        "warning": "Max iterations reached",
    }

