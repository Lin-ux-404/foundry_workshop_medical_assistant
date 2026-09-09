# Microsoft Foundry: three-day notebook workshop

**Status:** Day 1 implemented as four notebooks; Days 2 and 3 remain planned.
**Audience:** Beginners; no application-development or machine-learning background required.
**Goal:** Understand Foundry's main capabilities by running small, independent examples.

This is a technology workshop, not a medical application project. The existing
medical-assistant app can be one Day 3 demonstration, but its backend, datasets,
tools, and infrastructure plan are not prerequisites for the notebooks.

## 1. Keep the workshop simple

Each notebook teaches one main idea: **understand the concept -> predict ->
complete the implementation -> observe -> explain**.

Use a small, fictional **internal HTTP service** as the running example: an
orders API with a rate limit, token expiry, status codes, and a short incident
runbook. Keep examples technical. Do not dress a lesson up as event logistics,
office trivia, or any other non-technical scenario -- the reader is here to
learn Foundry, and a contrived setting adds reading for no teaching value.
Put the few example records or document strings directly in the relevant
notebook. There is no mandatory domain, real dataset, document-licensing
exercise, or application to build.

### Write for one reader with their own subscription

Address a single reader who owns the subscription and does the work themselves.
They create their own project, deploy their own model, build their own index,
and clean up after themselves. Do not write around a classroom: no instructor,
facilitator, or organizer supplies values; no resource is described as shared;
no step is deferred to somebody else's setup. Where a resource must exist
before the notebook runs, show how to create it in a collapsible section.

Do not warn the reader about spending, budget, or shared quota. State a cost or
latency trade-off only where it is genuine engineering guidance, such as the
effect of `top_k` on retrieval.

Give participants small implementation tasks, not only finished code to run.
After a short explanation, ask them to complete meaningful SDK settings, agent
instructions, tool attachments, or workflow steps. Keep authentication and
error-handling code supplied. Keep SDK calls visible and short rather than
hiding them behind workshop helpers. Small helper functions belong in the
notebook that uses them. Repeating a little setup is intentional.

### Write clear, learner-directed instructions

