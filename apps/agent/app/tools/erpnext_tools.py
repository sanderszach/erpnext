"""
ERPNext tools for the agent.

This module provides LangChain-compatible tools for interacting with ERPNext.
"""

import json
from typing import Any

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.tools.erpnext_client import ERPNextClientError, get_erpnext_client


# ============================================================================
# Input Schemas
# ============================================================================


class GetDocumentInput(BaseModel):
    """Input for getting a single document."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")
    name: str = Field(..., description="Document name/ID")


class GetDocumentsInput(BaseModel):
    """Input for listing documents."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")
    filters: dict[str, Any] | None = Field(
        default=None,
        description="Filter conditions as {field: value} (e.g., {'status': 'Active'})",
    )
    fields: list[str] | None = Field(
        default=None,
        description="Fields to include (e.g., ['name', 'customer_name']). Use ['*'] for all.",
    )
    limit: int | None = Field(
        default=20,
        description="Maximum number of documents to return",
        ge=1,
        le=500,
    )
    order_by: str | None = Field(
        default=None,
        description="Field to order by (e.g., 'creation desc')",
    )


class CreateDocumentInput(BaseModel):
    """Input for creating a document."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")
    data: dict[str, Any] = Field(..., description="Document data to create")


class UpdateDocumentInput(BaseModel):
    """Input for updating a document."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")
    name: str = Field(..., description="Document name/ID to update")
    data: dict[str, Any] = Field(..., description="Fields to update")


class DeleteDocumentInput(BaseModel):
    """Input for deleting a document."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")
    name: str = Field(..., description="Document name/ID to delete")


class RunReportInput(BaseModel):
    """Input for running a report."""

    report_name: str = Field(..., description="Name of the ERPNext report")
    filters: dict[str, Any] | None = Field(
        default=None,
        description="Report filters",
    )


class GetDoctypeFieldsInput(BaseModel):
    """Input for getting doctype fields."""

    doctype: str = Field(..., description="ERPNext DocType (e.g., Customer, Item)")


# ============================================================================
# Tools
# ============================================================================


@tool(args_schema=GetDocumentInput)
async def get_document(doctype: str, name: str) -> str:
    """
    Get a single ERPNext document by doctype and name.

    Use this to fetch the complete details of a specific document when you
    know its exact name/ID.

    Args:
        doctype: The ERPNext DocType (e.g., "Customer", "Sales Order").
        name: The document name/ID.

    Returns:
        JSON string with the document data.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        document = await client.get_document(doctype, name)
        return json.dumps(document, indent=2, default=str)
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=GetDocumentsInput)
async def get_documents(
    doctype: str,
    filters: dict[str, Any] | None = None,
    fields: list[str] | None = None,
    limit: int | None = 20,
    order_by: str | None = None,
) -> str:
    """
    Get a list of ERPNext documents for a doctype.

    Use this to search and list documents with optional filtering and field selection.

    Args:
        doctype: The ERPNext DocType (e.g., "Customer", "Item").
        filters: Filter conditions as {field: value}.
        fields: Fields to include in response. Use ["*"] for all fields.
        limit: Maximum number of documents (default 20, max 500).
        order_by: Field to order by (e.g., "creation desc").

    Returns:
        JSON string with list of documents.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        documents = await client.get_documents(
            doctype=doctype,
            filters=filters,
            fields=fields,
            limit=limit,
            order_by=order_by,
        )
        return json.dumps(
            {"count": len(documents), "documents": documents},
            indent=2,
            default=str,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=CreateDocumentInput)
async def create_document(doctype: str, data: dict[str, Any]) -> str:
    """
    Create a new document in ERPNext.

    Use this to create a new document of any DocType. Make sure to include
    all required fields for the DocType.

    Args:
        doctype: The ERPNext DocType (e.g., "Customer", "Item").
        data: The document data with field values.

    Returns:
        JSON string with the created document.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        document = await client.create_document(doctype, data)
        return json.dumps(
            {
                "success": True,
                "message": f"Created {doctype}: {document.get('name')}",
                "document": document,
            },
            indent=2,
            default=str,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=UpdateDocumentInput)
async def update_document(doctype: str, name: str, data: dict[str, Any]) -> str:
    """
    Update an existing document in ERPNext.

    Use this to modify fields on an existing document. Only include the
    fields you want to change.

    Args:
        doctype: The ERPNext DocType (e.g., "Customer", "Item").
        name: The document name/ID to update.
        data: The fields to update.

    Returns:
        JSON string with the updated document.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        document = await client.update_document(doctype, name, data)
        return json.dumps(
            {
                "success": True,
                "message": f"Updated {doctype}: {name}",
                "document": document,
            },
            indent=2,
            default=str,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=DeleteDocumentInput)
async def delete_document(doctype: str, name: str) -> str:
    """
    Delete a document from ERPNext.

    Use this carefully - deletion may be permanent or may fail if the
    document is linked to other records.

    Args:
        doctype: The ERPNext DocType.
        name: The document name/ID to delete.

    Returns:
        JSON string with deletion result.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        await client.delete_document(doctype, name)
        return json.dumps(
            {
                "success": True,
                "message": f"Deleted {doctype}: {name}",
            },
            indent=2,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=RunReportInput)
async def run_report(
    report_name: str, filters: dict[str, Any] | None = None
) -> str:
    """
    Run an ERPNext report.

    Use this to execute built-in or custom ERPNext reports with optional filters.

    Args:
        report_name: Name of the report to run.
        filters: Optional filter parameters for the report.

    Returns:
        JSON string with report results.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        result = await client.run_report(report_name, filters)
        return json.dumps(result, indent=2, default=str)
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool
async def get_doctypes() -> str:
    """
    Get a list of all available ERPNext DocTypes.

    Use this to discover what types of documents are available in the
    ERPNext instance. Common DocTypes include Customer, Supplier, Item,
    Sales Order, Purchase Order, etc.

    Returns:
        JSON string with list of DocType names.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        doctypes = await client.get_all_doctypes()
        return json.dumps(
            {"count": len(doctypes), "doctypes": doctypes},
            indent=2,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


@tool(args_schema=GetDoctypeFieldsInput)
async def get_doctype_fields(doctype: str) -> str:
    """
    Get the field definitions for a specific ERPNext DocType.

    Use this to understand what fields are available on a DocType before
    creating or updating documents. Shows field names, types, and requirements.

    Args:
        doctype: The ERPNext DocType (e.g., "Customer", "Item").

    Returns:
        JSON string with field definitions.
    """
    try:
        client = get_erpnext_client()
        if not client.is_authenticated():
            return json.dumps({"error": "ERPNext API credentials not configured"})

        fields = await client.get_doctype_fields(doctype)
        return json.dumps(
            {"doctype": doctype, "field_count": len(fields), "fields": fields},
            indent=2,
        )
    except ERPNextClientError as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# Tool Registry
# ============================================================================

ERPNEXT_TOOLS = [
    get_doctypes,
    get_doctype_fields,
    get_document,
    get_documents,
    create_document,
    update_document,
    delete_document,
    run_report,
]

