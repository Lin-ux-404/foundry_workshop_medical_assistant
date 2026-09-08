# Foundry notebook workshop plan

**Status:** Design and implementation plan; implementation has not started.
**Research snapshot:** 2026-09-08. Recheck SDK versions, feature availability, and source permissions before implementation.
**Scope:** Notebook curriculum, learning assets, exercises, evaluation, and instructor support.
**Application and Azure services:** [Application and Azure services plan](application-and-azure-plan.md).

## Purpose and approach

Design a three-day, guided introduction to Microsoft Foundry for people with little technical background, using a fictional medical center as a familiar setting. Participants learn what each capability does, when to use it, and how to judge its results before looking at implementation details.

The learning arc is:

**Day 1: deploy a model -> deploy an agent -> ground it with AI Search -> coordinate agents with Agent Framework.**

**Day 2: reuse knowledge with Foundry IQ -> add and understand guardrails.**

**Day 3: evaluate and improve, including fine-tuning, performance, and tool calling -> play with the app and explain the evidence.**

Retain **nine guided notebooks**: orientation, seven focused lessons, and an app-based capstone with a notebook experiment record. Each combines selected Microsoft Learn reading, a plain-language explanation, a facilitator demonstration, and a small participant activity. Revisit the same questions, fictional documents, approved education sources, and historical attendance aggregates. A separate fictional visit fixture supports patient examples without linking it to historical patients.

This document covers only the learning path. UI layouts, the Sage Mist theme, application/backend changes, detailed agent-tool contracts, and shared Azure resource provisioning are owned by the companion application plan. Participants deploy a model and register prompt agents within the organizer-prepared Foundry environment; creating subscriptions, resource groups, or an appointment system is not part of the course.

Saving this document does not authorize notebook implementation, application changes, or Azure operations. The implementation roadmap below remains future work.

## 1. Confirmed scope

| Decision | Agreed boundary |
| --- | --- |
| Audience | Primarily nontechnical; no Python, Azure administration, or machine-learning background assumed. Microsoft Learn concepts, guided portal demonstrations, small notebook choices, progressive hints, and optional technical extensions. |
| Local runtime | Jupyter, function callbacks, and Agent Framework orchestration run locally; application runtime is covered by the companion plan. |
| Azure runtime | Models, service-managed prompt agents, Blob Storage, AI Search, Foundry IQ, and selected cloud evaluation capabilities. |
| Resources | The organizer supplies shared Azure resources, permissions, connections, and `.env` configuration. Day 1 includes guided model deployment within the existing environment, with approved model, region, quota, and spending limits. No infrastructure-as-code or shared-resource provisioning curriculum. |
| Agents | Deploy/register Foundry prompt agents and coordinate at least two through Microsoft Agent Framework. No Foundry hosted-agent/container deployment. |
| Tools and knowledge | Explicitly compare multiple tool types and at least two reusable knowledge bases. |
| Medical boundary | Administrative information and sourced general patient education. No diagnosis, personalized test interpretation, clinical triage, prescribing, or patient risk scoring. |
| Data use | Original Kaggle no-show cohort for approved aggregate exercises; separate fictional patient visits and procedures. No invented departments, doctors, or future booking times attached to historical rows. |
| Actions | Read-only administrative answers and calculations. No appointment booking, rescheduling, cancellation, or approval workflows. |
| Personas | Fictional patient and staff question contexts for learning; not authentication or real role-based authorization. |
| Guardrails | Teach layered controls for model/agent behavior, retrieved content, and tool execution. Use instructor-approved configurations; never disable shared protections for a lesson. |
| Evaluation and fine-tuning | Evaluate response quality, runtime performance, and tool calling. Include a guided fine-tuning decision and base-versus-tuned comparison using prepared results or deployments; live training is an optional instructor-led extension. The final Azure evaluation surface remains for organizer review. |
| App exploration | Required Day 3 activity using the prepared patient/staff app. No app coding or hosting exercise, and no assumption that notebook changes automatically reach the app. |

### Teaching for a nontechnical audience

Teach **why -> see it -> try it -> explain it**. Begin each topic with an everyday example, then introduce its product name. Use the portal and visible outputs first where supported; notebooks are guided activity sheets, not a Python programming course.

Keep required edits to natural-language instructions, supplied names, or a small choice such as which source/tool to use. Supply SDK plumbing, authentication, tool schemas, and orchestration code. Put API details, raw JSON, and advanced extensions in clearly marked instructor/optional sections. Explain how to run a cell and read an error during orientation; do not assess coding speed.

Use short paired discussions and a plain-language checkpoint after each lesson. A participant should be able to explain why an answer needs a source, why a tool was selected, or why a result is not trustworthy without reading SDK code. Day 1 is the densest day: protect the four requested topics and move Blob authoring, charts, extra tools, and alternative orchestration patterns to optional extensions.

Introduce a small glossary progressively:

| Term | Plain-language meaning |
| --- | --- |
| Model / deployment | The AI engine / making a chosen engine available for use in our Azure environment; deployment does not mean training it. |
| Prompt / agent | Instructions or a question / a configured assistant that uses a model, instructions, and permitted tools. |
| Tool | A specific operation the assistant can request, such as retrieving a document or calculating an approved total. |
| Blob / index | File storage / a searchable representation of content. Storing a file does not automatically make it searchable. |
| RAG / grounding | Looking up relevant evidence before answering / supporting an answer with that evidence. |
| Knowledge base (KB) | A reusable collection of knowledge sources and retrieval settings that agents can query. |
| Orchestration | Coordinating which agent works on which step and what information passes between them. |
| Guardrail | A control that detects or limits particular risks; not a guarantee that every answer is safe or correct. |
| Evaluation | Checking results against agreed examples and expectations rather than judging one impressive answer. |
| Fine-tuning | Additional training that changes a model's behavior using examples; not the same as attaching documents. |
| Latency / tokens | Time spent waiting for a response / pieces of text processed by the model, which affect usage and cost. |

