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
- `labs/` a three-day Foundry notebook workshop, with the four
  Day 1 notebooks implemented. The application is not a prerequisite.

## What you build

Work through the notebooks in `labs/` to learn Foundry through small
independent examples. Each one runs from a fresh kernel. Labs 3 and 4 share the
same knowledge base, so run Lab 3 first if you want Lab 4's retrieval to make
sense.

| Notebook | You implement |
| --- | --- |
| `day_1/01_deploy_a_model.ipynb` | Deploy a model, complete a Responses call, move standing rules into `instructions` |
| `day_1/02_prompt_agents.ipynb` | Write an agent role, save two versions, build the `agent_reference` |
| `day_1/03_knowledge_bases_and_foundry_iq.ipynb` | Query a Foundry IQ knowledge base and ground an agent in it over MCP |
| `day_1/04_agent_framework_orchestration.ipynb` | Connect to a saved agent and order a sequential workflow |

Day 1 builds a grounded clinical assistant end to end: deploy a model, save it
as an agent, ground it in real WHO guidelines, then coordinate two agents over
that knowledge. Day 2 turns it into something you would run in production, and
Day 3 is hands-on with the application.

| Placeholder | Planned content |
| --- | --- |
| `day_2/05_guardrails.ipynb` | Guardrails |
| `day_2/06_tools.ipynb` | Tools, including function tools and MCP servers beyond the knowledge base |
| `day_2/07_evaluations_in_foundry.ipynb` | Evaluations in Foundry |
| `day_3/README.md` | Application guide for `backend/` and `frontend/` |

Labs 3 and 4 read from a knowledge base built from three published WHO clinical
guidelines. `scripts/medical_kb/` provisions it and is safe to rerun; see
[`scripts/medical_kb/README.md`](scripts/medical_kb/README.md). The notebooks need
no shared helper packages and no changes to the starter application, which remains
a separate workstream.

## Prerequisites

- Python 3.11+ (the notebooks check this and stop on older kernels) and Node 18+
- An Azure AI Foundry project with a deployed chat model (the labs assume `gpt-5.6-luna`)
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
