from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from yaml import YAMLError

from handovergap.slot_rules import GAP_TYPE_BY_SLOT, HIGH_RISK_SLOTS, PROFILE_REQUIRED_SLOTS, QUESTION_BY_SLOT

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH"}


class SlotPolicy(BaseModel):
    slot_name: str
    description: str | None = None
    question: str | None = None
    gap_type: str | None = None
    severity: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    high_risk: bool = False


class ProfileDefinition(BaseModel):
    profile: str
    required_slots: list[SlotPolicy] = Field(min_length=1)


class ProfileValidationResult(BaseModel):
    path: str
    profiles: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


class ProfileCatalog:
    def __init__(self, profiles: list[ProfileDefinition]):
        self._profiles = {profile.profile: profile for profile in profiles}

    @classmethod
    def builtins(cls) -> ProfileCatalog:
        profiles = []
        for profile, slots in PROFILE_REQUIRED_SLOTS.items():
            profiles.append(
                ProfileDefinition(
                    profile=profile,
                    required_slots=[
                        SlotPolicy(
                            slot_name=slot,
                            description=_default_description(slot),
                            question=QUESTION_BY_SLOT.get(slot),
                            gap_type=GAP_TYPE_BY_SLOT.get(slot, f"{slot}_gap"),
                            severity="HIGH" if slot in HIGH_RISK_SLOTS else "MEDIUM",
                            high_risk=slot in HIGH_RISK_SLOTS,
                        )
                        for slot in slots
                    ],
                )
            )
        return cls(profiles)

    @classmethod
    def from_yaml(cls, path: str | Path) -> ProfileCatalog:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("YAML profile loading requires PyYAML. Install handovergap with the default dependencies.") from exc

        payload = yaml.safe_load(Path(path).read_text()) or {}
        raw_profiles = payload.get("profiles", payload)
        if isinstance(raw_profiles, dict):
            profiles = [
                _profile_from_mapping(profile_name, profile_payload)
                for profile_name, profile_payload in raw_profiles.items()
            ]
        else:
            profiles = [ProfileDefinition.model_validate(item) for item in raw_profiles]
        return cls(profiles)

    def names(self) -> list[str]:
        return list(self._profiles)

    def get(self, profile: str) -> ProfileDefinition:
        try:
            return self._profiles[profile]
        except KeyError as exc:
            available = ", ".join(self.names())
            raise ValueError(
                f"Unknown profile '{profile}'. Available profiles: {available}. "
                "Use `handovergap profiles validate <path>` before passing a custom profile file."
            ) from exc

    def required_slots(self, profile: str) -> list[str]:
        return [slot.slot_name for slot in self.get(profile).required_slots]

    def slot_policy(self, profile: str, slot_name: str) -> SlotPolicy:
        definition = self.get(profile)
        for slot in definition.required_slots:
            if slot.slot_name == slot_name:
                return slot
        available = ", ".join(slot.slot_name for slot in definition.required_slots)
        raise ValueError(f"Unknown slot '{slot_name}' for profile '{profile}'. Available slots: {available}.")


def _profile_from_mapping(profile_name: str, payload: object) -> ProfileDefinition:
    if not isinstance(payload, dict):
        raise ValueError(f"Profile '{profile_name}' must be an object.")
    data = {"profile": profile_name, **payload}
    return ProfileDefinition.model_validate(data)


def validate_profile_file(path: str | Path) -> ProfileValidationResult:
    profile_path = Path(path)
    errors: list[str] = []
    profiles: list[str] = []

    try:
        import yaml
    except ImportError as exc:
        return ProfileValidationResult(
            path=str(profile_path),
            errors=[f"{profile_path}: YAML profile validation requires PyYAML: {exc}"],
        )

    try:
        raw_text = profile_path.read_text()
    except OSError as exc:
        return ProfileValidationResult(path=str(profile_path), errors=[f"{profile_path}: cannot read file: {exc}"])

    try:
        payload = yaml.safe_load(raw_text)
    except YAMLError as exc:
        return ProfileValidationResult(path=str(profile_path), errors=[f"{profile_path}: invalid YAML: {exc}"])

    if payload is None:
        return ProfileValidationResult(path=str(profile_path), errors=[f"{profile_path}: file is empty"])
    if not isinstance(payload, dict):
        return ProfileValidationResult(path=str(profile_path), errors=[f"{profile_path}: top-level YAML must be an object"])

    raw_profiles = payload.get("profiles", payload)
    normalized_profiles = _normalize_profiles(raw_profiles, errors)
    for profile_name, profile_payload in normalized_profiles:
        profiles.append(profile_name)
        _validate_profile_payload(profile_path, profile_name, profile_payload, errors)

    if len(profiles) != len(set(profiles)):
        duplicates = sorted({profile for profile in profiles if profiles.count(profile) > 1})
        errors.append(f"{profile_path}: duplicate profile names: {', '.join(duplicates)}")

    if not errors:
        try:
            ProfileCatalog.from_yaml(profile_path)
        except Exception as exc:
            errors.append(f"{profile_path}: profile catalog failed to load: {exc}")

    return ProfileValidationResult(path=str(profile_path), profiles=profiles, errors=errors)


