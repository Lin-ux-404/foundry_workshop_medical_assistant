# Microsoft Foundry workshop

Three days of small, self-contained notebook lessons. The focus is Foundry and
its technologies, not building a medical application.

| Day | Topics | Plan |
| --- | --- | --- |
| 1 | Model deployment, prompt agents, AI Search, Agent Framework orchestration | [Day 1 notebooks](day_1/README.md) |
| 2 | Foundry IQ, knowledge bases, MCP | [Day 2](day_2/README.md) |
| 3 | Out of scope here; covered elsewhere | [Day 3](day_3/README.md) |

See the [curriculum](../docs/notebook-workshop-plan.md) for activities and learning
outcomes. **Five notebooks are implemented: Labs 1 to 4 on Day 1, and Lab 5 on
Day 2.** Evaluation, fine-tuning, tool calling and guardrails are covered
elsewhere, so Labs 6, 7 and 8 are empty placeholder files.

## How the notebooks work

Each lesson carries its own package setup, configuration, authentication,
example data, SDK calls, exercises and hints. Read the concept, complete a
**To-Do**, then run the deterministic check that proves what you built.
The notebooks use marked `...` code blanks with hints and collapsible
solutions; they are not a sequence of finished examples to run unchanged.

You need your own Azure subscription and a Foundry project. Each notebook lists
its own prerequisites and cleans up what it creates. Examples use a small
fictional orders API, not real patient data. The app in this repository is not
a dependency.