Follow the Microsoft Writing Style Guide's guidance on
[simple, human language](https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human),
[active verbs](https://learn.microsoft.com/en-us/style-guide/grammar/verbs), and
[step-by-step instructions](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions).
Address the learner as "you." Start task steps with verbs such as **select**,
**complete**, **connect**, and **compare**. Explain terms before using them,
keep each step focused on one action, and give errors a practical next step.
Use original instructional text, not copied Learn articles. Write without emoji.

### Teach the concept before asking for the code

A To-Do is only worth setting when a learner cannot complete it without
understanding something. Never leave a blank for a label, a free-text answer
that no code reads, or a value the notebook could supply itself. Every blank
should name a real parameter, instruction, or object that changes what Azure
does.

Introduce each idea before its exercise, and prefer scannable devices over long
prose:

- A short **New words** glossary near the top, with bolded terms and one-line definitions.
- A `text`-fenced flow diagram instead of an image.
- A **Microsoft Learn diagram**, embedded by its `learn.microsoft.com` URL, where a real one exists. Add an italic caption naming the source article and linking to it. Never copy the image file into this repository, and never invent a URL — verify it returns an image before using it.
- A **table** whenever you compare options, list parameters, or map a choice to its consequence. A "what this parameter does and what breaks if you get it wrong" table teaches faster than a paragraph.
- One short "Think of it as ..." analogy per notebook, not one per section.
- A **Predict:** question before a cell, answered later in a collapsible block.

Precede each code cell with a **Run the cell. You should see** contract that
states the expected output and names the likely failure with its fix.

### Keep code cells clean

Code cells should show the SDK call being taught and little else. Do not
scatter type checks, range checks, or per-blank `raise` statements through them.

Define one `check_todos(**answers)` helper in the setup cell, documented as a
workshop helper rather than part of the exercise. Each exercise cell then calls
it on a single line, so an unfilled `...` stops with a readable message instead
of reaching Azure. The setup cell may also raise once, with remediation text,
when a required setting is missing.

Put verification at the end instead, in a **Deterministic success check** cell.
Model wording is nondeterministic, so assert structure rather than phrasing:
request status, presence of citations, participant order, version identity.
Give every assertion a message that diagnoses the problem, and finish with
`print("PASS - ...")` naming what was proved.

### Exercise conventions

Mark exercises with `### To-Do n` headings, stating a **Goal:** and numbered
**Steps**. In code, write the blank as `...` with a `# TODO n:` comment naming
what the value must be. Give a conceptual `<details>` **Hint** first and a
collapsible **Show solution code** second.

Close each notebook with a **What you learned** recap, two or three reflection
questions with a collapsible comparison, and an **Expected artifact:** line.

## 2. Three-day agenda

| Day | Topics | What participants can explain afterward |
| --- | --- | --- |
| **1: Build the foundations** | Models and deployment; prompt agents; Azure AI Search and RAG; Microsoft Agent Framework and multi-agent orchestration. | How a model, an agent, retrieval, and an agent workflow differ. |
| **2: Add knowledge and controls** | Foundry IQ; reusable knowledge bases; MCP tool connections; guardrails and content controls. | How agents use knowledge and where controls can act. |
| **3: Compare and explore** | Evaluations; answer quality; latency and token usage; tool calling; fine-tuning; hands-on app exploration. | How to compare alternatives and decide what to improve. |

Plan around a short explanation and demonstration followed by hands-on work.
Reserve discussion and break time. Day 1 has the most topics: keep its examples
small instead of adding infrastructure, ingestion pipelines, or application work.

## 3. Day 1: models, agents, retrieval, and orchestration

**Outcome:** Run a model, register an agent, ground an answer, and coordinate two agents.

| Notebook | Main topics | Small hands-on activity | Visible result |
| --- | --- | --- | --- |
| `01_deploy_a_model.ipynb` | Model versus deployment; deployment versus training; `instructions` versus `input`. | Deploy an approved model in the portal, complete a Responses call, then move the standing rules out of the question and into `instructions`. | Two answers from one deployment, with token usage. |
| `02_prompt_agents.ipynb` | Named, versioned Foundry prompt agents; agent references; conversations; version immutability. | Write the agent's role and save version 1, build the `agent_reference`, then save version 2 and prove version 1 is unchanged. | One agent, two versions, and a conversation follow-up. |
| `03_search_and_grounded_answers.ipynb` | Index fields and analyzers, chunks, keyword/vector/hybrid retrieval, tools, grounding, citations. | Define the index schema, run a direct Search query, describe the index in `AISearchIndexResource`, and write the grounding rule the agent must follow. | A baseline answer, retrieved passages, a cited grounded answer, and an honest gap answer. |
| `04_agent_framework_orchestration.ipynb` | Remote agents versus local orchestration; sequential workflows; participants, outputs, and events. | Write two distinct roles, connect to a saved version with `FoundryAgent`, then set the workflow's participant order and output selection. | Workflow events in order plus both participants' output. |

Orientation is folded into notebook 01 rather than a separate notebook.
Day 1 stays focused on these four topics: no additional custom-function,
evaluation, app-building, or data-engineering lesson.

Notebook 02 uses a few fictional facts directly in its instructions. No function
schemas or callback loop are needed to teach agent deployment and versioning.

Notebook 03 creates its own index from three short reference documents defined
in the notebook, so the reader sees field design and indexing rather than
inheriting a prepared resource. Explain **document -> index -> retrieval ->
answer**. Label a direct Search query separately from an agent's retrieval
activity, and call out that the reader's identity and the project connection's
identity are different.

Notebook 04 runs an actual Microsoft Agent Framework workflow with two distinct
remote prompt agents. It includes its own agent setup and input documents; it
does not load agents, answers, or checkpoints from notebooks 02 or 03.
Pass source references along when the example uses sources. More agents are not
automatically better.

## 4. Day 2: Foundry IQ and guardrails

**Outcome:** Connect agents to reusable knowledge and observe simple controls.

| Notebook | Main topics | Small hands-on activity | Visible result |
| --- | --- | --- | --- |
| `05_knowledge_bases_and_foundry_iq.ipynb` | Foundry IQ; knowledge sources and knowledge bases; MCP; agent tool choice versus retrieval planning. | Connect an agent to a knowledge base holding two small sources. Ask a single-source, a combined, and an unknown-answer question. | The selected tool, returned source references, and an honest unknown answer. |
| `06_guardrails.ipynb` | Instructions versus enforced controls; Foundry content controls; retrieved-content boundaries; local tool validation. | Predict and run a few benign cases against a referenced guardrail configuration, including one harmless question that should still work. | A small table: expected outcome, observed outcome, and the control evidenced by the result. |

Notebook 05 supplies its own agent and knowledge-base connection code. Reuse one
knowledge base from a second agent to demonstrate that knowledge belongs to a
reusable resource, not to one assistant.

Notebook 06 defines its own small read-only tool and example inputs. Distinguish
a model refusal, a platform filter event, and an argument-validation error.
Use benign cases only. Never ask a reader to weaken protections or compose
harmful prompts.

Confirm feature, model, and region support before relying on a lesson. If a
cloud feature is unavailable, say plainly that the live activity was not run
rather than substituting a lookalike. Direct Search is never relabelled as
Foundry IQ.

## 5. Day 3: evaluation, improvement, and app exploration

**Outcome:** Compare two approaches using a few understandable observations.

| Notebook | Main topics | Small hands-on activity | Visible result |
| --- | --- | --- | --- |
| `07_evaluate_and_improve.ipynb` | Answer quality; Foundry evaluation; latency; available token usage; correct tool selection/arguments; fine-tuning. | Run 5-8 inline questions, inspect a simple score table, change one instruction or tool description, and compare. Review a small prepared base-versus-tuned example. | Before/after observations and a reasoned improvement choice. |
| `08_app_experiments.ipynb` | Using an agent through an app; connecting workshop concepts; explaining an experiment. | Try a supplied running demo or Foundry playground, then use an independent model/agent example in this notebook to change one variable. | A short written account of what changed, what improved, and what remained uncertain. |

Notebook 07 contains its own questions, expected tool choices, tiny tool, agent
setup, and comparison code. Start with human review; introduce one supported
Foundry evaluation surface rather than an evaluation-adapter architecture.
Inspect relevance/groundedness or agent-evaluation results where supported.
Measure elapsed time directly; show token usage only when returned. Do not
invent cost or treat a classroom sample as a production benchmark.

Fine-tuning remains a taught topic, not a prerequisite training job. Explain
**better instructions versus better retrieval versus training on examples**.
Inspect a few fictional training examples, separate training and held-out
examples, and compare prepared base/tuned outputs. Running a real training job
is optional and sits outside the lesson.

Notebook 08 is hands-on exploration, not app development or deployment. Work
against a playground or a small running demo. The repository's medical app is
optional; understanding medicine is not a learning objective.
Notebook changes do not automatically update an app. Record observations in a
Markdown cell, not a checkpoint system or experiment-manifest format.

## 6. What "self-contained notebook" means

Every notebook must run from a fresh kernel on its own, given the Azure
resources listed at its top. **Independent does not mean offline**: a Search or
IQ lesson still needs its Azure service.

**Target Python 3.11 or later.** Do not use syntax or standard-library
additions from a later version, such as PEP 695 generics or
`itertools.batched`. Each setup cell checks `sys.version_info` and stops with a
readable message, because the alternative is a `SyntaxError` from an
unfamiliar SDK that tells a beginner nothing.

Each notebook includes, in order:

1. **What will you do:** The goal, why the capability exists, a `text` flow diagram, and a numbered roadmap.
2. **New words:** A short glossary of the terms the lesson uses, defined before they appear in code.
3. **Before you start:** Prerequisites, including the Python floor, and how the To-Do sections work.
4. **Setup:** The package-install cell, imports, authentication, clearly marked resource settings, and the `check_todos` helper.
5. **Teaching sections:** For each idea, a markdown cell that explains the concept, compares the options in a table, states the **Run the cell. You should see** contract, and sets one **To-Do** with a goal, steps, a hint, and a collapsible solution. Then one code cell.
6. **Deterministic success check:** Assertions on structure, ending in `print("PASS - ...")`.
7. **What you learned:** A recap, reflection questions with a collapsible comparison, troubleshooting, reset notes, and an **Expected artifact:** line.

Keep the rhythm strictly alternating: one markdown cell frames every code cell.
Aim for 14 to 21 cells per notebook, and roughly a third to a half markdown.

Use the existing `AZURE_AI_PROJECT_ENDPOINT` and
`AZURE_AI_MODEL_DEPLOYMENT_NAME` names. Each notebook may read environment
variables directly or offer clearly marked nonsecret configuration fields.
Repeat the necessary configuration in each notebook; do not import repository
modules or require a shared `.env` loader. Never print credentials.

There are **no shared Python modules, test directory, checkpoint files, workshop
manifest, separate solution package, backend imports, or cross-notebook state**.
Small datasets and supplied example outputs live in cells. No external CSV or
document bundle is required for a basic example.

Keep only the safeguards needed for the demonstration: do not expose secrets,
bound tool execution, reject unsupported arguments, display errors honestly,
and never delete shared Azure resources. Do not build a validation framework.

During authoring, fill the blanks with the supplied solutions and run the
notebook top to bottom in a fresh kernel on the oldest supported Python. Then run it again with the blanks
left open and confirm it stops at the first To-Do without calling Azure.
Keep the distributed notebook's blanks and empty outputs. This is practical
rehearsal, not a separate formal testing curriculum.

## 7. Minimal repository layout

```text
labs/
  README.md
  day_1/
    README.md
    01_deploy_a_model.ipynb
    02_prompt_agents.ipynb
    03_search_and_grounded_answers.ipynb
    04_agent_framework_orchestration.ipynb
  day_2/
    README.md
    05_knowledge_bases_and_foundry_iq.ipynb
    06_guardrails.ipynb
  day_3/
    README.md
    07_evaluate_and_improve.ipynb
    08_app_experiments.ipynb
```

The four Day 1 notebooks exist under `labs/day_1/`; Day 2 and Day 3 filenames
remain authoring targets. Keep hints and suggested solutions inside each
notebook, in collapsible sections.

## 8. Short Microsoft Learn reading path

Read a selected introduction or diagram, not an entire developer tutorial.
Place a short original explanation beside the link in each notebook.

| Topic | Reading |
| --- | --- |
| Orientation | [Introduction to generative AI and agents](https://learn.microsoft.com/en-us/training/modules/fundamentals-generative-ai/) |
| Model deployment | [Foundry quickstart](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources) - deployment section only |
| Prompt agents | [Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) |
| Search and RAG | [RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) |
| Agent Framework | [Sequential orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential) |
| Foundry IQ | [Foundry IQ overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq) |
| Guardrails | [Guardrails and controls](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview) |
| Evaluation and tool calling | [Built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators) and [agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) |
| Fine-tuning | [Fine-tuning considerations](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/fine-tuning-considerations) |

Re-check SDK compatibility, links, feature availability, and permissions
whenever these notebooks are revised. Those checks belong to authoring; they
should not dominate what the reader sees.
