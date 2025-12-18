# Agent Control Plane

A **control plane** service for agent orchestration using **FastAPI** and **LangGraph**.

> ⚠️ **Note**: This is a **control plane**, not business logic. It provides the infrastructure for agent execution, planning, and tool orchestration. Domain-specific logic and tools should be plugged in separately.

## Purpose

This service provides:

- **API Layer**: FastAPI endpoints for agent interaction
- **Agent Orchestration**: LangGraph-based state machine for planning and execution
- **Tool Interface**: Extensible tool system (stubs ready for implementation)
- **Configuration**: Centralized, environment-driven settings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                          │
│  POST /agent/run  │  GET /health                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Agent                           │
│  ┌─────────┐      ┌──────────┐      ┌─────────┐            │
│  │ Planner │ ───▶ │ Executor │ ───▶ │  Tools  │            │
│  └─────────┘      └──────────┘      └─────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
apps/agent/
├── pyproject.toml       # Python package configuration
├── README.md            # This file
├── app/
│   ├── main.py          # FastAPI application entry
│   ├── config.py        # Environment configuration
│   ├── api/
│   │   ├── __init__.py
│   │   └── agent.py     # Agent API endpoints
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py     # LangGraph state machine
│   │   ├── state.py     # Agent state definitions
│   │   ├── planner.py   # Planning node
│   │   └── executor.py  # Execution node
│   └── tools/
│       ├── __init__.py
│       └── example_tool.py  # Example tool stub
```

## Local Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

```bash
cd apps/agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Or with uv (faster)
uv pip install -e ".[dev]"
```

### Environment Variables

Create a `.env` file in the `apps/agent/` directory:

```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-api-key-here

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

### Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --port 8000

# Or directly
python -m uvicorn app.main:app --reload --port 8000
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Run agent
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, agent!"}'
```

## Extending the Control Plane

### Adding Tools

1. Create a new file in `app/tools/`
2. Define a LangChain-compatible tool using the `@tool` decorator
3. Register the tool in `app/tools/__init__.py`

### Adding Authentication

Authentication middleware can be added in `app/main.py`. This is intentionally left as a stub for your specific auth requirements.

### Adding Persistence

Agent state persistence can be added using LangGraph's checkpointing system. See the LangGraph documentation for details.

## Future Enhancements

- [ ] Streaming responses
- [ ] Agent state persistence
- [ ] Tool safety contracts
- [ ] Approval interrupts (human-in-the-loop)
- [ ] Multi-tenant session management
- [ ] Authentication & RBAC

## License

MIT

