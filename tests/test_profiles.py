from handovergap.core.detector import HandoverGapDetector
from handovergap.store import InMemoryStore


def test_store_get_scenario_uses_profile() -> None:
    store = InMemoryStore.from_builtin_dataset()

    scenario = store.get_scenario("S001", profile="CS")

    assert scenario.scenario_id == "S001"
    assert scenario.profile == "CS"


def test_detector_uses_profile() -> None:
    store = InMemoryStore.from_builtin_dataset()
    detector = HandoverGapDetector(store)

    result = detector.detect("S001", profile="CS")

    assert result.profile == "CS"
    assert result.task_context == "顧客問い合わせ対応"
    assert result.transferability_status == "blocked"
