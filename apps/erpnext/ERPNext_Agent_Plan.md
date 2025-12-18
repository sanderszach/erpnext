# Plan: Dynamic ERPNext API Tool Generation for AI Agent

## Overview
Create an AI agent that can dynamically discover and interact with ERPNext APIs by automatically generating tools from DocType definitions and whitelisted methods.

## Architecture

### 1. API Discovery Layer

#### 1.1 DocType Discovery
**Endpoint**: `GET /api/resource/DocType?fields=["name","module","custom"]&filters=[["istable","=",0]]`

**Purpose**: Discover all available DocTypes (data models) in ERPNext

**Implementation**:
- Query ERPNext to get list of all DocTypes
- Filter out system/internal DocTypes if needed
- For each DocType, fetch its schema/metadata

#### 1.2 DocType Schema Discovery
**Endpoint**: `GET /api/method/frappe.desk.form.load.getdoctype?doctype={DocType}`

**Alternative**: Use DocType JSON files directly from codebase:
- Pattern: `erpnext/{module}/doctype/{doctype_name}/{doctype_name}.json`
- Contains complete field definitions, permissions, validations

**Schema Information Needed**:
- Field names and types
- Required fields
- Field options (for Select/Link fields)
- Permissions (read/write/create/delete)
- Validations and constraints

#### 1.3 Whitelisted Method Discovery
**Challenge**: Frappe doesn't expose a built-in endpoint to list all whitelisted methods

**Solutions**:
1. **Codebase Scanning**: Parse Python files for `@frappe.whitelist()` decorators
   - Pattern: `**/*.py` files
   - Extract module path and function name
   - Example: `erpnext.accounts.doctype.currency_exchange_settings.currency_exchange_settings.get_api_endpoint`

2. **Runtime Discovery** (if possible):
   - Query Frappe's method registry (if exposed)
   - Use introspection APIs

3. **Documentation/Manifest**: Maintain a curated list of important methods

### 2. Tool Generation Layer

#### 2.1 DocType CRUD Tools

For each DocType, generate 4 standard tools:

**a) List/Query Tool**
```python
{
    "name": f"erpnext_list_{doctype_snake_case}",
    "description": f"List or query {doctype} records with filters, sorting, and pagination",
    "parameters": {
        "type": "object",
        "properties": {
            "filters": {
                "type": "array",
                "description": "Filter conditions in format [[field, operator, value], ...]",
                "items": {"type": "array"}
            },
            "fields": {
                "type": "array",
                "description": "Fields to return (default: all)",
                "items": {"type": "string"}
            },
            "limit_start": {"type": "integer", "default": 0},
            "limit_page_length": {"type": "integer", "default": 20},
            "order_by": {"type": "string"}
        }
    }
}
```

**b) Get Single Record Tool**
```python
{
    "name": f"erpnext_get_{doctype_snake_case}",
    "description": f"Get a single {doctype} record by name",
    "parameters": {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "description": "Document name/ID"},
            "fields": {"type": "array", "items": {"type": "string"}}
        }
    }
}
```

**c) Create Record Tool**
```python
{
    "name": f"erpnext_create_{doctype_snake_case}",
    "description": f"Create a new {doctype} record",
    "parameters": {
        "type": "object",
        "required": [/* required fields from schema */],
        "properties": {
            /* Generated from DocType field definitions */
        }
    }
}
```

**d) Update Record Tool**
```python
{
    "name": f"erpnext_update_{doctype_snake_case}",
    "description": f"Update an existing {doctype} record",
    "parameters": {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            /* All updatable fields from schema */
        }
    }
}
```

**e) Delete Record Tool** (optional, based on permissions)
```python
{
    "name": f"erpnext_delete_{doctype_snake_case}",
    "description": f"Delete a {doctype} record",
    "parameters": {
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {"type": "string"}
        }
    }
}
```

#### 2.2 Custom Method Tools

For each whitelisted method, generate a tool:

