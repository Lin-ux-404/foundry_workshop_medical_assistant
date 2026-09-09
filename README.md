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
- `labs/` a three-day Foundry notebook workshop, with four
  Day 1 notebooks implemented. The application is not a prerequisite.

## What you build

Work through the notebooks in `labs/` to learn Foundry through small
independent examples. Each one runs from a fresh kernel and depends on nothing
before it.

| Notebook | You implement |
| --- | --- |
| `day_1/01_deploy_a_model.ipynb` | Deploy a model, complete a Responses call, move standing rules into `instructions` |
| `day_1/02_prompt_agents.ipynb` | Write an agent role, save two versions, build the `agent_reference` |
| `day_1/03_search_and_grounded_answers.ipynb` | Query AI Search, describe the index, write the grounding rule |
| `day_1/04_agent_framework_orchestration.ipynb` | Connect to a saved agent and order a sequential workflow |
| `day_2/05_knowledge_bases_and_foundry_iq.ipynb` | Reach a Foundry IQ knowledge base over MCP |

Labs 6 to 8 are empty placeholders. Guardrails, evaluation, fine-tuning and
tool calling are covered elsewhere.

The notebooks do not require medical datasets, shared helper packages, or changes
to the starter application. Application development remains a separate workstream.

## Prerequisites

- Python 3.11+ (the notebooks check this and stop on older kernels) and Node 18+
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
