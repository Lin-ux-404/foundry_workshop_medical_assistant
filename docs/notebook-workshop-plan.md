# Foundry notebook workshop plan

**Status:** Design and implementation plan; implementation has not started.
**Research snapshot:** 2026-09-08. Recheck SDK versions, feature availability, and source permissions before implementation.
**Scope:** Notebook curriculum, learning assets, exercises, evaluation, and instructor support.
**Application and Azure services:** [Application and Azure services plan](application-and-azure-plan.md).

## Purpose and approach

Design a coherent set of fill-in-the-blank Jupyter notebooks that teaches Microsoft Foundry through a fictional medical center. The center is the familiar setting, not the product being built.

The learning arc is:

**Ask without knowledge -> load documents -> use tools -> retrieve evidence -> reuse knowledge bases -> invoke the same agent through Agent Framework -> evaluate and improve.**

Recommend **nine small notebooks**: orientation, seven focused lessons, and a capstone experiment. Each produces an inspectable artifact and revisits the same questions, fictional documents, approved education sources, and historical attendance aggregates. A separate fictional visit fixture supports patient examples without linking it to historical patients.

This document covers only the learning path. UI layouts, the Sage Mist theme, application/backend changes, detailed agent-tool contracts, and Azure resource provisioning are owned by the companion application plan. The notebooks use organizer-prepared services; building an appointment system is not part of the course.

Saving this document does not authorize notebook implementation, application changes, or Azure operations. The implementation roadmap below remains future work.

## 1. Confirmed scope

| Decision | Agreed boundary |
| --- | --- |
| Audience | Mixed technical confidence; one guided notebook path, small blanks, progressive hints, optional technical extensions. |
| Local runtime | Jupyter and its function callbacks run locally; application runtime is covered by the companion plan. |
| Azure runtime | Models, service-managed prompt agents, Blob Storage, AI Search, Foundry IQ, and selected cloud evaluation capabilities. |
| Resources | The organizer supplies Azure resources, permissions, connections, and `.env` configuration. No provisioning/IaC curriculum. |
| Agents | Foundry prompt agents only. No Foundry hosted-agent/container deployment. |
| Tools and knowledge | Explicitly compare multiple tool types and at least two reusable knowledge bases. |
| Medical boundary | Administrative information and sourced general patient education. No diagnosis, personalized test interpretation, clinical triage, prescribing, or patient risk scoring. |
| Data use | Original Kaggle no-show cohort for approved aggregate exercises; separate fictional patient visits and procedures. No invented departments, doctors, or future booking times attached to historical rows. |
| Actions | Read-only administrative answers and calculations. No appointment booking, rescheduling, cancellation, or approval workflows. |
| Personas | Fictional patient and staff question contexts for learning; not authentication or real role-based authorization. |
| Evaluation | Specify the learning goals and data contract now; the final Azure evaluation surface remains for the organizer to review. |

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

## 3. Proposed notebook sequence

Retain the existing day folders as navigation groups, without prescribing workshop duration.

| Notebook | Location | Learning outcome | Visible result |
| --- | --- | --- | --- |
| 00. Welcome and connections | `labs\day_1\00_welcome_and_connections.ipynb` | Explain what runs locally versus Azure and load the supplied environment. | Capability/readiness map without secret values. |
| 01. Documents, data, and Blob | `labs\day_1\01_documents_and_blob.ipynb` | Distinguish a document from a structured dataset; read prepared data and upload approved fictional assets where permitted. | Source manifest, historical aggregate summary, and a Blob round trip or labelled read-only variant. |
| 02. A real Foundry prompt agent | `labs\day_1\02_prompt_agents.ipynb` | Understand model + instructions + tools, Agent Service, versions, and conversations. | Named/versioned remote agent and an ungrounded baseline. |
| 03. Give the agent tools | `labs\day_1\03_tools_and_structured_data.ipynb` | Observe function request, local execution, and returned output. | Exact attendance counts, snapshot evidence, and a tool-call record; optional chart. |
| 04. Search and grounded answers | `labs\day_2\04_search_and_grounded_answers.ipynb` | Inspect chunks/indexes, compare retrieval, attach Azure AI Search as a tool. | Ranked evidence and actual source citations. |
| 05. Knowledge bases and Foundry IQ | `labs\day_2\05_knowledge_bases_and_foundry_iq.ipynb` | Use and reuse two KBs; distinguish agent tool selection from retrieval planning. | Correct KB/source selection and cited multi-source answers. |
| 06. The same agent through Agent Framework | `labs\day_3\06_agent_framework.ipynb` | Invoke an existing prompt-agent version through the Framework client. | Equivalent behavior, sessions, and observable tool events. |
| 07. Evaluate and improve | `labs\day_3\07_evaluate_and_improve.ipynb` | Compare configurations with a fixed question set and review failures. | Per-case evaluation table and a reproducible improvement experiment. |
| 08. Explain your experiment | `labs\day_3\08_workshop_experiments.ipynb` | Change one setting, replay the scenario, and explain the effect. | Reproducible experiment record and a notebook-based evidence presentation. |

