from __future__ import annotations

import json
from importlib import resources

from handovergap.schemas import HandoverScenario


class InMemoryStore:
    def __init__(self, scenarios: list[HandoverScenario]):
        self._scenarios = scenarios
        self._by_key = {(scenario.scenario_id, scenario.successor_role): scenario for scenario in scenarios}

    @classmethod
    def from_builtin_dataset(cls) -> InMemoryStore:
        dataset_path = resources.files("handovergap.data").joinpath("handover_gap_bench.json")
        payload = json.loads(dataset_path.read_text())
        return cls([HandoverScenario.model_validate(item) for item in payload["scenarios"]])

    def get_scenario(self, scenario_id: str, successor_role: str) -> HandoverScenario:
        try:
            return self._by_key[(scenario_id, successor_role)]
        except KeyError as exc:
            available = ", ".join(f"{scenario.scenario_id}/{scenario.successor_role}" for scenario in self._scenarios)
            raise ValueError(f"Unknown scenario/role: {scenario_id}/{successor_role}. Available: {available}") from exc

    def list_scenarios(self) -> list[HandoverScenario]:
        return list(self._scenarios)
