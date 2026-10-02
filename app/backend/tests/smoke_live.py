"""Smoke-test the running API; never reads configuration files or prints secrets."""
import json
import sys
from collections import Counter
import httpx

with httpx.Client(base_url="http://127.0.0.1:8000", timeout=330) as client:
    health = client.get("/api/health").raise_for_status().json()
    print("Backend configured:", health["configured"], flush=True)
    if not health["configured"]:
        response = client.post("/api/chat/stream", json={"message": "Help me prepare a list of questions for a routine appointment."})
        assert response.status_code == 503
        print("Unconfigured chat correctly returns 503. Live test requires backend configuration.", flush=True)
        sys.exit(2)
    counts = Counter()
    calls = {}
    tasks = {}
    prompt = (
        "Create a short community hand-hygiene briefing. Have the web researcher find current guidance, "
        "the WHO knowledge specialist retrieve relevant WHO guidance, the safety reviewer check caveats, "
        "and the formatter produce three concise bullets with source links. The coordinator should compare "
        "the contributions and preserve any uncertainty. This is general education, not personal medical advice."
    )
    with client.stream("POST", "/api/chat/stream", json={"message": prompt}) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.strip():
                continue
            event = json.loads(line)
            counts[event["type"]] += 1
            if event["type"] == "agents":
                for agent in event["agents"]:
                    print("Foundry agent:", agent["name"], "version", agent["version"], flush=True)
            elif event["type"] == "call":
                call = event["call"]
                calls[call["id"]] = call
                print("Agent call:", call["agent"], call["status"], flush=True)
            elif event["type"] == "task":
                tasks[event["task"]["id"]] = event["task"]
                print("Task:", event["task"]["agent"], event["task"]["status"], flush=True)
            elif event["type"] == "ledger":
                print("Ledger:", event["entry"]["kind"], flush=True)
            elif event["type"] == "agent_delta":
                counts["agent_text_chunks"] += 1
            elif event["type"] == "error":
                print("API error:", event["message"], flush=True)
                sys.exit(1)
            elif event["type"] == "reply":
                assert event["reply"].strip()
                print("Final reply received:", len(event["reply"]), "characters", flush=True)
    assert counts["reply"] == 1 and counts["ledger"] > 0
    assert counts["agent_text_chunks"] > 0
    assert calls and all(call["status"] == "completed" for call in calls.values())
    print("PASS. Events:", dict(counts), "Actual calls:", len(calls), "Tasks:", len(tasks), flush=True)