### 00. Welcome and connections

Introduce the fictional center, two personas, and three anchor questions:

- "What should I bring to my first visit at this center?"
- "What is a complete blood count?"
- "What fraction of appointments in the historical cohort were marked no-show?"

Have learners predict whether each needs a policy document, patient-education document, or structured-data tool.

Read the existing `.env` through one shared helper. Preserve `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME`; document only the additional supplied references needed by later lessons. Check prerequisites per lesson instead of making every optional service mandatory at startup.

No resource creation, role assignment, Azure app hosting, or model download. No credentials printed in notebook output.

### 01. Documents, data, and Blob

Inputs: six small fictional policies, three approved medical-education documents, the prepared attendance projection and audit/manifest, and a separate fictional visit fixture. The original licensed CSV remains organizer-only; participants consume the approved curated snapshot and aggregate results.

Learner blanks: select the document category, approved destination prefix, and useful metadata. Read the prepared objects and inspect source/version/hash. With supplied authoring permissions, upload an approved fictional document only to the designated exercise scope and read it back. If the supplied identity is read-only, use the explicitly labelled prepared-object variant instead; do not grant writes to shared snapshots just to complete a cell.

Explain that Blob upload alone does not index content or teach an agent anything. Contrast "documents for retrieval" with "rows for calculation."

Keep the data lesson small: inspect the label mapping, denominator, source dates, and one quality warning. Explain that an SMS-flag comparison is observational, not evidence that reminders cause or prevent missed visits. This is not a predictive-model or patient-risk-scoring course.

### 02. A real Foundry prompt agent

Use the current Projects 2.x prompt-agent API: `PromptAgentDefinition`, `create_version`, Responses, and conversations. The current official quickstart specifies `azure-ai-projects>=2.3.0`; implementation should pin a tested compatible release set rather than install unbounded latest versions.

Learner blanks: concise instructions, supplied model deployment, and a namespaced agent name. Register only participant-owned prompt-agent versions in the existing project, or inspect a prepared version when authoring permission is not supplied.

Ask a center-specific question before tools are attached. Discuss why a fluent answer is not proof of knowledge. Record the response, agent name/version, and conversation reference as the baseline.

Agent Service is taught here as the Azure service managing the agent; it does not need an artificial separate deployment lesson.

### 03. Give the agent tools

Core exercise: declare `get_attendance_summary` on the remote prompt agent and supply its bounded Python implementation locally, reading the approved attendance snapshot from Azure Blob through the shared data helper.

Learner blanks: tool description, an allowlisted filter/schema field, and the intended aggregation. Make the agent request the function, inspect arguments, validate them, execute the allowlisted function, and return the result to the service. Foundry does not call a laptop's localhost endpoint directly; the notebook handles the callback and submits its output.

Reuse the four contracts defined in the [application plan](application-and-azure-plan.md): `get_attendance_summary`, `compare_attendance_groups`, `explain_attendance_data`, and `get_demo_visit_brief`. After completing the first tool, participants inspect supplied implementations of the others and predict which fits a comparison, a provenance question, or a fictional visit question. Do not duplicate or expand the application schemas just for a lesson.

Contrast a KB answer with a deterministic numeric answer. Use a finite tool-call loop and visible errors; do not allow arbitrary file paths, SQL, URLs, or patient identifiers.

Optional Code Interpreter cells upload only a small approved aggregate summary, not raw appointment rows, and request a chart in Azure's managed interpreter. Inspect the returned file reference and independently compare totals. This is a managed tool on a prompt agent, not a Foundry hosted-agent deployment. State model/region prerequisites and additional charges.

Optional File Search cells can contrast managed file/vector-store grounding with the more explicit Search/IQ path. Do not introduce a second full ingestion curriculum.

### 04. Search and grounded answers

Use organizer-prepared indexes with documented text, source, title, version, namespace, vector, and filterable metadata fields. Participants inspect the schema and upload approved chunks only into their designated learning scope; they do not create/delete shared indexes.

Learner blanks: a heading-aware chunking choice, a search query, retrieval mode, top-k, and citation/abstention instructions.

Compare keyword and hybrid retrieval on the same question. Explain embeddings through a small visible example; do not bury learners in vector-index algorithms.

Attach the existing Search connection/index to a new prompt-agent version using the Azure AI Search tool. Repeat the baseline question and inspect real annotation/reference objects.

A completion check must not pass because the answer merely contains the word "source." Where a managed tool does not expose its full retrieval trace, say so; display a separately labelled direct Search probe rather than pretending it is the agent's exact hidden retrieval.

