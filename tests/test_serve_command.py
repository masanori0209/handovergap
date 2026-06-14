from typer.testing import CliRunner

from handovergap.cli import app


def test_serve_command_is_documented() -> None:
    result = CliRunner().invoke(app, ["serve", "--help"])

    assert result.exit_code == 0
    assert "bilingual Streamlit comparison demo" in result.output
    assert "--port" in result.output
    assert "--host" in result.output
