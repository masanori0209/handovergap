from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from handovergap.slot_rules import GAP_TYPE_BY_SLOT, HIGH_RISK_SLOTS, PROFILE_REQUIRED_SLOTS, QUESTION_BY_SLOT


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
            raise ValueError(f"Unknown profile: {profile}. Available: {available}") from exc

    def required_slots(self, profile: str) -> list[str]:
        return [slot.slot_name for slot in self.get(profile).required_slots]

    def slot_policy(self, profile: str, slot_name: str) -> SlotPolicy:
        for slot in self.get(profile).required_slots:
            if slot.slot_name == slot_name:
                return slot
        raise ValueError(f"Unknown slot '{slot_name}' for profile '{profile}'.")


def _profile_from_mapping(profile_name: str, payload: object) -> ProfileDefinition:
    if not isinstance(payload, dict):
        raise ValueError(f"Profile '{profile_name}' must be an object.")
    data = {"profile": profile_name, **payload}
    return ProfileDefinition.model_validate(data)


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
