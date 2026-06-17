import pytest

from handovergap.core.detector import HandoverGapDetector
from handovergap.profiles import ProfileCatalog
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


def test_unknown_profile_error_lists_available_profiles() -> None:
    catalog = ProfileCatalog.builtins()

    with pytest.raises(ValueError) as exc_info:
        catalog.required_slots("UnknownRole")

    message = str(exc_info.value)
    assert "Unknown profile 'UnknownRole'" in message
    assert "Available profiles: CS, Engineer, Sales" in message
    assert "profiles validate" in message


def test_unknown_slot_error_lists_available_slots() -> None:
    catalog = ProfileCatalog.builtins()

    with pytest.raises(ValueError) as exc_info:
        catalog.slot_policy("CS", "unknown_slot")

    message = str(exc_info.value)
    assert "Unknown slot 'unknown_slot' for profile 'CS'" in message
    assert "communication_status" in message
    assert "customer_facing_wording" in message
