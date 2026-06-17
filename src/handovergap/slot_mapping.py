from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from handovergap.schemas import EvidenceEvent


def map_evidence_slots_by_keywords(
    evidence: Iterable[str | Mapping[str, Any] | EvidenceEvent],
    slot_keywords: Mapping[str, Iterable[str]],
) -> list[str]:
    """Map raw evidence snippets to supported slots with deterministic keyword rules.

    This helper is intentionally simple. It is useful for first integrations and tests,
    while LLM-based slot filling remains an optional higher-level path.
    """

    evidence_text = "\n".join(_evidence_text(item) for item in evidence).lower()
    supported_slots = []
    for slot_name, keywords in slot_keywords.items():
        if any(keyword.lower() in evidence_text for keyword in keywords):
            supported_slots.append(slot_name)
    return supported_slots


def _evidence_text(item: str | Mapping[str, Any] | EvidenceEvent) -> str:
    if isinstance(item, EvidenceEvent):
        parts = [item.title or "", item.content]
        parts.extend(str(value) for value in item.metadata.values())
        return "\n".join(parts)
    if isinstance(item, str):
        return item
    parts = [str(item.get("title", "")), str(item.get("content", ""))]
    metadata = item.get("metadata")
    if isinstance(metadata, Mapping):
        parts.extend(str(value) for value in metadata.values())
    return "\n".join(parts)