def _normalize_profiles(raw_profiles: object, errors: list[str]) -> list[tuple[str, object]]:
    if isinstance(raw_profiles, dict):
        return [(str(profile_name), profile_payload) for profile_name, profile_payload in raw_profiles.items()]
    if isinstance(raw_profiles, list):
        normalized = []
        for index, item in enumerate(raw_profiles):
            if not isinstance(item, dict):
                errors.append(f"profiles[{index}]: profile entry must be an object")
                continue
            profile_name = item.get("profile")
            if not isinstance(profile_name, str) or not profile_name.strip():
                errors.append(f"profiles[{index}]: missing required key 'profile'")
                continue
            normalized.append((profile_name, item))
        return normalized
    errors.append("profiles: must be an object or a list")
    return []


def _validate_profile_payload(path: Path, profile_name: str, payload: object, errors: list[str]) -> None:
    context = f"{path}: profile '{profile_name}'"
    if not isinstance(payload, dict):
        errors.append(f"{context}: profile payload must be an object")
        return

    required_slots = payload.get("required_slots")
    if "required_slots" not in payload:
        errors.append(f"{context}: missing required key 'required_slots'")
        return
    if not isinstance(required_slots, list) or not required_slots:
        errors.append(f"{context}: required_slots must be a non-empty list")
        return

    slot_names: list[str] = []
    for index, slot_payload in enumerate(required_slots):
        slot_context = f"{context}: required_slots[{index}]"
        if not isinstance(slot_payload, dict):
            errors.append(f"{slot_context}: slot must be an object")
            continue

        slot_name = slot_payload.get("slot_name")
        if not isinstance(slot_name, str) or not slot_name.strip():
            errors.append(f"{slot_context}: missing required key 'slot_name'")
        else:
            slot_names.append(slot_name)
            slot_context = f"{context}: slot '{slot_name}'"

        question = slot_payload.get("question")
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{slot_context}: missing required key 'question'")

        severity = slot_payload.get("severity", "MEDIUM")
        if severity not in VALID_SEVERITIES:
            errors.append(f"{slot_context}: severity must be one of LOW, MEDIUM, HIGH")

        high_risk = slot_payload.get("high_risk", False)
        if not isinstance(high_risk, bool):
            errors.append(f"{slot_context}: high_risk must be true or false")

    duplicates = sorted({slot_name for slot_name in slot_names if slot_names.count(slot_name) > 1})
    for slot_name in duplicates:
        errors.append(f"{context}: duplicate slot_name '{slot_name}'")


def _default_description(slot: str) -> str:
    descriptions = {
        "scope": "このプロファイルが適用範囲を判断するための情報が不足しています",
        "communication_status": "関係者または顧客に説明済みか不明です",
        "authority": "このプロファイルが回答または判断してよい範囲が不明です",
        "fallback_plan": "想定外の場合の代替手段が不明です",
        "escalation_path": "問題発生時の相談先またはエスカレーション先が不明です",
        "customer_facing_wording": "外部向けに使ってよい説明文が不明です",
        "rationale": "なぜその判断になったかが不明です",
        "technical_constraint": "技術的制約または前提条件が不明です",
        "implementation_scope": "実装対象と対象外の境界が不明です",
        "trigger_for_reconsideration": "再検討が必要になる条件が不明です",
        "related_issue": "関連するチケットや追跡先が不明です",
        "failure_modes": "失敗パターンと観測方法が不明です",
        "contract_impact": "契約や商談への影響が不明です",
        "promise_boundary": "顧客に約束してよい範囲が不明です",
        "customer_expectation": "顧客期待値が調整済みか不明です",
        "timeline_confidence": "提示できる時期の確度が不明です",
        "negotiation_status": "交渉状況と未合意点が不明です",
    }
    return descriptions.get(slot, f"{slot} が不足しています")
