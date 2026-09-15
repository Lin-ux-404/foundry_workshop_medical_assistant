# Agentic Medical Operations Assistant

A three-day Microsoft Foundry workshop repo, plus a working end-to-end
reference app: a React chat frontend talking to a FastAPI backend that runs
an agent on **Microsoft Foundry** via the **Microsoft Agent Framework**.

> Educational demo only. It does not diagnose, does not replace a healthcare
> professional, and uses synthetic data throughout.

## Repository layout

```text
app/
  backend/           FastAPI app (main.py, config.py, clients/, agents/, routers/, schemas.py)
                     Runs the agent(s) on Microsoft Foundry and exposes /api/chat, /api/triage, /api/health.
  frontend/          Vite + React + TypeScript chat UI (src/)
                     Calls the backend's /api/chat endpoint.
labs/
  day_1/ day_2/ day_3/   Foundry notebooks, one per topic (see below).
  data/                  Datasets used by the labs (WHO guidelines, hospital IPC data).
scripts/
  setup/             Provisions the Azure environment (Search, Storage, Foundry) and the knowledge base the labs query.
```

## Labs

Work through the notebooks in `labs/` to learn Foundry through independent
examples. Each runs from a fresh kernel. Lab 3 introduces the knowledge base
reused by the later grounded-agent and live RAG labs.

| Notebook | Topic |
| --- | --- |
| `day_1/01_deploy_a_model.ipynb` | Deploy a model, call the Responses API |
| `day_1/02_prompt_agents.ipynb` | Save an agent, version its instructions |
| `day_1/03_knowledge_bases_and_foundry_iq.ipynb` | Ground an agent in a Foundry IQ knowledge base |
| `day_1/04_agent_framework_orchestration.ipynb` | Orchestrate a sequential multi-agent workflow |
| `day_2/05_guardrails.ipynb` | Create an account guardrail, assign it to an agent, test and clean up |
| `day_2/06_tools.ipynb` | Function tools, tool-call round trip, approvals |
| `day_2/07_evaluations_in_foundry.ipynb` | OpenTelemetry tracing and privacy-safe observability |
| `day_2/08_grounded_answer_evaluation.ipynb` | Retrieval, groundedness and relevance evaluation |
| `day_2/09_agent_trajectory_evaluation.ipynb` | System and process evaluation of function-tool trajectories |
| `day_2/10_tool_call_regression.ipynb` | Exact and semantic tool-call regression testing |
| `day_2/11_red_team_security_testing.ipynb` | Local policy-abuse tests and optional cloud red teaming |
| `day_2/12_end_to_end_search_rag_evaluation.ipynb` | Live Azure AI Search RAG evaluation |
| `day_2/13_end_to_end_foundry_iq_evaluation.ipynb` | Repeated live Foundry IQ RAG evaluation |
| `day_3/README.md` | Application guide for `app/backend/` and `app/frontend/` |

Labs 3, 4, 6, 7, 12 and 13 use a knowledge base built from three published WHO
clinical guidelines. Labs 6, 9 and 10 use synthetic hospital IPC data or its
tool contracts. Labs 12 and 13 share a versioned evaluation benchmark and
deterministic helper module. `scripts/setup/` builds the knowledge base
and is safe to rerun - see
[`scripts/setup/README.md`](scripts/setup/README.md).

Follow the Day 2 notebooks in the order above for the evaluation learning
path. Each notebook describes its expected artifacts, preview fallbacks
and additional permissions.

## Prerequisites

- Python 3.11+ and Node 18+
- An Azure AI Foundry project with a deployed chat model (the current workshop uses `gpt-5.6-terra`)
- Azure CLI: run `az login` (the backend uses `DefaultAzureCredential`, no API keys)

## Run the backend

```bash
cd app/backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt      # if agent-framework is not found: pip install --pre agent-framework
cp .env.example .env                  # then fill in your Foundry endpoint + model
uvicorn main:app --reload             # http://localhost:8000  (docs at /docs)
```

Quick check:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I have had a fever for two days. Should I be worried?"}'
```

## Run the frontend

```bash
cd app/frontend
npm install
npm run dev                           # http://localhost:3000
```

The dev server proxies `/api` to `http://localhost:8000`, so run the backend first.

## Responsible AI

Keep the disclaimer visible, keep data synthetic, escalate on severe/ambiguous
symptoms, ground informational answers, and give agents purpose-built tools
rather than unrestricted database access.
