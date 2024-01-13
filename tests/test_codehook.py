from typer.testing import CliRunner
from codehook.main import app

runner = CliRunner()


def test_app():
    result = runner.invoke(
        app, ["deploy", "--file", "tests/handler.py", "--name", "handler"]
    )
    assert result.exit_code == 0
    assert "Deployment complete 🚀" in result.stdout
    assert "Function name:" in result.stdout
    assert "API ID:" in result.stdout
    assert "Webhook URL:" in result.stdout
    assert "Webhook ID:" in result.stdout

    result = runner.invoke(app, ["list"])
    assert "No codehook endpoints" not in result.stdout
    assert "No lambda functions" not in result.stdout
    assert "No webhook endpoints" not in result.stdout

    result = runner.invoke(app, ["delete", "--all"])
    assert "Deleting all functions and endpoints" in result.stdout
    assert "Deletion complete" in result.stdout

    result = runner.invoke(app, ["list"])
    assert "No codehook endpoints" in result.stdout
    assert "No lambda functions" in result.stdout
    assert "No webhook endpoints" in result.stdout
