import importlib.util
import json
from pathlib import Path


def _load_main():
    path = Path("harness/validation/independent_gap_label_check.py")
    spec = importlib.util.spec_from_file_location("independent_gap_label_check", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main


def test_independent_gap_label_check_writes_report(tmp_path, monkeypatch) -> None:
    main = _load_main()
    output_json = tmp_path / "labels.json"
    output_md = tmp_path / "labels.md"
    monkeypatch.setattr(
        "sys.argv",
        [
            "independent_gap_label_check.py",
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
    )

    assert main() == 0
    payload = json.loads(output_json.read_text())

    assert payload["status"] == "ok"
    assert payload["observation_count"] == 5
    assert output_md.read_text().startswith("# Independent Gap Label Review")