### 05. Knowledge bases and Foundry IQ

Use two prepared reusable KBs:

- `center-operations-kb`: fictional policies, contact information, visit/accessibility procedures.
- `patient-education-kb`: the small attributed NLM education corpus.

These can be backed by separate prepared indexes/knowledge sources on one Search service. They do not require separate Azure Search services. The organizer supplies the physical configuration.

Teach the distinctions explicitly:

**Document -> chunk/index -> knowledge source -> knowledge base -> retrieval tool -> agent.**

Learners fill KB references, source descriptions, and expected-source labels. Connect the KB MCP endpoints to service-managed prompt agents using the supplied project connections. Reuse the public education KB in patient and staff prompt-agent configurations.

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

### 06. The same agent through Agent Framework

Use `agent_framework.foundry.FoundryAgent` to connect to the already-created prompt-agent name/version. Do not replace it with an application-owned `Agent(client=FoundryChatClient(...))` and imply they are identical.

Learner blanks: agent name/version, the callable matching a function already declared remotely, and the example persona/question.

Explain what the service owns (model, instructions, declared tools, version) and what the local Framework client owns (client orchestration, session handling, local function execution, result presentation).

Inspect the same response/citation/tool contract used earlier. Optional streaming illustrates observable progress, not hidden chain-of-thought. No multi-agent appointment workflow, hosted-agent infrastructure, or Foundry Workflow authoring.

### 07. Evaluate and improve

Start with a hand-reviewed set of approximately 12 concise cases, not automatically generated medical ground truth. Include ordinary questions, multi-source questions, exact numeric queries, unknown answers, conflicting/superseded policy, wrong-tool choices, and an out-of-scope clinical request.

Each case records expected behavior, expected tool/KB, and expected source IDs. Capture the actual answer, exact available context, citations, tool inputs/outputs, agent version, corpus version, and retrieval settings.

Compare a baseline with one deliberate improvement. Keep the question set, corpus, attendance snapshot, and fictional fixture version fixed; show failures and disagreements, not only an average score. Include no-data handling, exact no-show counts, and rejection of causal SMS claims without implying a clinical assessment.

Proposed measurement layers:

- Deterministic evidence checks: valid citation IDs, actual tool call, correct exact counts, expected output structure.
- Retrieval checks: relevant source coverage, with hand-authored relevance labels where appropriate.
- Cloud judges: groundedness and relevance as the initial candidates.
- Human review: useful answer, clear language, faithful source use, appropriate abstention, and no individualized clinical conclusions.

Do not describe string matching as semantic groundedness or a high score as clinical validation.

The preferred candidate is **Foundry cloud dataset evaluation through Projects 2.x**, with results inspected in the portal. The alternative is `azure-ai-evaluation` for locally orchestrated scoring using Azure judge models/services. These are distinct supported surfaces, not interchangeable API examples.

Because some functions execute on the laptop, capture the real local flow and submit its versioned JSONL for cloud scoring. Cloud agent-target evaluation cannot invoke localhost functions. Use remote target evaluation only for agents whose required tools execute remotely.

Keep the final evaluation implementation behind a narrow adapter until the organizer chooses the product. The case design and deterministic/human comparison do not depend on that choice.

### 08. Explain your experiment

Let each participant choose one change: prompt wording, tool description, retrieval mode/top-k, active source version, or KB selection.

They predict the result, publish an owned checkpoint, replay the same cases, inspect evidence, and explain what changed. Save an experiment manifest that another clean kernel can replay.

The notebook is the required presentation surface. Demonstrating the separately planned application is optional and is not a prerequisite for completing the course.

## 4. Repeated notebook format and supporting files

Each notebook uses:

**Situation -> objective -> where it runs -> inputs -> prediction -> small blanks -> evidence -> change one variable -> reflection -> optional extension -> safe reset.**

Use a small number of concept-focused blanks per lesson. Preserve runnable surrounding code, progressive hints, and instructor solutions. Helpers should remove repetitive plumbing, not hide every meaningful Azure SDK call.

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

The organizer-supplied configuration covers existing project/model, Blob destination, Search indexes/connections, KB/MCP references, API version, and optional judge deployment. Agent versions and experiment results belong in a nonsecret workshop manifest, not scattered manual `.env` edits.

Every notebook supports a fresh kernel and explicit artifact loading. No reliance on another notebook's live variables.

Writable artifacts require an explicit participant namespace and ownership record. Enforce namespace/active-version constraints in retrieval configuration, not only in prompts. If the selected managed tool cannot enforce those constraints on a shared index, use an organizer-prepared isolated scope or the explicitly read-only prepared corpus. A classroom namespace or persona filter is not a real authorization boundary.

## 5. Shared artifact contract