```python
{
    "name": f"erpnext_method_{module_path_snake_case}",
    "description": "Extracted from function docstring or inferred",
    "parameters": {
        "type": "object",
        "properties": {
            /* Generated from function signature using introspection */
        }
    }
}
```

**Challenge**: Python function signatures need to be introspected or documented.

**Solutions**:
1. Parse function signatures from source code
2. Use type hints if available
3. Maintain method documentation/OpenAPI spec
4. Use runtime introspection (if Frappe exposes this)

### 3. Field Type Mapping

Map ERPNext field types to JSON Schema types:

| ERPNext Field Type | JSON Schema Type | Notes |
|-------------------|------------------|-------|
| Data | string | Text field |
| Int | integer | |
| Float/Currency | number | |
| Date | string (format: date) | ISO 8601 |
| Datetime | string (format: date-time) | ISO 8601 |
| Time | string (format: time) | |
| Check | boolean | |
| Select | string (enum) | Use options array |
| Link | string | Reference to another DocType |
| Table | array | Child table records |
| Text Editor | string | HTML content |
| Attach | string | File URL/path |
| Image | string | Image URL/path |

### 4. Implementation Strategy

#### Phase 1: Static Discovery (Codebase-based)
1. **Scan DocType JSON files** in `erpnext/**/doctype/**/*.json`
2. **Parse field schemas** from JSON
3. **Scan for whitelisted methods** using regex/AST parsing
4. **Generate tool definitions** in JSON Schema format
5. **Cache results** for performance

#### Phase 2: Dynamic Discovery (Runtime-based)
1. **Query ERPNext API** at startup to discover DocTypes
2. **Fetch DocType metadata** via API
3. **Generate tools dynamically** from runtime data
4. **Refresh periodically** or on-demand

#### Phase 3: Hybrid Approach (Recommended)
1. **Initial load**: Use codebase scanning for comprehensive discovery
2. **Runtime validation**: Query API to verify DocTypes exist and get permissions
3. **Incremental updates**: Monitor for new DocTypes/methods

### 5. Agent Integration

#### 5.1 Tool Registry
Maintain a registry of generated tools:
```python
class ERPNextToolRegistry:
    def __init__(self, erpnext_url, api_key, api_secret):
        self.erpnext_url = erpnext_url
        self.auth = (api_key, api_secret)
        self.tools = {}
        self.discover()
    
    def discover(self):
        # Discover DocTypes and methods
        # Generate tools
        # Register in self.tools
    
    def get_tool(self, name):
        return self.tools.get(name)
    
    def execute_tool(self, tool_name, **kwargs):
        # Execute API call to ERPNext
        # Return result
```

#### 5.2 API Client
```python
class ERPNextAPIClient:
    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url.rstrip('/')
        self.auth = (api_key, api_secret)
    
    def request(self, method, endpoint, **kwargs):
        # Make authenticated request to ERPNext
        # Handle errors
        # Return JSON response
    
    def list_resource(self, doctype, **params):
        return self.request('GET', f'/api/resource/{doctype}', params=params)
    
    def get_resource(self, doctype, name, **params):
        return self.request('GET', f'/api/resource/{doctype}/{name}', params=params)
    
    def create_resource(self, doctype, data):
        return self.request('POST', f'/api/resource/{doctype}', json=data)
    
    def update_resource(self, doctype, name, data):
        return self.request('PUT', f'/api/resource/{doctype}/{name}', json=data)
    
    def delete_resource(self, doctype, name):
        return self.request('DELETE', f'/api/resource/{doctype}/{name}')
    
    def call_method(self, method_path, **kwargs):
        return self.request('GET', f'/api/method/{method_path}', params=kwargs)
```

#### 5.3 Agent Framework Integration

**For OpenAI Function Calling / Anthropic Tools:**
```python
def generate_openai_tools(registry):
    tools = []
    for tool_name, tool_def in registry.tools.items():
        tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_def["description"],
                "parameters": tool_def["parameters"]
            }
        })
    return tools
```

