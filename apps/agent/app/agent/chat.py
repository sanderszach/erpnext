"""
Chat agent using LangChain ReAct pattern with tools.

This module provides a simple chat interface that uses an LLM
with access to ERPNext tools and conversation memory.
"""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

from app.agent.memory import get_memory_store
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
    session_id: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """
    Chat with the ERPNext agent.

    Supports two modes:
    1. Session-based memory: Pass a session_id to automatically persist conversation
    2. Manual history: Pass conversation_history for stateless operation

    Args:
        message: The user's message.
        session_id: Optional session ID for automatic memory persistence.
        conversation_history: Optional list of previous messages (used if no session_id).

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

    # Get conversation history from memory or from provided history
    memory_store = get_memory_store()
    session = None

    if session_id:
        # Use session-based memory
        session = memory_store.get_session(session_id)
        for msg in session.get_recent_messages(limit=50):
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
    elif conversation_history:
        # Use provided history
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    # Add the current message
    messages.append(HumanMessage(content=message))

    # Save user message to session if using memory
    if session:
        session.add_message("user", message)

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
            response_text = response.content

            # Save assistant response to session if using memory
            if session:
                session.add_message("assistant", response_text)

            return {
                "response": response_text,
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
                "result_preview": tool_result,
            })

            # Add tool result to messages
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

    # If we hit max iterations, return what we have
    fallback_response = "I've made several tool calls but haven't reached a final answer. Here's what I found so far."

    # Save to session even on fallback
    if session:
        session.add_message("assistant", fallback_response)

    return {
        "response": fallback_response,
        "tool_calls": tool_calls_made,
        "error": False,
        "warning": "Max iterations reached",
    }


async def clear_session(session_id: str) -> bool:
    """
    Clear conversation history for a session.

    Args:
        session_id: The session to clear.

    Returns:
        True if session was cleared/deleted.
    """
    memory_store = get_memory_store()
    return memory_store.delete_session(session_id)


async def get_session_history(session_id: str) -> list[dict[str, str]]:
    """
    Get conversation history for a session.

    Args:
        session_id: The session ID.

    Returns:
        List of messages with role and content.
    """
    memory_store = get_memory_store()
    session = memory_store.get_session(session_id)
    return session.get_messages_for_llm()

