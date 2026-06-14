from __future__ import annotations

import json
from importlib import resources

from handovergap.schemas import HandoverScenario

DATASET_FILES = {
    "mini": "handover_gap_bench.json",
    "holdout": "handover_gap_bench_holdout.json",
}


class InMemoryStore:
    def __init__(self, scenarios: list[HandoverScenario]):
        self._scenarios = scenarios
        self._by_key = {(scenario.scenario_id, scenario.successor_role): scenario for scenario in scenarios}

    @classmethod
    def from_builtin_dataset(cls, dataset: str = "mini") -> InMemoryStore:
        if dataset == "all":
            scenarios = []
            for dataset_name in DATASET_FILES:
                scenarios.extend(cls.from_builtin_dataset(dataset_name).list_scenarios())
            return cls(scenarios)
        try:
            filename = DATASET_FILES[dataset]
        except KeyError as exc:
            available = ", ".join([*DATASET_FILES, "all"])
            raise ValueError(f"Unknown built-in dataset: {dataset}. Available: {available}") from exc
        dataset_path = resources.files("handovergap.data").joinpath(filename)
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
