# Day 2 - Knowledge

**Goal:** Give an agent reusable knowledge through Foundry IQ.

| Notebook | Topics | What you implement |
| --- | --- | --- |
| [Lab 5 - Knowledge bases and Foundry IQ](05_knowledge_bases_and_foundry_iq.ipynb) | Knowledge sources, knowledge bases, agentic retrieval, MCP tools, project connections | Build the `MCPTool` that reaches the knowledge base, write the retrieval rules, then point a second agent at the same knowledge base. |
| `06_guardrails.ipynb` | Guardrails | Placeholder. Content is owned elsewhere. |

Allow roughly 45 to 60 minutes for Lab 5.

## Start here

Same rhythm as Day 1: read the concept, predict the outcome, fill the `...`
blanks marked `# TODO`, run the cell, then read what came back. A
**Deterministic success check** at the end prints `PASS - ...` once you have
built the right thing.

Run `az login` before you start, and set `AZURE_AI_PROJECT_ENDPOINT` and
`AZURE_AI_MODEL_DEPLOYMENT_NAME` in the notebook or your environment. Never
paste a credential into a cell.

## Prerequisites

Lab 5 needs the Foundry project and model deployment from Day 1, plus
permission to author agents. You do not need any output or saved agent from a
Day 1 notebook: the lab creates what it uses.

Lab 5 also needs an Azure AI Search service with a knowledge base, and a
project connection that lets the agent call it. The knowledge base is built
with `azure-search-documents`, not `azure-ai-projects`, and the connection is
created in the portal or with an ARM call. Both steps are written out in a
collapsible section in the notebook, along with `AZURE_SEARCH_ENDPOINT`,
`AZURE_KNOWLEDGE_BASE_NAME` and `AZURE_PROJECT_CONNECTION_ID`.

**Explain it back:** Where does a knowledge base live, and why is that not the
agent? What has to exist before an agent can call one?

[Full curriculum](../../docs/notebook-workshop-plan.md) | [All days](../README.md)
