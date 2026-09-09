# Day 1 - Foundry foundations

**Goal:** Deploy a model, turn it into a versioned agent, ground it in real
documents, and coordinate two agents from your own code.

Four notebooks. Each one carries its own setup, example data, code blanks,
hints and solutions.

| Notebook | Topics | What you implement |
| --- | --- | --- |
| [Lab 1 - Deploy a model](01_deploy_a_model.ipynb) | Model versus deployment, deployment versus training, the Responses API | Deploy an approved model, complete the request, then split the standing rules out of the question into `instructions`. |
| [Lab 2 - Deploy a prompt agent](02_prompt_agents.ipynb) | Named and versioned agents, agent references, conversations | Write the agent's role, build the `agent_reference`, then save a second version and prove the first did not change. |
| [Lab 3 - Ground an agent in AI Search](03_search_and_grounded_answers.ipynb) | Index fields, chunks, retrieval, tools, grounding, citations | Define the index schema, run a Search query, describe the index the agent should search, and write the grounding rule it must follow. |
| [Lab 4 - Coordinate agents](04_agent_framework_orchestration.ipynb) | Remote agents versus local orchestration, sequential workflows | Write two distinct roles, connect to a saved version, then set the workflow's participant order and output selection. |

Allow roughly 45 to 55 minutes per notebook, plus breaks and discussion. Custom
function tools, Foundry IQ, guardrails, evaluation and app building belong to
later days.

## Start here

Use Python 3.11 or later with a dedicated notebook environment and a Jupyter or
VS Code kernel. Run `az login` in a terminal with the account that owns your subscription. Open a
notebook and work down its cells with **Shift+Enter**. Each notebook installs
its own packages; restart the kernel if you changed packages after importing.

Every lesson follows the same rhythm:

1. **What will you do** and **New words** set up the vocabulary before you meet it in code.
2. Each section explains the concept, compares the options in a table, and tells you what output to expect.
3. A **To-Do** states a goal and steps, then leaves `...` blanks in the next code cell marked with `# TODO`.
4. A **Deterministic success check** at the end proves what you built, printing `PASS - ...`.
5. **What you learned** recaps the ideas and asks two or three reflection questions.

Replace each `...` with a value, not a description of one. Use a variable name
without quotes when you want its value; use quotes when you are writing text.
If you leave a blank open, the cell stops and names it rather than sending a
placeholder to Azure. Try the task before opening **Hint**, then use **Show
solution code** if you are still stuck.

Fill the nonsecret settings inside the notebook, or supply
`AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` as environment
variables. No `.env` file or repository configuration loader is required.
Never paste a credential into a cell or leave one in an output.

Lab 1's portal steps are the part that actually teaches deployment; its Python
cells call the deployment you just made. Labs 2, 3 and 4 create prompt agents
when you run their creation cells, and running a creation cell again adds a
version rather than replacing one. Lab 3 deletes the index it created; agents
are small and stay in your project until you remove them from the portal.

## Prerequisites

You need an Azure subscription with a Foundry project, permission to deploy a
model that supports the Responses API, and permission to author agents. Lab 1
walks you through the deployment itself.

Lab 3 also needs an Azure AI Search service and its
`AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX_NAME` and
`AZURE_SEARCH_CONNECTION_NAME` settings, the last being the connection name
inside the Foundry project. You build the index in the notebook from three
short documents defined there, so you need **Search Service Contributor** and
**Search Index Data Contributor** on the service. Core retrieval uses keyword
search; the hybrid comparison is an optional extension needing a vector field
and an integrated vectorizer.

Lab 4 needs no Search resource. It passes its own source notes through two
distinct Foundry agents. Its install cell pins the compatible SDK versions.

See the [workshop overview](../README.md) and the
[notebook workshop plan](../../docs/notebook-workshop-plan.md).
