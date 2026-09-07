# Backend

FastAPI + Microsoft Agent Framework (`agent_framework.ChatAgent`) on Microsoft Foundry.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt                     # or: pip install --pre agent-framework
cp .env.example .env                                 # fill in AZURE_AI_* values
az login
uvicorn main:app --reload
```

## Endpoints

- `GET  /api/health`  liveness check
- `POST /api/chat`    `{ "message": "..." }` -> `{ "reply": "..." }`
- `POST /api/triage`  `{ "message": "..." }` -> structured `TriageResult`

Interactive docs: http://localhost:8000/docs

## Where to add things

- New agents -> a new file in `agents/` (prompt + builder), re-export it in `agents/__init__.py`
- New tools -> register on the agent via `create_agent(..., tools=[...])`
- New endpoints -> a new module in `routers/`, then `include_router` in `main.py`
- Data access (SQLite/Parquet) -> add a `data/` or `db.py` layer and call it from tools
- Swap the model client -> `clients/foundry_client.py` only