### Microsoft Learn preparation and in-session reading

Recommend **20-30 minutes of selected introductory reading before Day 1**, with an equivalent facilitator recap for anyone who cannot complete it. Use [Introduction to generative AI and agents](https://learn.microsoft.com/en-us/training/modules/fundamentals-generative-ai/), focusing on the **Large language models**, **Prompts**, and **AI agents** units. The module lists AI/ML familiarity as a prerequisite; the facilitator supplies that vocabulary rather than requiring another technical course. Its exercise and assessment are optional.

Before each hands-on topic, reserve roughly **5-10 minutes for selected Microsoft Learn concepts and discussion**, not completion of an entire module or developer tutorial. These are suggested teaching allocations, not Microsoft Learn's published durations. The table is the assigned reading path; the source bibliography at the end is primarily for authors and instructors.

| When | Microsoft Learn reading | Focus and understanding check |
| --- | --- | --- |
| Day 1: deploy a model | [Set up Microsoft Foundry resources](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources) - facilitator-guided model-deployment portion only. | Distinguish model choice, deployment, and training. Shared-resource creation steps are not participant tasks. |
| Day 1: deploy an agent | [What is Foundry Agent Service?](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) - overview; [prompt-agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent) is instructor reference. | Explain what instructions and tools add to a model, and which work runs locally versus in Azure. |
| Day 1: AI Search | [RAG and generative AI](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview) - introduction and classic RAG explanation. | Explain why looking up a center policy is different from asking the model to guess. |
| Day 1: Agent Framework | [Sequential orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential) - opening explanation and diagram only. | Explain how two specialist agents share a task; SDK examples are optional. |
| Day 2: Foundry IQ | [What is Foundry IQ?](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq) - overview and components. | Distinguish a reusable KB from one agent and from an individual Search index. |
| Day 2: guardrails | [Guardrails and controls overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview) - introduction, intervention points, and model/agent distinction. | Identify where a control acts and explain one limitation. Skip provisioning and role setup. |
| Day 3: evaluations and tool calling | [Built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators) and [agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) - facilitator-selected quality, task-completion, and tool-call descriptions. | Decide whether an example failed because of its answer, evidence, tool choice, or execution. No evaluator API study required. |
| Day 3: fine-tuning | [Fine-tuning considerations](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/fine-tuning-considerations) - definition and when to fine-tune. | Choose between a better prompt, better retrieval, and training on examples; justify the choice before reviewing results. |

Open readings at the relevant point in the lesson and provide a short original summary beside each link. Do not copy whole Learn articles into notebooks or present advanced documentation as prerequisite homework. Recheck links, portal labels, model support, and preview boundaries during instructor rehearsal.

## 2. Research findings that shape the design

### Notebook starting point

At the research snapshot, the three `labs\day_*` directories contain README outlines but no notebooks. Blob, Search, IQ, dataset, citation, and evaluation exercises still need implementation.

The existing booking/triage-oriented lab outlines conflict with the agreed read-only, nonclinical course boundary. Replace those exercises rather than building on them.

A direct model call through an inline `Agent(client=FoundryChatClient(...))` is not a registered, named/versioned Foundry prompt agent. The lessons must teach the latter, including the same remote agent invoked through Agent Framework.

### Datasets

- The [qacData appointments table](https://rkabacoff.github.io/qacData/reference/appointments.html) explicitly derives from [Joni Hoppen's Kaggle dataset](https://www.kaggle.com/datasets/joniarroba/noshowappointments/data). They are not two independent cohorts.
- The original Kaggle metadata declares **CC BY-NC-SA 4.0**. Do not assume CC0 because copies elsewhere use that label. Commercial-workshop use and redistribution need review.
- qacData documents 110,527 rows and 14 fields, but its date descriptions, binary-field assumptions, and some displayed encodings need scrutiny. This is useful for a provenance/data-quality discussion, not an effortless clean fixture.
- The supplied [triage dataset](https://www.kaggle.com/datasets/aditya9001/triage-data) contains 7,000 rows with `temperature`, `heart_rate`, `resp_rate`, `cough`, `fatigue`, `age`, and `risk`. Its metadata declares MIT but does not establish generation method or clinical label meaning. Exclude it from the core nonclinical course.
- Use the organizer-prepared, versioned projection of the original Kaggle no-show cohort for the attendance exercises, after rights/privacy review. The source has 110,527 appointment rows, including 22,319 marked `No-show = Yes`; the overall rate is approximately 20.2%. These are historical appointments, not a live patient schedule.
- Keep raw identifiers and health/social attributes out of agent context and knowledge indexes. Teach exact counts through bounded aggregate tools, with a separate fictional visit fixture for patient questions.
- The shared field definitions, date/denominator rules, quality exclusions, and Blob snapshot contract live in the application plan. Notebook helpers must reuse those rules, not invent departments or silently replace the cohort with synthetic data. Small synthetic fixtures can illustrate a calculation if they are explicitly labelled and never presented as source results.

### Documents

Author fictional center procedures rather than copying a real clinic's hours or policies:

| Fictional document | Useful RAG lesson |
| --- | --- |
| `contact-hours.md` | Find an exact center-specific fact instead of guessing. |
| `appointments-information.md` | Explain who to contact without executing a booking/change. |
| `visit-preparation-accessibility.md` | Retrieve check-in and interpreter/access information across sections. |
| `referral-information.md` | Explain administrative steps without deciding clinical eligibility. |
| `records-access.md` | Preserve the center/jurisdiction boundary instead of inventing legal requirements. |
| `patient-rights-language-access.md` | Reuse public communication and accessibility information across personas. |

Use reserved-domain fictional contacts and a persistent workshop notice. Keep one superseded-policy document and one labelled adversarial fixture outside the normal active corpus for controlled exercises.

For related medical education, use a small reviewed set of NLM-authored MedlinePlus Medical Test text, such as:

- [Blood testing](https://medlineplus.gov/lab-tests/what-you-need-to-know-about-blood-testing/)
- [Complete blood count](https://medlineplus.gov/lab-tests/complete-blood-count-cbc/)
- [Fluoroscopy](https://medlineplus.gov/lab-tests/fluoroscopy/)

Keep general explanatory sections, source attribution, and section-level provenance. Exclude personal-result interpretation and personalized risk advice. MedlinePlus has [mixed licensing](https://medlineplus.gov/about/using/usingcontent/); do not ingest A.D.A.M. encyclopedia articles, ASHP monographs, protected images, or linked third-party references without permission.

### Reference workshops

Use the supplied participant workshop as the main scaffolding influence: instructor-provided `.env`, small participant tasks, namespaced artifacts, explicit completion criteria, and ownership-aware cleanup.

Use Microsoft Learn's "ask before grounding, add knowledge, ask again, inspect the citation" teaching pattern. Adapt the Foundry webapp's visible tool/annotation events into notebook evidence cells, not its full C#/Entra/deployment stack.

Do not copy older agentic-ai-lab SDK code or fixed-index deletion behavior. The current `foundry-samples` prompt-agent folder includes advanced identity/skills and custom-interpreter examples; its folder name alone does not make every sample suitable for a prompt-agent-only beginner course.

## 3. Three-day notebook sequence

Use the existing day folders for the requested three-day agenda. The notebook names below are proposed implementation targets, not files already created. Reading, demonstrations, and discussion are part of each day; optional technical extensions must not displace the core activities.

| Day | Notebook and location | Learning outcome | Visible result |
| --- | --- | --- | --- |
| 1 | 00. Welcome and connections - `labs\day_1\00_welcome_and_connections.ipynb` | Explain the scenario, basic vocabulary, and local/Azure split; run a supplied cell. | Capability/readiness map without secret values. |
| 1 | 01. Deploy a model - `labs\day_1\01_deploy_a_model.ipynb` | Deploy an approved model in the prepared environment and try a prompt. | Deployment reference and a recorded model response. |
| 1 | 02. Deploy an agent - `labs\day_1\02_prompt_agents.ipynb` | Register a prompt agent, change its instructions, and observe a prepared read-only tool. | Named/versioned remote agent, ungrounded baseline, and a tool-call record. |
| 1 | 03. AI Search and grounded answers - `labs\day_1\03_search_and_grounded_answers.ipynb` | Understand documents, Blob, indexes, and retrieval; attach Search to the agent. | Ranked evidence and actual source citations. |
| 1 | 04. Agent Framework and multi-agent orchestration - `labs\day_1\04_agent_framework_orchestration.ipynb` | Run a supplied sequential workflow with at least two named Foundry prompt agents. | Observable agent-to-agent steps and a sourced combined answer. |
| 2 | 05. Knowledge bases and Foundry IQ - `labs\day_2\05_knowledge_bases_and_foundry_iq.ipynb` | Use and reuse two KBs; distinguish agent tool selection from retrieval planning. | Correct KB/source selection and cited multi-source answers. |
| 2 | 06. Guardrails - `labs\day_2\06_guardrails.ipynb` | Identify layered controls and observe approved examples of their effects and limitations. | Expected-versus-observed behavior table with control/configuration references. |
| 3 | 07. Evaluate and improve - `labs\day_3\07_evaluate_and_improve.ipynb` | Compare quality, performance, tool calling, and a prepared fine-tuning experiment. | Per-case scorecard, base-versus-tuned comparison, and an improvement decision. |
| 3 | 08. Play with the app - `labs\day_3\08_app_experiments.ipynb` | Explore patient/staff scenarios in the prepared app and explain evidence and limitations. | App observations and a reproducible notebook experiment record. |

### Day 1: deploy a model, deploy an agent, AI Search, and Agent Framework

**Daily outcome:** Participants can explain the difference between a model and an agent, show an answer supported by Search, and describe how two agents work together.

#### 00. Welcome and connections

Introduce the fictional center, two personas, and three anchor questions:

- "What should I bring to my first visit at this center?"
- "What is a complete blood count?"
- "What fraction of appointments in the historical cohort were marked no-show?"

Have learners predict whether each needs a policy document, patient-education document, or structured-data tool.

Read the existing `.env` through one shared helper. Preserve `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME`; document only the additional supplied references needed by later lessons. Check prerequisites per lesson instead of making every optional service mandatory at startup.

Show how to run and rerun a cell, distinguish a result from an error, and open the matching Learn reading. Use a simple diagram instead of an SDK walkthrough.

No resource creation, role assignment, Azure app hosting, or model download in orientation. No credentials printed in notebook output.

#### 01. Deploy a model

Begin with "choose an engine and make it available." Explain model name versus deployment name, what a prompt is, and that deployment does not train the model or load the center's documents.

The instructor demonstrates model selection and deployment in the existing Foundry environment. Participants follow the approved portal steps where permissions and quota allow, then record the deployment reference in their checkpoint. The organizer selects a supported model/version, region, deployment type, capacity, and budget before class; do not ask beginners to make infrastructure or billing decisions.

Where participant deployment is not permitted, use a clearly labelled instructor-led deployment and let participants invoke the prepared deployment. Do not claim that invoking an existing deployment created one.

Try a general question and a center-specific question, change the prompt once, and record the responses. Explain variability and unsupported claims. Use the deployment in notebook 02; reuse `AZURE_AI_MODEL_DEPLOYMENT_NAME` through the shared configuration rather than scattering endpoint edits across notebooks.

#### 02. Deploy a Foundry prompt agent and observe a tool

Explain "model + instructions + tools" before introducing Agent Service, versions, and conversations. Here **deploy an agent** means registering a named/versioned service-managed prompt agent, not deploying a container or a web application.

Learner choices: concise instructions, the Day 1 model deployment, and a namespaced agent name. Register only participant-owned prompt-agent versions in the existing project, or inspect a prepared version with an instructor-led creation demonstration when authoring permission is not supplied.

Ask a center-specific question before tools are attached. Discuss why a fluent answer is not proof of knowledge. Record the response, agent name/version, and conversation reference as the ungrounded agent baseline.

Then ask the historical no-show question and observe a supplied `get_attendance_summary` tool. Explain the three visible steps: the agent requests an operation, the local notebook validates and executes the permitted function, and the result returns to the agent. Foundry does not call a laptop's localhost endpoint directly.

Participants choose a clear tool description and predict the correct tool; they do not write a schema, aggregation algorithm, or callback loop. Display validated arguments, exact counts/denominator, snapshot provenance, and the final answer. Contrast deterministic calculation with generated prose.

Reuse the four contracts defined in the [application plan](application-and-azure-plan.md): `get_attendance_summary`, `compare_attendance_groups`, `explain_attendance_data`, and `get_demo_visit_brief`. Demonstrate the first; use the others as supplied examples for later orchestration, evaluation, and app activities. Do not duplicate or expand application schemas just for a lesson.

**Instructor implementation notes:** Use the current Projects 2.x prompt-agent API: `PromptAgentDefinition`, `create_version`, Responses, and conversations. The current official quickstart specifies `azure-ai-projects>=2.3.0`; pin a tested compatible release set. Supply a finite tool-call loop, allowlisted functions/arguments, and visible errors. Do not allow arbitrary file paths, SQL, URLs, or patient identifiers. These controls apply from Day 1, before their dedicated Day 2 explanation.

Optional Code Interpreter cells use only a small approved aggregate summary, not raw appointment rows, to produce a chart in Azure's managed interpreter. Inspect its returned file reference and independently compare totals. State model/region prerequisites and additional charges; this is not a Foundry hosted-agent deployment.

#### 03. AI Search and grounded answers

Start with "look it up before answering." Introduce the six fictional policies, three approved education documents, and their source manifest. Contrast documents for retrieval with rows for calculation. Historical aggregate tools read the approved versioned Blob snapshot; the original licensed CSV remains organizer-only.

Explain **Blob file -> chunks -> Search index -> retrieved evidence -> agent answer** using one short policy. Blob upload alone does not index content or teach an agent anything. Show a prepared object's source/version/hash and an instructor demonstration of the ingestion path. Optional authoring uploads an approved fictional document only to an authorized isolated exercise scope; read-only participants inspect prepared objects instead.

Use organizer-prepared indexes with documented text, source, title, version, namespace, vector, and filterable metadata fields. Participants inspect an understandable rendering of a chunk and its source, not an index-creation script. They do not create/delete shared indexes.

Learner choices: a search query, keyword versus hybrid retrieval, and citation/abstention instructions. Explain embeddings as representations used to find similar meaning, with one visible example; chunking details and top-k tuning are optional.

Attach the existing Search connection/index to a new prompt-agent version. Repeat the ungrounded baseline question and inspect actual source citations. Explain what improved and what remains uncertain.

A completion check must not pass because an answer merely contains the word "source." If the managed tool does not expose its full retrieval trace, display a separately labelled direct Search probe rather than presenting it as the agent's hidden retrieval.

Keep historical-data interpretation brief: inspect the label mapping, denominator, source dates, and one quality warning. An SMS-flag comparison is observational, not evidence that reminders cause or prevent missed visits. This is not a predictive-model or patient-risk-scoring course.

Optional File Search cells contrast managed file/vector-store grounding with the explicit Search/IQ path without introducing a second ingestion curriculum.

#### 04. Agent Framework and multi-agent orchestration

Begin with a two-person team analogy and the Microsoft Learn sequential-orchestration diagram. First invoke the existing named/versioned prompt agent through `agent_framework.foundry.FoundryAgent`; then run a supplied Agent Framework sequential workflow with **at least two distinct Foundry prompt agents**.

Use a read-only example: a center-information agent retrieves visit-preparation policy, then a patient-education agent adds a general explanation of a CBC and produces a combined answer that preserves the policy citations and adds its own education citations. Give each specialist explicit instructions and only the relevant prepared Search tool scope. The second agent must not treat the first agent's prose as independently verified evidence.

Learner choices: select the prepared agent references, predict their order, and write a short role description. The instructor supplies the registration/connectivity and workflow code. Show which agent ran, what observable messages and source references passed between steps, which tools ran, and the final answer. Compare the workflow with a single-agent response; more agents do not automatically mean better quality.

Explain what the service owns (model, instructions, declared tools, version) and what the local Framework client owns (orchestration, session handling, local function execution, result presentation). Record all agent versions and workflow settings for Day 3 evaluation.

Do not replace the named remote agents with `Agent(client=FoundryChatClient(...))` and imply that direct model inference is the same thing. Supply bounded execution, explicit errors, and citation-preserving handoffs. Streaming, parallel orchestration, and routing are optional comparisons; do not require learners to author a graph or an appointment workflow. No hosted-agent infrastructure or Foundry Workflow authoring.

### Day 2: Foundry IQ and guardrails

**Daily outcome:** Participants can reuse knowledge across agents and explain which controls limit risky behavior, including what those controls cannot guarantee.

#### 05. Knowledge bases and Foundry IQ

Use two prepared reusable KBs:

- `center-operations-kb`: fictional policies, contact information, visit/accessibility procedures.
- `patient-education-kb`: the small attributed NLM education corpus.

These can be backed by separate prepared indexes/knowledge sources on one Search service. They do not require separate Azure Search services. The organizer supplies the physical configuration.

Teach the distinctions explicitly:

**Document -> chunk/index -> knowledge source -> knowledge base -> retrieval tool -> agent.**

Learners choose KB references from supplied options, write source descriptions, and predict the right source. Explain MCP as a standard way for an agent to call an external capability; connection/authentication code is supplied. Connect the KB MCP endpoints to service-managed prompt agents using the supplied project connections. Reuse the public education KB in patient and staff prompt-agent configurations, building on Day 1's specialists.

Exercises:

- Choose the right KB for a single-source question.
- Ask a question needing both center information and general medical education, with separate citations.
- Ask for information absent from both KBs.
- Inspect a superseded-policy fixture and explain why version/status filtering matters.
- Inspect an MCP call/approval when the configured policy requires approval.

Distinguish the agent selecting a KB/tool from IQ planning searches inside a KB. Show subqueries/activity only when the service actually returns them.

Foundry IQ is **partially GA**, not simply "all GA" or "all preview." The `2026-04-01` Search API supports a subset; non-minimal reasoning, answer synthesis, multi-turn capabilities, and current portal experiences have preview boundaries. Pin the supported API/SDK combination supplied by the organizer.

IQ remains a planned curriculum topic. If unavailable in a particular environment, show an explicitly labelled saved IQ example alongside live direct Search; do not silently relabel the fallback as IQ.

An organizer-provided Toolbox can be an optional final comparison: a Toolbox groups callable tools; a KB groups knowledge sources. Do not add a provisioning or advanced skills course.

#### 06. Guardrails

Start with "what should this assistant never do, and where can we enforce that?" Revisit the administrative/general-education boundary and distinguish an instruction from an enforced control.

| Layer | Guided example | Limitation to explain |
| --- | --- | --- |
| Instructions and response scope | Ask for an unsupported center fact or an individualized clinical conclusion; inspect abstention or redirection. | A well-written prompt is not an authorization or security boundary. |
| Foundry guardrails/content controls | Inspect instructor-approved model/agent guardrail configurations, content filters, and Prompt Shields where supported; replay a benign labelled prompt-injection fixture. | Coverage depends on the model, intervention point, and feature availability; filters do not establish factual or clinical correctness. |
| Retrieval and data controls | Inspect active-policy filtering and keep raw identifiers and the adversarial fixture out of the normal corpus. | Citations and classroom personas do not enforce real user permissions. |
| Tool execution controls | Attempt an unsupported filter or a request to change an appointment against the supplied read-only tool contract. | Enforcement belongs in the tool allowlist/argument validation, not just the tool description. |

Participants predict **answer / abstain / block / reject tool request**, run supplied cases, and record the observed outcome and the control responsible. Include a harmless question that should still work to discuss overblocking. Separate a model refusal from a platform filter event or a local tool-validation error; do not infer that a specific control fired without evidence.

Use prepared approved configurations for comparison, or let participants select only an allowed configuration in their isolated scope. Do not disable shared protections, weaken production settings, or ask learners to invent harmful prompts. The instructor owns any permission-sensitive guardrail authoring.

Agent guardrails and tool-call/tool-response intervention points have preview boundaries at the research snapshot. Check exact model/agent support before class; do not imply that a Foundry guardrail automatically governs every local Framework step. Keep local validation in place regardless of cloud feature availability. If a feature is unavailable, label its saved demonstration and continue the live instruction/retrieval/tool-control exercises without calling those a live Foundry guardrail run.

Save the guardrail/configuration references and expected-versus-observed table for Day 3. Guardrails reduce specified risks; they do not replace evaluation, human review, or clinical validation.

### Day 3: evaluations, fine-tuning, performance, tool calling, and app exploration

**Daily outcome:** Participants can use a simple scorecard to compare alternatives, explain when fine-tuning may help, and assess the assistant through the prepared app.

#### 07. Evaluate and improve

Start with "how would we know it got better?" Participants agree on a few plain-language success criteria before seeing scores. Use three guided parts in the same notebook: quality/performance, tool calling, and fine-tuning as an evaluation-led improvement option.

**Quality and performance.** Start with a hand-reviewed set of approximately 12 concise cases, not automatically generated medical ground truth. Include ordinary questions, multi-source questions, exact numeric queries, unknown answers, conflicting/superseded policy, wrong-tool choices, and an out-of-scope clinical request.

| Dimension | Participant question | Evidence |
| --- | --- | --- |
| Answer quality | Is it useful, understandable, and supported by the right sources? | Human notes, actual citation IDs, relevance/groundedness results, and expected source coverage. |
| Numeric correctness | Did it calculate the right result from the approved snapshot? | Deterministic exact counts, denominators, validated filters, and snapshot version. |
| Runtime performance | How long did we wait, and how much work did the system do? | End-to-end latency, observed model/tool calls, token usage where available, and a labelled cost estimate only when supported by usage and pricing inputs. |
| Tool calling | Did it choose the right tool, supply valid arguments, and use the returned result correctly? | Recorded requests/results, expected tool or no-tool outcome, argument checks, errors, and applicable agent evaluators. |
| Guardrails and scope | Did it abstain, block, or reject when expected without blocking harmless tasks? | Day 2 cases, control references, and observed outcomes rather than assumed filter events. |

Each case records expected behavior, expected tool/KB, and expected source IDs. Capture the actual answer, available context, citations, tool inputs/outputs, all participating agent/model versions, corpus/snapshot versions, retrieval settings, and guardrail configuration. Distinguish unavailable metrics from zero; never fabricate usage or cost.

Compare a baseline with one deliberate improvement. Keep the questions, corpus, attendance snapshot, and fictional fixture fixed; show per-case failures and disagreements, not only an average. Repeat selected cases to illustrate variability and report the sample size; this small class exercise is not a production performance benchmark. Include no-data handling, exact no-show counts, and rejection of causal SMS claims without implying a clinical assessment.

**Tool-calling evaluation.** Compare expected versus actual choices across Search, a KB MCP tool, and the local read-only functions. Include a question that needs no tool, an invalid-argument case, a surfaced execution failure, and a multi-agent handoff. Change one tool description and rerun the same cases. Evaluate both task completion and the sequence of steps; a plausible final sentence does not prove correct tool use.

**Fine-tuning and comparison.** Explain the difference between improving instructions, improving retrieval, and training a model on examples. Use consistent plain-language response format or tool-selection behavior as the example, not personalized medical advice. Fine-tuning is not a replacement for current policy retrieval, exact calculations, or guardrails.

The instructor shows a small, rights-cleared fictional training-data excerpt, explains separate training/validation/test sets, and walks through a prepared fine-tuning job and its results. Evaluate the corresponding base model and tuned model on held-out cases with the same task settings, tools, and data. Keep final test cases out of training and tuning decisions; compare quality, tool use, latency, and available cost evidence without promising an improvement.

The required participant activity is to inspect examples, predict the effect, compare the base-versus-tuned scorecard, and decide whether tuning was worthwhile. Provide prepared deployments or clearly labelled saved runs so completion does not depend on training time, model eligibility, regional support, or quota. A live fine-tuning submission is an optional instructor-led extension with explicit budget approval, never an assumed participant task. Do not train on the historical patient-level dataset or the workshop's evaluation cases.

**Instructor evaluation implementation notes:** Use deterministic checks, hand-authored retrieval labels, human review, and groundedness/relevance judges as complementary evidence. String matching is not semantic groundedness; an AI judge or high score is not clinical validation.

The preferred candidate is **Foundry cloud dataset evaluation through Projects 2.x**, with results inspected in the portal. The alternative is `azure-ai-evaluation` for locally orchestrated scoring using Azure judge models/services. These are distinct supported surfaces. Because some functions and orchestration execute locally, capture the real flow and submit versioned JSONL for scoring; cloud agent-target evaluation cannot invoke localhost functions or reproduce an uncaptured local workflow. Use remote target evaluation only where its tools run remotely. Keep the implementation behind a narrow adapter until the organizer chooses the product and confirms evaluator/model support.

#### 08. Play with the app and explain an experiment

Make hands-on app exploration a **core Day 3 activity**, not an optional final demonstration. The organizer supplies the running app, approved data, working agent connections, and a short scenario sheet; learners do not build or deploy the application.

| Scenario | Participant activity | Evidence to discuss |
| --- | --- | --- |
| Patient view | Ask what to bring to the fictional visit and request a general CBC explanation. | Center-policy versus education citations; no personal test interpretation. |
| Staff view | Explore the attendance dashboard and ask for a no-show total or an approved comparison. | Agreement between dashboard filters and bounded tool counts, snapshot provenance, and observational limitations. |
| Boundaries | Ask for an unknown center fact or an appointment change. | Honest abstention/read-only boundaries, visible errors, and no invented action success. |
| Experiment | Choose one change in prompt wording, tool description, retrieval mode/top-k, active source version, or KB selection; predict and replay fixed cases. | Before/after evidence and the Day 3 scorecard, including regressions and uncertainty. |

Use the app for exploration and the notebook for recording the hypothesis, configuration references, observed results, and explanation. Save an experiment manifest that another clean kernel can replay. Participants finish with a brief plain-language account of what changed, what evidence supports it, and what still needs human review.

The existing app does not automatically load notebook checkpoints or inherit agent-version changes. Core app exploration can use a fixed, organizer-tested configuration while the change-one-variable experiment runs in the notebook. Demonstrating that change inside the app requires the explicit checkpoint/configuration adapter described in the companion plan; show the active app configuration and never imply that a notebook edit updated it.

A running app is a prerequisite for delivering this day as planned. A saved walkthrough is a labelled contingency, not completion of the hands-on app activity; record that gap and arrange the missing activity rather than silently downgrading it to optional.

## 4. Repeated notebook format and supporting files

Each notebook uses:

**Situation -> plain-language concept and glossary -> selected Microsoft Learn reading -> objective -> where it runs -> instructor demonstration -> prediction -> small choices/blanks -> evidence -> change one variable -> explain it back -> optional technical extension -> safe reset.**

Use a small number of concept-focused blanks per lesson. Preserve runnable surrounding code, progressive hints, and instructor solutions. Helpers remove repetitive plumbing; keep the relevant SDK calls available in an optional technical explanation rather than requiring participants to understand them to complete the activity. Every lesson includes a beginner-readable expected output and a "what this does not prove" note.

Proposed supporting layout:

```text
labs\
  README.md
  requirements.txt
  shared\
    config.py
    clients.py
    artifacts.py
    display.py
    checks.py
  data\
    synthetic\
    policies\
    education\
    source-manifest.json
  evaluations\
    cases.jsonl
    prepared-runs\
  fine_tuning\
    fictional-training-examples.jsonl
    experiment-manifest.json
  solutions\
    day_1\
    day_2\
    day_3\
  day_1\...
  day_2\...
  day_3\...
```

Exact helper boundaries should stay small during implementation. Reuse existing configuration conventions, and preserve the user's existing `backend\.env.example` content.

The `synthetic` folder contains only explicit teaching/fictional fixtures, not a replacement attendance cohort. Historical data is loaded from the supplied versioned Blob snapshot; do not commit the original licensed CSV to the notebook scaffolding.

The organizer-supplied configuration covers the existing project, model-deployment choices or prepared deployment, Blob destination, Search indexes/connections, KB/MCP references, approved guardrail configurations, API version, and any judge/base/tuned deployments. Model and agent versions, orchestration settings, app configuration references, and experiment results belong in a nonsecret workshop manifest, not scattered manual `.env` edits. Fine-tuning examples and saved runs need their own provenance and clear live/saved labels.

Every notebook supports a fresh kernel and explicit artifact loading. No reliance on another notebook's live variables.

Writable artifacts require an explicit participant namespace and ownership record. Enforce namespace/active-version constraints in retrieval configuration, not only in prompts. If the selected managed tool cannot enforce those constraints on a shared index, use an organizer-prepared isolated scope or the explicitly read-only prepared corpus. A classroom namespace or persona filter is not a real authorization boundary.

## 5. Shared artifact contract

Use one small versioned contract for notebook learning outputs. Application-specific request/response schemas and the four tool contracts stay in the companion plan:

| Artifact | Essential fields |
| --- | --- |
| Source | ID, title, publisher, URL, license/status, fictional/real classification, audience, version, update/acquisition date, hash. |
| Chunk | Chunk/document ID, section/page, content, source reference, version, namespace, active status. |
| Retrieval | Query, retrieval mode, KB/source/index reference, actual returned hits/references, optional service score/activity. |
| Model deployment | Model name/version, deployment reference/type, participant/instructor ownership, and live-created versus prepared status; no credentials. |
| Agent run | Run/conversation reference, agent name/version, model deployment, answer, citations, observable tool events, persona, corpus version, guardrail configuration reference. |
| Orchestration | Workflow version/pattern, participating agent names/versions, observed execution order, handoff messages/source references, and surfaced errors. |
| Structured-data result | Tool name, validated filters, exact counts/denominators, warnings, dataset/fixture version, snapshot/ETag/hash evidence. |
| Guardrail observation | Case ID, expected/observed outcome, control/configuration reference, intervention point if known, observed event/error, live/saved status. |
| Evaluation | Case ID, expected behavior/tool/arguments/sources, observed output/context, evaluator version/results, latency, available usage/cost inputs, human notes. |
| Fine-tuning comparison | Base/tuned model and job references, rights-cleared training/validation/test split versions, fixed evaluation settings, per-case results, limitations, live/saved status. |
| App observation | Scenario, active app configuration/version, visible filters, question/answer, source/tool evidence, linked notebook experiment if applicable. |
| Workshop checkpoint | Schema version, namespace, resource references, corpus version, active agent versions, output artifact references. |

Sources with uncertain rights remain link-only/excluded. Do not upload original historical patient-level rows to the default KB, prompt context, or evaluation dataset.

Show only observed tool calls, data, and service events. Never fabricate a trace, citation, query decomposition, score, or live-result status.

## 6. Implementation todos and dependencies

The following are future implementation tasks, not work already performed or authorized by saving this plan.

| ID | Todo | Depends on |
| --- | --- | --- |
| `workshop-contract` | Establishing the three-day curriculum/configuration/artifact contract and a small compatible SDK set, reusing the application plan's data/tool rules and prepared instructor-owned resources. Confirming deployment permissions, cost limits, feature support, and app-readiness dependencies. | None |
| `learn-scaffolding` | Curating the selected Microsoft Learn units/sections, plain-language summaries, glossary, facilitator demonstrations, and concept checks for nontechnical participants. | `workshop-contract` |
| `workshop-assets` | Authoring fictional fixtures/procedures and approved education text; preparing source/rights manifests and question labels that reference the approved attendance snapshot. | `workshop-contract` |
| `notebook-scaffold` | Creating the shared notebook helpers, beginner lesson template, progressive hints, instructor solutions, and fresh-kernel artifact loading. | `learn-scaffolding` |
| `notebooks-foundations` | Implementing Day 1 notebooks 00-03: orientation, explicit model deployment, prompt-agent deployment with a prepared tool, and Search grounding with Blob/source context. | `workshop-assets`, `notebook-scaffold` |
| `notebook-framework` | Implementing Day 1 notebook 04 with at least two named/versioned prompt agents in a supplied sequential Framework orchestration, preserving source evidence across steps. | `notebooks-foundations` |
| `notebook-iq` | Implementing Day 2 notebook 05 with two reusable IQ KBs, MCP, and explicit capability boundaries. | `notebook-framework` |
| `notebook-guardrails` | Implementing Day 2 notebook 06 with approved configurations, benign fixtures, layered control examples, and expected-versus-observed outcomes. | `notebook-iq` |
| `evaluation-design` | Finalizing fixed cases and evaluator choice; implementing Day 3 notebook 07 quality, runtime-performance, tool-calling, and guardrail scorecards. | `notebook-guardrails` |
| `fine-tuning-comparison` | Preparing rights-cleared fictional training examples, separate validation/test cases, and a reproducible base-versus-tuned comparison for notebook 07; documenting budget, model support, and saved-run contingencies. | `evaluation-design` |
| `app-readiness` | Coordinating the core patient/staff scenarios with the application workstream; confirming a running app, approved data, visible sources/tool evidence, and active configuration. Keeping notebook-to-app configuration transfer optional and explicit. | `workshop-contract` |
| `notebook-capstone` | Implementing Day 3 notebook 08's required app exploration and notebook experiment record; updating lab navigation and instructor notes. | `fine-tuning-comparison`, `app-readiness` |
| `workshop-rehearsal` | Rehearsing completed solutions and app scenarios, selected Learn readings, beginner pacing, evidence/replay, explicit fallback labels, and owned-artifact cleanup. | `notebook-capstone` |

Prepared shared Azure services, approved deployment/guardrail permissions, the approved Blob snapshot, compatible bounded tool helpers, evaluation/fine-tuning assets, and the running app are external prerequisites coordinated with the organizer and application/Azure workstream. Notebook authors consume those contracts rather than independently provisioning shared resources or implementing competing metric definitions. This revised curriculum does not claim that the companion application's implementation work is already complete.

## 7. Completion criteria

- The agenda follows the requested order: Day 1 model deployment, agent deployment, AI Search, and Agent Framework multi-agent orchestration; Day 2 Foundry IQ and guardrails; Day 3 evaluations including fine-tuning, performance, and tool calling, followed by app exploration.
- Each core topic has selected Microsoft Learn background, an original plain-language summary, a guided activity, and a concept check. No Python programming, Azure administration, or ML theory is required to finish the core path.
- Model and prompt-agent deployment are explicit activities in the existing environment, with any instructor-led/prepared variants clearly distinguished from participant-created deployments.
- Day 1 runs at least two named/versioned Foundry prompt agents in a real Framework orchestration and preserves observable handoff/source evidence; a single-agent invocation alone does not satisfy this outcome.
- Participants demonstrate at least three distinct tool paths: managed Search, a client-executed read-only function, and a remote KB MCP tool.
- Two KBs are actually referenced and reused; multi-source claims retain distinct citations.
- Guardrail exercises distinguish instructions, platform controls, retrieval restrictions, and local tool enforcement; observed outcomes and feature limitations are recorded without disabling shared protections.
- Each notebook contains meaningful small choices/blanks, hints, visible expected artifacts, and a corresponding instructor solution.
- Completed solutions run from clean kernels with explicit state loading; no invisible dependence on previous live notebook sessions.
- Attendance examples use only the approved aggregate-facing historical snapshot; patient examples remain fictional, and education content is attributed and permitted. Raw identifiers are never sent to the agent.
- No shared-infrastructure provisioning, hosted agents, end-user login implementation, appointment mutation, or clinical decision-making is required. Supplied Azure development authentication is still necessary; guided model/agent deployment is in scope.
- Live results, saved examples, unavailable features, and failed calls are visibly distinguishable.
- Cleanup touches only recorded participant-owned learning artifacts/deployments and never deletes shared model deployments, indexes, knowledge bases, connections, storage accounts, or resource groups. Organizer-owned training/deployment costs require an explicit retention/cleanup plan.
- Evaluation comparisons use fixed cases, include quality, runtime-performance and tool-calling evidence, and report limitations; the organizer's final evaluation-product decision is recorded before implementation is treated as complete.
- Participants explain prompting versus retrieval versus fine-tuning and review a documented base-versus-tuned comparison on held-out cases. A live training job is not required; saved evidence is labelled.
- Participants complete the prepared patient/staff app scenarios and explain an experiment using visible evidence. Notebook-to-app configuration transfer is not assumed; a missing app remains an explicit delivery gap, not a silently completed capstone.

## 8. Source references

These references preserve the research trail without depending on session-local files. Product documentation and sample repositories can change; use the research snapshot as context, not a guarantee of future API compatibility.

### User-provided workshop references

- [Foundry prompt-agent samples](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/prompt-agents)
- [Foundry agent webapp](https://github.com/microsoft-foundry/foundry-agent-webapp)
- [Foundry agent webapp architecture](https://github.com/microsoft-foundry/foundry-agent-webapp/blob/main/ARCHITECTURE-FLOW.md)
- [Agentic AI lab](https://github.com/microsoft/agentic-ai-lab)
- [Microsoft Learn AI fundamentals](https://microsoftlearning.github.io/mslearn-ai-fundamentals/)
- [Microsoft Learn Foundry IQ exercise](https://github.com/MicrosoftLearning/mslearn-ai-fundamentals/blob/main/Instructions/Exercises/07-foundry-iq.md)
- [Participant workshop](https://github.com/Lin-ux-404/foundry_workshop_participant_view/blob/main/labs/azure-ai-agents/README.md)

The four Microsoft repositories reported MIT licensing during research. The participant repository's reuse license was not confirmed. Prefer original instructional material and preserve applicable notices; repository licenses do not automatically cover external datasets or embedded media.

### Dataset provenance

- [Original no-show dataset metadata and license](https://www.kaggle.com/api/v1/datasets/view/joniarroba/noshowappointments)
- [qacData appointments documentation](https://rkabacoff.github.io/qacData/reference/appointments.html)
- [qacData source documentation](https://github.com/rkabacoff/qacData/blob/master/R/appointments.R)
- [Triage dataset metadata and license](https://www.kaggle.com/api/v1/datasets/view/aditya9001/triage-data)

### Foundry, retrieval, and tools

- [Introduction to generative AI and agents - beginner training](https://learn.microsoft.com/en-us/training/modules/fundamentals-generative-ai/)
- [Set up Foundry resources - model-deployment portion](https://learn.microsoft.com/en-us/azure/foundry/tutorials/quickstart-create-foundry-resources)
- [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Prompt-agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)
- [Agent Framework integration with Foundry Agent Service](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/agent-services/foundry)
- [Agent Framework sequential orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential)
- [Azure AI Search RAG overview](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)
- [Foundry IQ concepts](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq)
- [Agentic retrieval overview](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-overview)
- [Agentic retrieval API migration and capability boundaries](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-migrate)
- [Connect Foundry IQ to an agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/foundry-iq-connect)
- [Azure AI Search tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search)
- [Function calling](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/function-calling)
- [MCP tools](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [Code Interpreter](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter)
- [File Search](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/file-search)
- [Toolbox overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/toolbox-overview)

### Guardrails, evaluation, and fine-tuning

- [Foundry guardrails and controls overview](https://learn.microsoft.com/en-us/azure/foundry/guardrails/guardrails-overview)
- [Foundry cloud evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation)
- [Cloud evaluation datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets)
- [Cloud evaluation targets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets)
- [Built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
- [Agent evaluators, including tool calling](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Azure AI Evaluation Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-evaluation-readme?view=azure-python)
- [Fine-tuning considerations and when to fine-tune](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/fine-tuning-considerations)
