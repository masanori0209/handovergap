from pathlib import Path

from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.privacy import scan_privacy


def test_privacy_scan_default_public_paths() -> None:
    findings = scan_privacy()

    assert findings == []


def test_privacy_scan_detects_obvious_secret(tmp_path: Path) -> None:
    path = tmp_path / "leak.md"
    path.write_text("OPENAI_API_KEY=sk-" + "x" * 32 + "\n")

    findings = scan_privacy([str(path)])

    assert len(findings) >= 1
    assert findings[0].kind in {"assigned_secret", "openai_api_key"}
    assert "sk-" not in findings[0].excerpt or "REDACTED" in findings[0].excerpt


def test_privacy_check_cli_fails_on_secret(tmp_path: Path) -> None:
    path = tmp_path / "leak.md"
    path.write_text("TIDB_PASSWORD=actual-password-value\n")

    result = CliRunner().invoke(app, ["privacy-check", str(path)])

    assert result.exit_code == 1
    assert "Privacy findings" in result.output
    assert "actual-password-value" not in result.output
