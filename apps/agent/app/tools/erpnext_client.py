"""
ERPNext API client for interacting with ERPNext/Frappe.

This module provides an async HTTP client for the ERPNext REST API.
"""

import json
from typing import Any

import httpx

from app.config import settings


class ERPNextClientError(Exception):
    """Exception raised when ERPNext API calls fail."""

    pass


class ERPNextClient:
    """
    Async client for interacting with ERPNext REST API.

    Provides methods for:
    - Fetching documents
    - Listing documents with filters
    - Creating documents
    - Updating documents
    - Running reports
    - Getting DocType metadata
    """

    def __init__(self) -> None:
        """Initialize the ERPNext client with configuration from settings."""
        self.base_url = settings.erpnext_url
        self.api_key = settings.erpnext_api_key
        self.api_secret = settings.erpnext_api_secret

        if not self.base_url:
            raise ERPNextClientError("ERPNEXT_URL is not configured")

        # Remove trailing slash
        self.base_url = self.base_url.rstrip("/")

        # Build headers
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key and self.api_secret:
            self.headers["Authorization"] = f"token {self.api_key}:{self.api_secret}"

    def is_authenticated(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key and self.api_secret)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        """
        Make an async HTTP request to ERPNext.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: JSON body data.

        Returns:
            The parsed JSON response data.

        Raises:
            ERPNextClientError: If the request fails.
        """
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = ""
                try:
                    error_body = e.response.json()
                    error_detail = error_body.get("message", str(error_body))
                except Exception:
                    error_detail = e.response.text[:500]
                raise ERPNextClientError(
                    f"HTTP {e.response.status_code}: {error_detail}"
                ) from e
            except httpx.RequestError as e:
                raise ERPNextClientError(f"Request failed: {str(e)}") from e

    async def get_document(self, doctype: str, name: str) -> dict[str, Any]:
        """
        Get a document by doctype and name.

        Args:
            doctype: The ERPNext DocType (e.g., "Customer", "Item").
            name: The document name/ID.

        Returns:
            The document data.
        """
        response = await self._request("GET", f"/api/resource/{doctype}/{name}")
        return response.get("data", {})

    async def get_documents(
        self,
        doctype: str,
        filters: dict[str, Any] | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get a list of documents for a doctype.

        Args:
            doctype: The ERPNext DocType.
            filters: Filter conditions as {field: value}.
            fields: List of fields to include in response.
            limit: Maximum number of documents to return.
            order_by: Field to order by (e.g., "creation desc").

        Returns:
            List of matching documents.
        """
        params: dict[str, Any] = {}

        if fields:
            params["fields"] = json.dumps(fields)
        if filters:
            params["filters"] = json.dumps(filters)
        if limit:
            params["limit_page_length"] = limit
        if order_by:
            params["order_by"] = order_by

        response = await self._request("GET", f"/api/resource/{doctype}", params=params)
        return response.get("data", [])

    async def create_document(
        self, doctype: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a new document.

        Args:
            doctype: The ERPNext DocType.
            data: The document data.

        Returns:
            The created document.
        """
        response = await self._request(
            "POST",
            f"/api/resource/{doctype}",
            json_data={"data": data},
        )
        return response.get("data", {})

    async def update_document(
        self, doctype: str, name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update an existing document.

        Args:
            doctype: The ERPNext DocType.
            name: The document name/ID.
            data: The fields to update.

        Returns:
            The updated document.
        """
        response = await self._request(
            "PUT",
            f"/api/resource/{doctype}/{name}",
            json_data={"data": data},
        )
        return response.get("data", {})

    async def delete_document(self, doctype: str, name: str) -> dict[str, Any]:
        """
        Delete a document.

        Args:
            doctype: The ERPNext DocType.
            name: The document name/ID.

        Returns:
            The deletion response.
        """
        response = await self._request("DELETE", f"/api/resource/{doctype}/{name}")
        return response

    async def run_report(
        self, report_name: str, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Run an ERPNext report.

        Args:
            report_name: Name of the report.
            filters: Report filters.

        Returns:
            The report results.
        """
        params: dict[str, Any] = {"report_name": report_name}
        if filters:
            params["filters"] = json.dumps(filters)

        response = await self._request(
            "GET",
            "/api/method/frappe.desk.query_report.run",
            params=params,
        )
        return response.get("message", {})

    async def get_all_doctypes(self) -> list[str]:
        """
        Get all available DocTypes.

        Returns:
            List of DocType names.
        """
        try:
            response = await self._request(
                "GET",
                "/api/resource/DocType",
                params={
                    "fields": json.dumps(["name"]),
                    "limit_page_length": 500,
                },
            )
            data = response.get("data", [])
            return [item["name"] for item in data]
        except ERPNextClientError:
            # Fallback to common doctypes if API call fails
            return [
                "Customer",
                "Supplier",
                "Item",
                "Sales Order",
                "Purchase Order",
                "Sales Invoice",
                "Purchase Invoice",
                "Employee",
                "Lead",
                "Opportunity",
                "Quotation",
                "Payment Entry",
                "Journal Entry",
                "Stock Entry",
            ]

    async def get_doctype_fields(self, doctype: str) -> list[dict[str, Any]]:
        """
        Get field definitions for a DocType.

        Args:
            doctype: The DocType name.

        Returns:
            List of field definitions.
        """
        try:
            # Get the DocType document which contains field definitions
            response = await self._request("GET", f"/api/resource/DocType/{doctype}")
            doc = response.get("data", {})
            fields = doc.get("fields", [])

            # Extract relevant field info
            return [
                {
                    "fieldname": f.get("fieldname"),
                    "fieldtype": f.get("fieldtype"),
                    "label": f.get("label"),
                    "reqd": f.get("reqd", 0),
                    "options": f.get("options"),
                }
                for f in fields
                if f.get("fieldname")
            ]
        except ERPNextClientError:
            # Fallback: get fields from a sample document
            documents = await self.get_documents(doctype, fields=["*"], limit=1)
            if documents:
                return [
                    {"fieldname": key, "fieldtype": "unknown", "sample": str(val)[:50]}
                    for key, val in documents[0].items()
                ]
            return []


# Singleton client instance
_client: ERPNextClient | None = None


def get_erpnext_client() -> ERPNextClient:
    """
    Get the ERPNext client singleton.

    Returns:
        The ERPNext client instance.

    Raises:
        ERPNextClientError: If ERPNext is not configured.
    """
    global _client
    if _client is None:
        _client = ERPNextClient()
    return _client

