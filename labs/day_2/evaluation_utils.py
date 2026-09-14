"""Deterministic helpers shared by the live RAG evaluation labs."""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable, Mapping


_EVIDENCE_FIELDS = (
    "chunk_id",
    "parent_id",
    "publication_id",
    "metadata_storage_name",
    "document_title",
    "topic",
    "source_url",
)


def find_repo_root(start: Path | None = None) -> Path:
    """Find the workshop root from a notebook or terminal working directory."""
    current = (start or Path.cwd()).resolve()
    for folder in (current, *current.parents):
        if (folder / "README.md").is_file() and (folder / "labs").is_dir():
            return folder
    raise FileNotFoundError("Workshop repository root not found")


def load_cases(path: Path, target: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load and validate benchmark rows for one retrieval target."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0":
        raise ValueError("Unsupported medical RAG dataset schema")
    if payload.get("answer_contract_version") != "medical-required-parts-v1":
        raise ValueError("Unsupported medical answer contract")

    cases = [row for row in payload.get("cases", []) if row.get("target") == target]
    if not cases:
        raise ValueError(f"No evaluation cases found for target {target!r}")
    case_ids = [str(row.get("case_id", "")).strip() for row in cases]
    if not all(case_ids) or len(case_ids) != len(set(case_ids)):
        raise ValueError("Every evaluation case needs a unique non-empty case_id")

    filter_name = {
        "azure_ai_search": "search_filter",
        "foundry_iq": "knowledge_source_filter",
    }.get(target)
    if filter_name is None:
        raise ValueError(f"Unsupported retrieval target {target!r}")

    for row in cases:
        required = (
            "query",
            "ground_truth",
            "required_answer_parts",
            "expected_evidence_groups",
            "required_context_signals",
            filter_name,
        )
        missing = [name for name in required if not row.get(name)]
        if missing:
            raise ValueError(f"{row['case_id']}: missing {', '.join(missing)}")
        part_ids = [str(part.get("id", "")).strip() for part in row["required_answer_parts"]]
        if not all(part_ids) or len(part_ids) != len(set(part_ids)):
            raise ValueError(f"{row['case_id']}: answer-part IDs must be unique and non-empty")
        if not all(group.get("any_of") for group in row["expected_evidence_groups"]):
            raise ValueError(f"{row['case_id']}: every evidence group needs alternatives")
        if not all(group.get("any_of") for group in row["required_context_signals"]):
            raise ValueError(f"{row['case_id']}: every context signal needs alternatives")
    return payload, cases


def _normalize(value: Any) -> str:
    return str(value).strip().casefold()


def document_evidence_keys(document: Mapping[str, Any]) -> set[str]:
    """Return stable medical-index identifiers for one retrieved document."""
    return {
        _normalize(document[field])
        for field in _EVIDENCE_FIELDS
        if document.get(field) not in (None, "")
    }


def retrieval_recall(
    expected_groups: Iterable[Mapping[str, Any]],
    retrieved_keys: Iterable[str],
) -> dict[str, Any]:
    """Compute evidence-group recall, allowing equivalent IDs per group."""
    keys = {_normalize(value) for value in retrieved_keys}
    details = []
    for group in expected_groups:
        alternatives = {_normalize(value) for value in group["any_of"]}
        matches = sorted(alternatives & keys)
        details.append(
            {
                "name": str(group.get("name", "evidence")),
                "matched": bool(matches),
                "matched_keys": matches,
            }
        )
    matched = sum(int(item["matched"]) for item in details)
    return {
        "recall": matched / len(details) if details else 1.0,
        "matched_groups": matched,
        "total_groups": len(details),
        "groups": details,
    }


def context_signal_coverage(
    expected_signals: Iterable[Mapping[str, Any]],
    context: str,
) -> dict[str, Any]:
    """Check whether the frozen context contains each predeclared evidence signal."""
    normalized_context = _normalize(context)
    details = []
    for signal in expected_signals:
        matches = [
            str(value)
            for value in signal["any_of"]
            if _normalize(value) in normalized_context
        ]
        details.append(
            {
                "id": str(signal.get("id", "signal")),
                "matched": bool(matches),
                "matched_values": matches,
            }
        )
    matched = sum(int(item["matched"]) for item in details)
    return {
        "coverage": matched / len(details) if details else 1.0,
        "matched_signals": matched,
        "total_signals": len(details),
        "signals": details,
    }


def ranked_evidence_metrics(
    expected_groups: Iterable[Mapping[str, Any]],
    documents: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Measure expected-document precision and first-match rank."""
    expected = {
        _normalize(value)
        for group in expected_groups
        for value in group.get("any_of", [])
    }
    ranked = list(documents)
    matches = [bool(document_evidence_keys(document) & expected) for document in ranked]
    first_match_rank = next(
        (rank for rank, matched in enumerate(matches, start=1) if matched),
        None,
    )
    return {
        "precision": sum(matches) / len(matches) if matches else 0.0,
        "top_1_match": bool(matches and matches[0]),
        "first_match_rank": first_match_rank,
        "reciprocal_rank": 1.0 / first_match_rank if first_match_rank else 0.0,
        "matched_ranks": [
            rank for rank, matched in enumerate(matches, start=1) if matched
        ],
    }


def format_search_context(documents: Iterable[Mapping[str, Any]]) -> str:
    """Label direct Search results with stable IDs for answer generation."""
    blocks = []
    for index, document in enumerate(documents, start=1):
        blocks.append(
            f"[S{index}] {document.get('document_title', 'WHO guideline')}\n"
            f"publication_id: {document.get('publication_id', '')}\n"
            f"topic: {document.get('topic', '')}\n"
            f"source_url: {document.get('source_url', '')}\n"
            f"content: {document.get('chunk', '')}"
        )
    return "\n\n".join(blocks)


def _normalize_citation(value: Any) -> str:
    citation = _normalize(value).removeprefix("[").removesuffix("]")
    return f"ref_id:{citation}" if citation.isdigit() else citation


def validate_cited_answer(
    value: Mapping[str, Any],
    valid_source_ids: Iterable[str],
    required_answer_part_ids: Iterable[str],
) -> dict[str, Any]:
    """Validate strict claim citations and required-answer-part accounting."""
    valid = {_normalize_citation(value) for value in valid_source_ids}
    required = [str(value).strip() for value in required_answer_part_ids]
    if not required or not all(required) or len(required) != len(set(required)):
        raise ValueError("Required answer-part IDs must be unique and non-empty")
    required_set = set(required)

    raw_claims = value.get("claims")
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ValueError("A cited answer needs at least one claim")
    raw_insufficient = value.get("insufficient_evidence", [])
    if not isinstance(raw_insufficient, list) or not all(
        isinstance(item, str) for item in raw_insufficient
    ):
        raise ValueError("insufficient_evidence must be an array of answer-part IDs")
    insufficient = [item.strip() for item in raw_insufficient]
    if len(insufficient) != len(set(insufficient)):
        raise ValueError("insufficient_evidence must not contain duplicates")
    unknown_insufficient = sorted(set(insufficient) - required_set)
    if unknown_insufficient:
        raise ValueError(
            "Unknown insufficient answer-part IDs: " + ", ".join(unknown_insufficient)
        )

    claims = []
    answered: set[str] = set()
    all_citations: list[str] = []
    invalid_citations: list[str] = []
    cited_claims = 0
    validly_cited_claims = 0
    for index, raw_claim in enumerate(raw_claims, start=1):
        if not isinstance(raw_claim, Mapping):
            raise ValueError("Every claim must be an object")
        part_id = str(raw_claim.get("answer_part_id", "")).strip()
        text = str(raw_claim.get("text", "")).strip()
        source_ids = raw_claim.get("source_ids")
        if part_id not in required_set:
            raise ValueError(f"Unknown claim answer_part_id: {part_id!r}")
        if not text or not isinstance(source_ids, list) or not source_ids:
            raise ValueError("Every claim needs text and at least one source_id")

        citations = [_normalize_citation(source_id) for source_id in source_ids]
        unresolved = [citation for citation in citations if citation not in valid]
        cited_claims += 1
        if not unresolved:
            validly_cited_claims += 1
        all_citations.extend(citations)
        invalid_citations.extend(unresolved)
        answered.add(part_id)
        claims.append(
            {
                "claim_number": index,
                "answer_part_id": part_id,
                "text": text,
                "citation_ids": citations,
                "invalid_citation_ids": unresolved,
            }
        )

    overlap = sorted(answered & set(insufficient))
    if overlap:
        raise ValueError("Answer parts cannot be answered and insufficient: " + ", ".join(overlap))
    unaccounted = sorted(required_set - answered - set(insufficient))
    if unaccounted:
        raise ValueError("Required answer parts are unaccounted for: " + ", ".join(unaccounted))

    return {
        "claims": claims,
        "required_answer_part_ids": required,
        "answered_answer_part_ids": [part_id for part_id in required if part_id in answered],
        "insufficient_evidence": insufficient,
        "answer_part_coverage": len(answered) / len(required),
        "citation_coverage": cited_claims / len(claims),
        "citation_validity": (
            (len(all_citations) - len(invalid_citations)) / len(all_citations)
            if all_citations
            else 0.0
        ),
        "valid_citation_coverage": validly_cited_claims / len(claims),
        "invalid_citations": sorted(set(invalid_citations)),
    }


def render_cited_answer(validation: Mapping[str, Any]) -> str:
    """Render validated structured claims with visible source IDs."""
    lines = []
    for claim in validation["claims"]:
        citations = " ".join(
            f"[{citation.upper() if re.fullmatch(r's\d+', citation) else citation}]"
            for citation in claim["citation_ids"]
        )
        lines.append(f"- {claim['text']} {citations}")
    return "\n".join(lines)


def answer_json_schema(
    required_answer_part_ids: Iterable[str],
    valid_source_ids: Iterable[str],
) -> dict[str, Any]:
    """Build the strict JSON schema used by both live generation paths."""
    part_ids = list(required_answer_part_ids)
    source_ids = list(valid_source_ids)
    return {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "answer_part_id": {"type": "string", "enum": part_ids},
                        "text": {"type": "string"},
                        "source_ids": {
                            "type": "array",
                            "items": {"type": "string", "enum": source_ids},
                        },
                    },
                    "required": ["answer_part_id", "text", "source_ids"],
                    "additionalProperties": False,
                },
            },
            "insufficient_evidence": {
                "type": "array",
                "items": {"type": "string", "enum": part_ids},
            },
        },
        "required": ["claims", "insufficient_evidence"],
        "additionalProperties": False,
    }


def _iq_text_blocks(payload: Mapping[str, Any]) -> list[str]:
    blocks = []
    for message in payload.get("response") or []:
        for content in message.get("content") or []:
            if content.get("type") == "text" and content.get("text"):
                blocks.append(str(content["text"]))
    return blocks


def extract_iq_documents(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Decode the serialized document array from IQ extractiveData output."""
    documents = []
    for text in _iq_text_blocks(payload):
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Foundry IQ extractiveData was not valid JSON") from exc
        if isinstance(decoded, Mapping):
            decoded = decoded.get("documents") or decoded.get("value") or [decoded]
        if not isinstance(decoded, list) or not all(isinstance(item, Mapping) for item in decoded):
            raise ValueError("Foundry IQ extractiveData must be a document array")
        documents.extend(dict(item) for item in decoded)
    if not all(str(document.get("ref_id", "")).strip() for document in documents):
        raise ValueError("Every extracted IQ document needs a ref_id")
    return documents


def resolve_iq_references(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Join IQ references to extracted or inline source data."""
    extracted = {
        _normalize(document["ref_id"]): document
        for document in extract_iq_documents(payload)
    }
    activities = {
        str(activity.get("id")): activity
        for activity in payload.get("activity") or []
        if activity.get("type") == "searchIndex"
    }
    resolved = []
    for reference in payload.get("references") or []:
        if reference.get("type") != "searchIndex":
            continue
        ref_id = str(reference.get("id", "")).strip()
        source_data = reference.get("sourceData")
        document = dict(extracted.get(_normalize(ref_id), {}))
        if isinstance(source_data, Mapping):
            document = {**dict(source_data), **document}
        if not document:
            raise ValueError(f"Reference {ref_id!r} has no extractive or inline source data")
        activity = activities.get(str(reference.get("activitySource")), {})
        resolved.append(
            {
                "ref_id": ref_id,
                "doc_key": str(reference.get("docKey", "")),
                "source_name": str(activity.get("knowledgeSourceName", "")),
                "reranker_score": reference.get("rerankerScore"),
                "document": document,
            }
        )
    return resolved


def format_iq_context(references: Iterable[Mapping[str, Any]]) -> str:
    """Format the exact IQ evidence with its returned reference IDs."""
    blocks = []
    for reference in references:
        document = reference["document"]
        fields = [
            f"{field}: {document[field]}"
            for field in _EVIDENCE_FIELDS + ("chunk", "content")
            if document.get(field) not in (None, "")
        ]
        blocks.append(
            f"[ref_id:{reference['ref_id']}] {document.get('document_title', 'WHO guideline')}\n"
            + "\n".join(fields)
        )
    return "\n\n".join(blocks)


def response_token_usage(response: Any, semantic_requests: int = 0) -> dict[str, int]:
    """Extract observable token usage from an OpenAI Responses object."""
    usage = getattr(response, "usage", None)
    return {
        "model_input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "model_output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "agentic_retrieval_tokens": 0,
        "semantic_requests": int(semantic_requests),
    }


def iq_activity_metrics(activity: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Aggregate model, retrieval, and latency telemetry from IQ activity."""
    metrics = {
        "model_input_tokens": 0,
        "model_output_tokens": 0,
        "agentic_retrieval_tokens": 0,
        "semantic_requests": 0,
        "query_planning_ms": 0,
        "search_execution_ms": 0,
        "answer_synthesis_ms": 0,
    }
    for item in activity:
        item_type = item.get("type")
        if item_type in {"modelQueryPlanning", "modelAnswerSynthesis"}:
            metrics["model_input_tokens"] += int(item.get("inputTokens", 0) or 0)
            metrics["model_output_tokens"] += int(item.get("outputTokens", 0) or 0)
        if item_type == "modelQueryPlanning":
            metrics["query_planning_ms"] += int(item.get("elapsedMs", 0) or 0)
        elif item_type == "modelAnswerSynthesis":
            metrics["answer_synthesis_ms"] += int(item.get("elapsedMs", 0) or 0)
        elif item_type == "searchIndex":
            metrics["semantic_requests"] += 1
            metrics["search_execution_ms"] += int(item.get("elapsedMs", 0) or 0)
        elif item_type == "agenticReasoning":
            metrics["agentic_retrieval_tokens"] += int(item.get("reasoningTokens", 0) or 0)
    return metrics


def price_rates_from_env() -> dict[str, float | None]:
    """Read optional contract-specific rates without hard-coding prices."""
    names = {
        "model_input_per_1m": "RAG_MODEL_INPUT_USD_PER_1M_TOKENS",
        "model_output_per_1m": "RAG_MODEL_OUTPUT_USD_PER_1M_TOKENS",
        "semantic_per_1k": "RAG_SEMANTIC_RANKER_USD_PER_1000_REQUESTS",
        "agentic_per_1m": "RAG_AGENTIC_RETRIEVAL_USD_PER_1M_TOKENS",
    }
    rates = {}
    for key, variable in names.items():
        raw = os.getenv(variable, "").strip()
        rates[key] = float(raw) if raw else None
    return rates


def estimate_cost_usd(
    usage: Mapping[str, int],
    rates: Mapping[str, float | None],
) -> dict[str, Any]:
    """Estimate request cost only from rates explicitly supplied by the user."""
    inputs = {
        "model_input": (usage.get("model_input_tokens", 0), rates.get("model_input_per_1m"), 1_000_000),
        "model_output": (usage.get("model_output_tokens", 0), rates.get("model_output_per_1m"), 1_000_000),
        "semantic_ranker": (usage.get("semantic_requests", 0), rates.get("semantic_per_1k"), 1_000),
        "agentic_retrieval": (usage.get("agentic_retrieval_tokens", 0), rates.get("agentic_per_1m"), 1_000_000),
    }
    components = {
        name: round(float(quantity) * float(rate) / divisor, 8) if rate is not None else None
        for name, (quantity, rate, divisor) in inputs.items()
    }
    configured = [value for value in components.values() if value is not None]
    return {
        "estimated_cost_usd": round(sum(configured), 8) if configured else None,
        "components_usd": components,
        "rates_complete": all(rate is not None for rate in rates.values()),
    }


def percentile_95(values: Iterable[float]) -> float:
    """Return the nearest-rank p95 used in the repeated IQ report."""
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("percentile_95 needs at least one value")
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def primitive(value: Any) -> Any:
    """Convert Azure and OpenAI SDK models to JSON-compatible values."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "as_dict"):
        return value.as_dict()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value
