from __future__ import annotations

from typing import Literal

SlotFillMode = Literal["user_provided", "deterministic_rules", "optional_llm"]

SLOT_FILL_MODE_DESCRIPTIONS: dict[SlotFillMode, str] = {
    "user_provided": "Caller supplies already reviewed slots. This is the safest default for production gates.",
    "deterministic_rules": "Caller derives slots with deterministic code, such as keyword or parser rules.",
    "optional_llm": "Caller derives slots with a model. Reports should include model and prompt profile.",
}

EVALUATION_SLOT_PROFILES = ("provided", "conservative", "optimistic")


def mode_for_slot_profile(slot_profile: str) -> SlotFillMode:
    if slot_profile == "provided":
        return "user_provided"
    if slot_profile in {"conservative", "optimistic"}:
        return "optional_llm"
    return "user_provided"


def source_for_slot_profile(slot_profile: str) -> str:
    if slot_profile == "provided":
        return "scenario.provided_slots"
    if slot_profile in {"conservative", "optimistic"}:
        return f"bundled stress profile: {slot_profile}"
    return f"custom slot profile: {slot_profile}"


def validate_slot_fill_mode(mode: str) -> SlotFillMode:
    if mode in SLOT_FILL_MODE_DESCRIPTIONS:
        return mode  # type: ignore[return-value]
    available = ", ".join(SLOT_FILL_MODE_DESCRIPTIONS)
    raise ValueError(f"Invalid slot fill mode '{mode}'. Expected one of: {available}.")
