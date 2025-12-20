"""
Tool interfaces for the agent.

This package contains LangChain-compatible tools that can be
invoked by the agent executor.
"""

from app.tools.example_tool import example_tool
from app.tools.erpnext_tools import (
    ERPNEXT_TOOLS,
    create_document,
    delete_document,
    get_document,
    get_documents,
    get_doctype_fields,
    get_doctypes,
    run_report,
    update_document,
)

# List of all available tools
AVAILABLE_TOOLS = [
    example_tool,
    *ERPNEXT_TOOLS,
]


def get_available_tools() -> list:
    """
    Get all available tools for the agent.

    Returns:
        A list of LangChain-compatible tools.
    """
    return AVAILABLE_TOOLS


def get_erpnext_tools() -> list:
    """
    Get only ERPNext tools.

    Returns:
        A list of ERPNext-specific tools.
    """
    return ERPNEXT_TOOLS


__all__ = [
    # Tool functions
    "example_tool",
    "get_doctypes",
    "get_doctype_fields",
    "get_document",
    "get_documents",
    "create_document",
    "update_document",
    "delete_document",
    "run_report",
    # Tool registries
    "AVAILABLE_TOOLS",
    "ERPNEXT_TOOLS",
    "get_available_tools",
    "get_erpnext_tools",
]
