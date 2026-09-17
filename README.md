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
                     Runs the agent on Microsoft Foundry and exposes /api/chat and /api/health.
  frontend/          Vite + React + TypeScript chat UI (src/)
                     Calls the backend's /api/chat endpoint.
labs/
  day_1/ day_2/ day_3/   Foundry notebooks, one per topic (see below).
  extras/                Optional standalone labs outside the core 3-day path.
  data/                  Datasets used by the labs (WHO guidelines, hospital IPC data).
scripts/
  setup/             Provisions the Azure environment (Search, Storage, Foundry) and the knowledge base the labs query.
```

## Labs

Work through the notebooks in `labs/` to learn Foundry through independent
examples. Each runs from a fresh kernel. Lab 3 introduces the knowledge base
reused by the later grounded-agent and live RAG labs.

Use the table-based [workshop glossary](GLOSSARY.md) to look up terms as you go.

| Notebook | Topic |
| --- | --- |
| `day_1/01_deploy_a_model.ipynb` | Deploy a model, call the Responses API |
| `day_1/02_prompt_agents.ipynb` | Save an agent, version its instructions |
| `day_1/03_knowledge_bases_and_foundry_iq.ipynb` | Ground an agent in a Foundry IQ knowledge base |
| `day_1/04_tools.ipynb` | Function tools, tool-call round trip, approvals |
| `day_1/05_tool_call_regression.ipynb` | Exact and semantic tool-call regression testing |
| `day_2/06_agent_framework_orchestration.ipynb` | Orchestrate a sequential multi-agent workflow |
| `day_2/07_orchestration_sequential.ipynb` | Sequential orchestration pattern with `SequentialBuilder` |
| `day_2/08_orchestration_concurrent.ipynb` | Concurrent orchestration pattern with `ConcurrentBuilder` |
| `day_2/09_orchestration_magentic.ipynb` | Magentic orchestration pattern with `MagenticBuilder` |
| `day_2/10_guardrails.ipynb` | Create an account guardrail, assign it to an agent, test and clean up |
| `day_3/11_evaluations_in_foundry.ipynb` | OpenTelemetry tracing and privacy-safe observability |
| `day_3/12_grounded_answer_evaluation.ipynb` | Retrieval, groundedness and relevance evaluation |
| `day_3/13_agent_trajectory_evaluation.ipynb` | System and process evaluation of function-tool trajectories |
| `day_3/14_end_to_end_search_rag_evaluation.ipynb` | Live Azure AI Search RAG evaluation |
| `day_3/15_end_to_end_foundry_iq_evaluation.ipynb` | Repeated live Foundry IQ RAG evaluation |
| `extras/01_red_team_security_testing.ipynb` | Local policy-abuse tests and optional cloud red teaming (optional, outside the core path) |

Labs 3, 4, 6, 11, 14 and 15 use a knowledge base built from three published WHO
clinical guidelines. Labs 4, 5 and 13 use synthetic hospital IPC data or its
tool contracts. Labs 14 and 15 share a versioned evaluation benchmark and
deterministic helper module. `scripts/setup/` builds the knowledge base
and is safe to rerun - see
[`scripts/setup/README.md`](scripts/setup/README.md).

Follow the Day 3 notebooks in the order above for the evaluation learning
path. Each notebook describes its expected artifacts, preview fallbacks
and additional permissions.

## Prerequisites

- Python 3.11+ and Node 18+
- An Azure AI Foundry project with a deployed `gpt-5.4-mini` chat model
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
