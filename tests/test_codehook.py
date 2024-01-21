import time

from typer.testing import CliRunner

from codehook.main import app

runner = CliRunner(mix_stderr=False)


class TestDeployCommand:
    def test_deploy(self):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--file",
                "tests/handler.py",
                "--name",
                "handler",
                "--source",
                "stripe",
            ],
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

    def test_specific_event(self):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--file",
                "tests/handler.py",
                "--source",
                "stripe",
                "--enabled-events",
                "charge.succeeded",
            ],
        )
        assert result.exit_code == 0
        assert "Deployment complete 🚀" in result.stdout
        assert "Function name:" in result.stdout
        assert "API ID:" in result.stdout
        assert "Webhook URL:" in result.stdout
        assert "Webhook ID:" in result.stdout

        result = runner.invoke(app, ["delete", "--all"])
        assert result.exit_code == 0

    def test_unknown_event(self):
        result = runner.invoke(
            app,
            [
                "deploy",
                "--file",
                "tests/handler.py",
                "--source",
                "stripe",
                "--enabled-events",
                "charge.unknown",
            ],
        )
        assert result.exit_code == 2
        assert (
            "Invalid value for '--enabled-events': 'charge.unknown' is not one of"
            in result.stderr
        )

    def test_deploy_fail(self):
        result = runner.invoke(app, ["deploy", "--file", "tests/handler.py", "--fail"])

        assert result.exit_code == 2
        assert "No such option: --fail" in result.stderr


class TestConfigureCommand:
    def test_configure(self):
        result = runner.invoke(app, ["configure"])

        assert result.exit_code == 0
        assert "</> Welcome to codehook! </>" in result.stdout

    def test_configure_fail(self):
        result = runner.invoke(app, ["list", "--fail"])

        assert result.exit_code == 2
        assert "No such option: --fail" in result.stderr


class TestReconfigureCommand:
    def test_reconfigure(self):
        result = runner.invoke(app, ["reconfigure"])

        assert result.exit_code == 0
        assert "</> Welcome to codehook! </>" in result.stdout

    def test_reconfigure_fail(self):
        result = runner.invoke(app, ["list", "--fail"])

        assert result.exit_code == 2
        assert "No such option: --fail" in result.stderr


class TestListCommand:
    def test_list(self):
        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Listing all codehook endpoints..." in result.stdout
        assert "Listing all lambda functions..." in result.stdout
        assert "Listing all webhook endpoints..." in result.stdout

    def test_list_fail(self):
        result = runner.invoke(app, ["list", "--fail"])

        assert result.exit_code == 2
        assert "No such option: --fail" in result.stderr


class TestDeleteCommand:
    def test_delete(self):
        result = runner.invoke(app, ["delete", "--all"])

        assert result.exit_code == 0
        assert "Deleting all functions and endpoints" in result.stdout
        assert "Listing all codehook endpoints..." in result.stdout
        assert "Listing all lambda functions..." in result.stdout
        assert "Listing all webhook endpoints..." in result.stdout
        assert "Deletion complete" in result.stdout

    def test_delete_fail(self):
        result = runner.invoke(app, ["list", "--fail"])

        assert result.exit_code == 2
        assert "No such option: --fail" in result.stderr
