# Day 1 - Build the core agentic application

From a chat interface to an agent that can take action.

Start from the running `backend/` + `frontend/` starter, then:

1. Connect to your Foundry project (`.env` already wired in the starter).
2. Review the Patient Assistant in `backend/agents.py`.
3. Add an availability tool (returns synthetic open slots).
4. Add a booking tool (writes an appointment).
5. Register both tools on the agent and test tool calling.
6. Persist appointments in SQLite.
7. Show a basic admin appointment list.

Milestone: a patient can chat with the agent and book one of the valid slots the
backend returns.

Put any guided notebooks for the day in this folder.
