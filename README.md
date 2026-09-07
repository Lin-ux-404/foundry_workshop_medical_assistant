# Agentic Medical Operations Assistant

Starter repo for the three-day hackathon. It gives you a working end-to-end
slice: a React chat frontend talking to a FastAPI backend that runs an agent on
**Microsoft Foundry** through the **Microsoft Agent Framework** (`agent_framework.ChatAgent`),
including a **structured-output** example. Everything else in the brief is yours to build.

> Educational demo only. It does not diagnose, does not replace a healthcare
> professional, and uses synthetic data throughout.

## What is already built

- `backend/` FastAPI app with a clean, swappable structure:
  - a single place that constructs the Foundry client (`clients/foundry_client.py`),
  - a Patient Assistant and a Triage Agent, one file per agent under `agents/`,
  - `POST /api/chat` free-text reply, `POST /api/triage` structured `TriageResult`, `GET /api/health`,
  - Pydantic request/response and structured-output models (`schemas.py`),
  - config via environment variables (`config.py`).
- `frontend/` Vite + React + TypeScript chat UI that calls `/api/chat`.
- `labs/` per-day lab stubs. `notebooks` for guided exercises can live here too.

## What you build

Use the hackathon brief. In short:

- **Day 1** give agents real tools (availability + booking), persist to SQLite, show appointments to an admin.
- **Day 2** ground answers with **Foundry IQ** + Azure AI Search; add a Medical Knowledge Agent with citations.
- **Day 3** add **workflows** (Patient Intake, Appointment Booking, Priority Scheduling) and split into specialized agents.

Suggested folders to add as you go: `agents/`, `workflows/`, `knowledge/`, `data/`,
`models/`, `tests/` (see the brief's repository structure).

## Prerequisites

- Python 3.10+ and Node 18+
- An Azure AI Foundry project with a deployed chat model (e.g. `gpt-4o-mini`)
- Azure CLI: run `az login` (the backend uses `DefaultAzureCredential`, no API keys)

## Run the backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt      # if agent-framework is not found: pip install --pre agent-framework
cp .env.example .env                  # then fill in your Foundry endpoint + model
uvicorn main:app --reload             # http://localhost:8000  (docs at /docs)
```

Fill `.env`:

```
AZURE_AI_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

Quick check:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I have had a fever for two days. Should I be worried?"}'
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev                           # http://localhost:3000
```

The dev server proxies `/api` to `http://localhost:8000/docs`, so run the backend first.

## How the agent + structured output works

Each file in `agents/` builds a `ChatAgent` from the Foundry client and holds that agent's
instructions. `POST /api/triage` asks the Triage Agent to return the `TriageResult`
schema (`response_format=TriageResult`) and reads the parsed object from
`result.value`, with a text-JSON fallback. This is the pattern to reuse for every
structured step later (intake, priority rules, admin analytics).

To use a different client (for example `AzureOpenAIChatClient` if you want the most
reliable structured outputs), change only `clients/foundry_client.py`. The agents and routes
stay the same.

## Repository layout

```
backend/
  main.py            FastAPI app + lifespan (creates the Foundry client once)
  config.py          env-based settings
  clients/           foundry_client.py - the ONE place the client is built (swappable)
  agents/            one file per agent: patient_assistant.py, triage_agent.py
  schemas.py         Pydantic API models + TriageResult (structured output)
  routers/           chat.py (patient endpoints), health.py
  requirements.txt
  .env.example
frontend/
  src/               main.tsx, App.tsx, api.ts, components/Chat.tsx, styles.css
  vite.config.ts     dev proxy to the backend
labs/
  day_1/ day_2/ day_3/
```

## Responsible AI

Keep the disclaimer visible, keep data synthetic, escalate on severe/ambiguous
symptoms, ground informational answers (Day 2), and give agents purpose-built
tools rather than unrestricted database access.
