from typer.main import get_command
from typer.testing import CliRunner

from handovergap.cli import app


def test_serve_command_is_documented() -> None:
    result = CliRunner().invoke(app, ["serve", "--help"])

    assert result.exit_code == 0
    assert "bilingual Streamlit comparison demo" in result.output

    serve_command = get_command(app).commands["serve"]
    option_names = {name for parameter in serve_command.params for name in parameter.opts}
    assert {"--port", "--host"} <= option_names