Use one small versioned contract for notebook learning outputs. Application-specific request/response schemas and the four tool contracts stay in the companion plan:

| Artifact | Essential fields |
| --- | --- |
| Source | ID, title, publisher, URL, license/status, fictional/real classification, audience, version, update/acquisition date, hash. |
| Chunk | Chunk/document ID, section/page, content, source reference, version, namespace, active status. |
| Retrieval | Query, retrieval mode, KB/source/index reference, actual returned hits/references, optional service score/activity. |
| Agent run | Run/conversation reference, agent name/version, answer, citations, observable tool events, persona, corpus version. |
| Structured-data result | Tool name, validated filters, exact counts/denominators, warnings, dataset/fixture version, snapshot/ETag/hash evidence. |
| Evaluation | Case ID, expected behavior/tool/sources, observed output/context, evaluator version/results, human notes. |
| Workshop checkpoint | Schema version, namespace, resource references, corpus version, active agent versions, output artifact references. |

Sources with uncertain rights remain link-only/excluded. Do not upload original historical patient-level rows to the default KB, prompt context, or evaluation dataset.

Show only observed tool calls, data, and service events. Never fabricate a trace, citation, query decomposition, score, or live-result status.

## 6. Implementation todos and dependencies

The following are future implementation tasks, not work already performed or authorized by saving this plan.

| ID | Todo | Depends on |
| --- | --- | --- |
| `workshop-contract` | Establishing the curriculum/configuration/artifact contract and a small compatible SDK set, reusing the application plan's data/tool rules and prepared instructor-owned resources. | None |
| `workshop-assets` | Authoring fictional fixtures/procedures and approved education text; preparing source/rights manifests and question labels that reference the approved attendance snapshot. | `workshop-contract` |
| `notebook-scaffold` | Creating the shared notebook helpers, lesson template, progressive hints, instructor-solution convention, and fresh-kernel artifact loading. | `workshop-contract` |
| `notebooks-foundations` | Implementing notebooks 00-03: connections, Blob, prompt agents/Agent Service, and bounded tool calling. | `workshop-assets`, `notebook-scaffold` |
| `notebooks-knowledge` | Implementing notebooks 04-05: inspectable Search RAG, two reusable IQ KBs, MCP, and explicit capability boundaries. | `notebooks-foundations` |
| `notebook-framework` | Implementing notebook 06 with the same named/versioned prompt agent through Framework, not a hosted or direct-inference substitute. | `notebooks-knowledge` |
| `evaluation-design` | Finalizing cases, mappings, and evaluator choice with the organizer; implementing notebook 07 after that choice. | `notebook-framework` |
| `notebook-capstone` | Implementing notebook 08 and updating lab navigation/instructor notes around the final course. | `evaluation-design` |
| `workshop-rehearsal` | Rehearsing completed solutions from fresh kernels against supplied Azure resources and checking evidence, replay, and owned-artifact cleanup. | `notebook-capstone` |

Prepared Azure services, the approved Blob snapshot, and compatible bounded tool helpers are external prerequisites supplied by the organizer through the application/Azure workstream. Notebook authors consume those contracts rather than independently provisioning resources or implementing competing metric definitions.

## 7. Completion criteria

- All requested products appear in a coherent story: Blob, Search, prompt agents, Agent Service, Framework, IQ, and evaluation.
- Participants demonstrate at least three distinct tool paths: managed Search, a client-executed read-only function, and a remote KB MCP tool.
- Two KBs are actually referenced and reused; multi-source claims retain distinct citations.
- Each notebook contains meaningful blanks, hints, visible expected artifacts, and a corresponding instructor solution.
- Completed solutions run from clean kernels with explicit state loading; no invisible dependence on previous live notebook sessions.
- Attendance examples use only the approved aggregate-facing historical snapshot; patient examples remain fictional, and education content is attributed and permitted. Raw identifiers are never sent to the agent.
- No provisioning, hosted agents, end-user login, appointment mutation, or clinical decision-making is required. Supplied Azure development authentication is still necessary.
- Live results, saved examples, unavailable features, and failed calls are visibly distinguishable.
- Cleanup touches only owned learning artifacts and never deletes shared indexes, knowledge bases, connections, storage accounts, or resource groups.
- Evaluation comparisons use fixed cases and report limitations; the organizer's final evaluation-product decision is recorded before its implementation is treated as complete.

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

- [Prompt-agent quickstart](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/prompt-agent)
- [Agent Framework integration with Foundry Agent Service](https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/agent-services/foundry)
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

### Evaluation

- [Foundry cloud evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation)
- [Cloud evaluation datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets)
- [Cloud evaluation targets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets)
- [Built-in evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
- [RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
- [Azure AI Evaluation Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-evaluation-readme?view=azure-python)
