from typer.testing import CliRunner
from codehook.main import app

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Listing all codehook endpoints" in result.stdout
    assert "Listing all lambda functions" in result.stdout