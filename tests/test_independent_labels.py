import json
from pathlib import Path

from handovergap.store import InMemoryStore


def test_slack_observed_labels_are_anonymized_and_mapped() -> None:
    path = Path("src/handovergap/data/slack_observed_gap_labels.json")
    payload = json.loads(path.read_text())
    scenarios = {scenario.scenario_id for scenario in InMemoryStore.from_builtin_dataset("sanitized").list_scenarios()}
    raw_text = path.read_text()

    assert payload["observations"]
    assert all(observation["mapped_scenario_id"] in scenarios for observation in payload["observations"])
    assert "Raw Slack messages" in payload["source_method"]
    assert "http" not in raw_text
    assert "<@" not in raw_text
    assert "U0" not in raw_text
