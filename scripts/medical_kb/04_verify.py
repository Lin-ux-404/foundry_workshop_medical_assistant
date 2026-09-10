#!/usr/bin/env python3
"""Verify the WHO medical knowledge base end to end.

Checks:
  1. Every source PDF produced chunks in the index.
  2. Indexed chunks carry nonempty text and citation metadata.
  3. A question about each document retrieves relevant content from the
     Foundry IQ knowledge base, with usable source references.

Authentication is Microsoft Entra only (DefaultAzureCredential); no keys are
read or printed. Run `az login` first.

    python scripts/medical_kb/04_verify.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from azure.identity import DefaultAzureCredential

HERE = Path(__file__).resolve().parent

SEARCH_SERVICE = os.getenv("SEARCH_SERVICE", "umc-hackathon-devbox-fiq-search")
ENDPOINT = os.getenv("SEARCH_ENDPOINT", f"https://{SEARCH_SERVICE}.search.windows.net")
API_VERSION = os.getenv("SEARCH_API_VERSION", "2026-08-01-preview")
INDEX = os.getenv("SEARCH_INDEX", "who-guidelines-index")
INDEXER = os.getenv("INDEXER", "who-guidelines-indexer")
KNOWLEDGE_BASE = os.getenv("KNOWLEDGE_BASE", "umc-medical-kb")
KNOWLEDGE_SOURCE = os.getenv("KNOWLEDGE_SOURCE", "who-guidelines-ks")

QUESTIONS = {
    "who-hearts-d-diabetes.pdf": "What HbA1c and fasting plasma glucose thresholds does WHO use to diagnose type 2 diabetes, and which medicine is first-line treatment?",
    "who-hypertension-pharmacological-treatment.pdf": "At what blood pressure level does WHO recommend starting pharmacological treatment for hypertension in adults, and which drug classes are recommended as first-line?",
    "who-ipc-core-components.pdf": "What are the core components of infection prevention and control programmes that WHO recommends at the acute health care facility level?",
}

_credential = DefaultAzureCredential()


def token() -> str:
    return _credential.get_token("https://search.azure.com/.default").token


def call(method: str, path: str, body: dict | None = None) -> requests.Response:
    return requests.request(
        method,
        f"{ENDPOINT}{path}",
        params={"api-version": API_VERSION},
        headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"},
        json=body,
        timeout=180,
    )


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    failures.append(msg)


failures: list[str] = []
documents = json.loads((HERE / "documents.json").read_text())


def check_indexer() -> None:
    print("\n[1] indexer run")
    r = call("GET", f"/indexers/{INDEXER}/status")
    r.raise_for_status()
    last = r.json()["lastResult"]
    print(f"  status={last['status']} processed={last['itemsProcessed']} "
          f"failed={last['itemsFailed']} warnings={len(last.get('warnings') or [])}")
    if last["status"] != "success":
        fail(f"indexer status is {last['status']}")
    if last["itemsFailed"]:
        fail(f"{last['itemsFailed']} items failed")
    if last["itemsProcessed"] < len(documents):
        fail(f"expected {len(documents)} documents, processed {last['itemsProcessed']}")


def check_chunks() -> None:
    print("\n[2] indexed chunks per document")
    for doc in documents:
        name = doc["file"]
        r = call("POST", f"/indexes/{INDEX}/docs/search", {
            "search": "*",
            "filter": f"metadata_storage_name eq '{name}'",
            "count": True,
            "top": 3,
            "select": "chunk_id,chunk,document_title,source_url,publisher,publication_id,topic",
        })
        r.raise_for_status()
        data = r.json()
        total = data["@odata.count"]
        rows = data["value"]
        if total == 0:
            fail(f"{name}: no chunks indexed")
            continue
        empty = [x for x in rows if not (x.get("chunk") or "").strip()]
        lengths = [len(x.get("chunk") or "") for x in rows]
        top = rows[0]
        print(f"  {name}: {total} chunks, sample lengths {lengths}")
        print(f"      title      : {top.get('document_title')}")
        print(f"      source_url : {top.get('source_url')}")
        print(f"      topic      : {top.get('topic')} | id: {top.get('publication_id')}")
        print(f"      text       : {(top.get('chunk') or '')[:120].strip()!r}")
        if empty:
            fail(f"{name}: {len(empty)} sampled chunks have empty text")
        if top.get("source_url") != doc["source_url"]:
            fail(f"{name}: source_url mismatch ({top.get('source_url')})")
        if top.get("document_title") != doc["document_title"]:
            fail(f"{name}: document_title mismatch")


def check_retrieval() -> None:
    print("\n[3] knowledge base retrieval")
    for doc in documents:
        question = QUESTIONS[doc["file"]]
        print(f"\n  Q ({doc['topic']}): {question}")
        r = call("POST", f"/knowledgebases/{KNOWLEDGE_BASE}/retrieve", {
            "messages": [{"role": "user", "content": [{"type": "text", "text": question}]}],
            "includeActivity": True,
            "outputMode": "answerSynthesis",
            "maxOutputDocuments": 20,
            "maxRuntimeInSeconds": 120,
            "knowledgeSourceParams": [{
                "kind": "searchIndex",
                "knowledgeSourceName": KNOWLEDGE_SOURCE,
                "includeReferences": True,
                "includeReferenceSourceData": True,
            }],
        })
        if r.status_code not in (200, 206):
            fail(f"{doc['file']}: retrieve returned HTTP {r.status_code}: {r.text[:400]}")
            continue
        payload = r.json()
        answer = "".join(
            part.get("text", "")
            for msg in payload.get("response") or []
            for part in msg.get("content") or []
        )
        refs = payload.get("references") or []
        words = len(answer.split())
        print(f"  A ({words} words): {answer.strip()}")
        print(f"  references: {len(refs)}")
        if words > 160:
            fail(f"{doc['file']}: answer is {words} words, expected a concise answer")
        if not answer.strip():
            fail(f"{doc['file']}: empty answer")
        if not refs:
            fail(f"{doc['file']}: no references returned")
            continue

        cited: dict[str, tuple[str, int]] = {}
        for ref in refs:
            sd = ref.get("sourceData") or {}
            title = sd.get("document_title")
            if not title:
                continue
            url, count = cited.get(title, (sd.get("source_url") or "", 0))
            cited[title] = (url or (sd.get("source_url") or ""), count + 1)
        for title, (url, count) in sorted(cited.items(), key=lambda kv: -kv[1][1]):
            print(f"      - {title}  ({count} refs)")
            print(f"        {url}")

        titles = set(cited)
        urls = {u for u, _ in cited.values() if u}
        if not urls:
            fail(f"{doc['file']}: references carry no source_url")
        if doc["document_title"] not in titles:
            fail(f"{doc['file']}: expected document not among cited titles {sorted(titles)}")


check_indexer()
check_chunks()
check_retrieval()

print("\n" + "=" * 70)
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("All checks passed.")
