#!/usr/bin/env python3
"""Verify the WHO medical knowledge base end to end.

Checks:
  1. Every source PDF produced chunks in the index.
  2. Indexed chunks carry nonempty text and citation metadata.
  3. A question about each document retrieves relevant content from the
     Foundry IQ knowledge base, with usable source references.

Authentication is Microsoft Entra only (DefaultAzureCredential); no keys are
read or printed. Run `az login` first.

    python scripts/medical_kb/06_verify.py
"""

from __future__ import annotations

import sys
from collections import Counter

from azure.core.exceptions import HttpResponseError

from common import Settings, documents_manifest, kb_retrieval_client, load_settings, search_client, search_indexer_client

# Windows consoles often default to a legacy codepage (e.g. cp1252) that can't
# encode characters PDFs and model answers commonly contain (>=, en dashes,
# etc). Force UTF-8 output so a print statement never crashes the report.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUESTIONS = {
    "who-hearts-d-diabetes.pdf": "What HbA1c and fasting plasma glucose thresholds does WHO use to diagnose type 2 diabetes, and which medicine is first-line treatment?",
    "who-hypertension-pharmacological-treatment.pdf": "At what blood pressure level does WHO recommend starting pharmacological treatment for hypertension in adults, and which drug classes are recommended as first-line?",
    "who-ipc-core-components.pdf": "What are the core components of infection prevention and control programmes that WHO recommends at the acute health care facility level?",
}

CHUNK_SELECT_FIELDS = [
    "chunk_id",
    "chunk",
    "document_title",
    "source_url",
    "publisher",
    "publication_id",
    "topic",
    "license",
    "license_url",
    "citation",
]

failures: list[str] = []


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    failures.append(msg)


def check_indexer(settings: Settings, documents: list[dict]) -> None:
    print("\n[1] indexer run")
    status = search_indexer_client(settings).get_indexer_status(settings.indexer)
    last = status.last_result
    if last is None:
        fail("indexer has never run")
        return
    print(
        f"  status={last.status.value} processed={last.item_count} "
        f"failed={last.failed_item_count} warnings={len(last.warnings or [])}"
    )
    if last.status != "success":
        fail(f"indexer status is {last.status.value}")
    if last.failed_item_count:
        fail(f"{last.failed_item_count} items failed")
    if last.item_count < len(documents):
        fail(f"expected {len(documents)} documents, processed {last.item_count}")


def check_chunks(settings: Settings, documents: list[dict]) -> None:
    print("\n[2] indexed chunks per document")
    client = search_client(settings)
    for doc in documents:
        name = doc["file"]
        results = client.search(
            search_text="*",
            filter=f"metadata_storage_name eq '{name}'",
            include_total_count=True,
            top=3,
            select=CHUNK_SELECT_FIELDS,
        )
        rows = list(results)
        total = results.get_count()
        if not total:
            fail(f"{name}: no chunks indexed")
            continue

        empty = [row for row in rows if not (row.get("chunk") or "").strip()]
        lengths = [len(row.get("chunk") or "") for row in rows]
        top = rows[0]
        print(f"  {name}: {total} chunks, sample lengths {lengths}")
        print(f"      title      : {top.get('document_title')}")
        print(f"      source_url : {top.get('source_url')}")
        print(f"      topic      : {top.get('topic')} | id: {top.get('publication_id')}")
        print(f"      license    : {top.get('license')}")
        print(f"      text       : {(top.get('chunk') or '')[:120].strip()!r}")

        if empty:
            fail(f"{name}: {len(empty)} sampled chunks have empty text")
        if top.get("source_url") != doc["source_url"]:
            fail(f"{name}: source_url mismatch ({top.get('source_url')})")
        if top.get("document_title") != doc["document_title"]:
            fail(f"{name}: document_title mismatch")
        if top.get("license") != doc["license"]:
            fail(f"{name}: license mismatch ({top.get('license')})")
        if not (top.get("citation") or "").strip():
            fail(f"{name}: citation is empty, attribution would be lost")


def check_retrieval(settings: Settings, documents: list[dict]) -> None:
    print("\n[3] knowledge base retrieval")
    client = kb_retrieval_client(settings)
    for doc in documents:
        question = QUESTIONS[doc["file"]]
        print(f"\n  Q ({doc['topic']}): {question}")

        request = {
            "messages": [{"role": "user", "content": [{"type": "text", "text": question}]}],
            "includeActivity": True,
            "outputMode": "answerSynthesis",
            "maxOutputDocuments": 20,
            "maxRuntimeInSeconds": 120,
            "knowledgeSourceParams": [
                {
                    "kind": "searchIndex",
                    "knowledgeSourceName": settings.knowledge_source,
                    "includeReferences": True,
                    "includeReferenceSourceData": True,
                }
            ],
        }
        try:
            result = client.retrieve(request)
        except HttpResponseError as exc:
            fail(f"{doc['file']}: retrieve failed: {exc.message}")
            continue

        answer = "".join(
            (getattr(part, "text", None) or "")
            for message in (result.response or [])
            for part in (message.content or [])
        )
        refs = result.references or []
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

        cited_count: Counter[str] = Counter()
        cited_url: dict[str, str] = {}
        for ref in refs:
            source_data = ref.source_data or {}
            title = source_data.get("document_title")
            if not title:
                continue
            cited_count[title] += 1
            cited_url.setdefault(title, source_data.get("source_url") or "")
        for title, count in cited_count.most_common():
            print(f"      - {title}  ({count} refs)")
            print(f"        {cited_url[title]}")

        if not any(cited_url.values()):
            fail(f"{doc['file']}: references carry no source_url")
        if doc["document_title"] not in cited_count:
            fail(f"{doc['file']}: expected document not among cited titles {sorted(cited_count)}")


def main() -> None:
    settings = load_settings()
    documents = documents_manifest()

    check_indexer(settings, documents)
    check_chunks(settings, documents)
    check_retrieval(settings, documents)

    print("\n" + "=" * 70)
    if failures:
        print(f"FAILED ({len(failures)}):")
        for msg in failures:
            print(f"  - {msg}")
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