**For LangChain:**
```python
from langchain.tools import StructuredTool

def create_langchain_tools(registry, api_client):
    tools = []
    for tool_name, tool_def in registry.tools.items():
        tools.append(StructuredTool.from_function(
            func=lambda **kwargs: api_client.execute_tool(tool_name, **kwargs),
            name=tool_name,
            description=tool_def["description"],
            args_schema=create_pydantic_model(tool_def["parameters"])
        ))
    return tools
```

### 6. Example Implementation Structure

```
erpnext_agent/
├── __init__.py
├── discovery/
│   ├── __init__.py
│   ├── doctype_scanner.py      # Scan DocType JSON files
│   ├── method_scanner.py       # Scan for @frappe.whitelist()
│   └── schema_parser.py         # Parse DocType schemas
├── generator/
│   ├── __init__.py
│   ├── tool_generator.py       # Generate tool definitions
│   └── field_mapper.py          # Map field types
├── client/
│   ├── __init__.py
│   └── api_client.py            # ERPNext API client
├── registry/
│   ├── __init__.py
│   └── tool_registry.py         # Tool registry and execution
└── agent/
    ├── __init__.py
    └── erpnext_agent.py         # Main agent class
```

### 7. Key Considerations

#### 7.1 Authentication
- **API Key/Secret**: Generate in ERPNext (User → API Access)
- **Session-based**: Use login endpoint for session cookies
- **OAuth**: If ERPNext supports it

#### 7.2 Permissions
- Respect ERPNext user permissions
- Filter tools based on user's allowed DocTypes
- Handle permission errors gracefully

#### 7.3 Error Handling
- Network errors
- Authentication failures
- Validation errors from ERPNext
- Permission denied errors

#### 7.4 Performance
- Cache tool definitions
- Batch API calls when possible
- Use pagination for large lists
- Lazy-load tool definitions

#### 7.5 Field Relationships
- **Link fields**: Reference other DocTypes
- **Table fields**: Child records (array of objects)
- **Dynamic Links**: Polymorphic references
- Handle these in tool descriptions

### 8. Example Generated Tool

**Input**: Customer DocType schema

**Output**:
```json
{
  "name": "erpnext_create_customer",
  "description": "Create a new Customer record in ERPNext",
  "parameters": {
    "type": "object",
    "required": ["customer_name"],
    "properties": {
      "customer_name": {
        "type": "string",
        "description": "Full name of the customer"
      },
      "customer_type": {
        "type": "string",
        "enum": ["Company", "Individual"],
        "description": "Type of customer"
      },
      "customer_group": {
        "type": "string",
        "description": "Customer Group (Link to Customer Group DocType)"
      },
      "territory": {
        "type": "string",
        "description": "Territory (Link to Territory DocType)"
      },
      "email_id": {
        "type": "string",
        "format": "email",
        "description": "Primary email address"
      },
      "mobile_no": {
        "type": "string",
        "description": "Mobile phone number"
      }
    }
  }
}
```

### 9. Next Steps

1. **Proof of Concept**: 
   - Implement DocType scanner for Customer
   - Generate basic CRUD tools
   - Test with simple agent

2. **Expand Discovery**:
   - Add all DocTypes
   - Add method discovery
   - Handle edge cases

3. **Agent Integration**:
   - Choose agent framework (OpenAI, Anthropic, LangChain, etc.)
   - Implement tool execution
   - Add error handling

4. **Testing**:
   - Unit tests for discovery
   - Integration tests with ERPNext
   - Agent behavior tests

5. **Documentation**:
   - API documentation
   - Usage examples
   - Troubleshooting guide

## Resources

- ERPNext REST API Docs: `/api/resource/{DocType}`
- Frappe Framework Docs: https://frappeframework.com/docs
- DocType JSON Schema: See `erpnext/**/doctype/**/*.json` files
- API Authentication: User → API Access → Generate Keys

