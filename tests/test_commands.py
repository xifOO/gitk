from unittest.mock import ANY, MagicMock, patch

import pytest
from click.testing import CliRunner

from core.cli.commands import cli


@pytest.fixture
def runner():
    return CliRunner()


@patch("core.cli.commands.GitkConfig")
@patch("core.cli.commands.TemplatesCLI")
@patch("core.cli.commands.ModelsCLI")
@patch("core.cli.commands.ApiKeyCLI")
def test_init_command(mock_api_key_cli, mock_models_cli, mock_templates_cli, mock_config_cls, runner):
    mock_config = MagicMock()
    mock_config_cls.return_value = mock_config

    mock_models = mock_models_cli.return_value
    mock_models.select_model.return_value = "mock-model"

    mock_api_key = mock_api_key_cli.return_value
    mock_api_key.setup_api_key.return_value = "mock-api-key"

    mock_templates = mock_templates_cli.return_value
    mock_templates.setup_interactive.return_value = "mock-template"

    result = runner.invoke(cli, ["init"])

    assert result.exit_code == 0
    mock_models.select_model.assert_called_once()
    mock_api_key.setup_api_key.assert_called_once_with("mock-model")
    mock_templates.setup_interactive.assert_called_once()
    mock_config.save_config.assert_called_once_with("mock-model", "mock-template", "mock-api-key")
    assert "GitK initialized." in result.output


@patch("core.cli.commands.subprocess.run")
@patch("core.cli.commands.os.remove")
@patch("core.cli.commands.tempfile.NamedTemporaryFile")
@patch("core.cli.commands.click.echo")
@patch("core.cli.commands.click.confirm")
@patch("core.cli.commands.GitkConfig")
@patch("core.cli.commands.argparse.Namespace")
@patch("core.cli.commands.generate_commit_message")
def test_commit_command_no_split_confirm(
    mock_generate_commit_message,
    mock_namespace,
    mock_config_cls,
    mock_confirm,
    mock_echo,
    mock_tempfile,
    mock_remove,
    mock_subprocess_run,
    runner,
):
    mock_config = MagicMock()
    mock_config_cls.return_value = mock_config

    mock_namespace.return_value = MagicMock(detailed=False, instruction=None, template=None, template_file=None, init=False)

    mock_subprocess_run.return_value = MagicMock(stdout="diff content", returncode=0)
    mock_generate_commit_message.return_value = "Commit message"
    mock_confirm.return_value = True

    mock_tmp_file = MagicMock()
    mock_tmp_file.__enter__.return_value.name = "/safe/mock/path/tmpfile"
    mock_tmp_file.__enter__.return_value.write = MagicMock()
    mock_tempfile.return_value = mock_tmp_file

    result = runner.invoke(cli, ["commit"])

    assert result.exit_code == 0
    mock_echo.assert_any_call("\n--- Commit message ---")
    mock_echo.assert_any_call("Commit message")
    mock_echo.assert_any_call("----------------------")
    mock_confirm.assert_called_once()
    mock_subprocess_run.assert_called()
    mock_remove.assert_called_once_with(ANY)
    mock_generate_commit_message.assert_called_once()


@patch("core.cli.commands.subprocess.run")
@patch("core.cli.commands.click.echo")
@patch("core.cli.commands.generate_commit_message")
def test_commit_command_split(
    mock_generate_commit_message,
    mock_echo,
    mock_subprocess_run,
    runner,
):
    mock_subprocess_run.side_effect = [
        MagicMock(stdout="file1.py\nfile2.py", returncode=0),
        MagicMock(stdout="diff content for file1", returncode=0),
        MagicMock(stdout="diff content for file2", returncode=0),
        MagicMock(returncode=0),
        MagicMock(returncode=0),
    ]

    mock_generate_commit_message.return_value = "Commit message for file"

    result = runner.invoke(cli, ["commit", "--split", "--yes"])

    assert result.exit_code == 0
    mock_echo.assert_any_call("\n--- Generating commit message for file: file1.py ---")
    mock_echo.assert_any_call("\n--- Generating commit message for file: file2.py ---")
    assert mock_generate_commit_message.call_count == 2


@patch("core.cli.commands.ModelsCLI")
@patch("core.cli.commands.click.secho")
def test_update_models(mock_secho, mock_models_cli, runner):
    mock_models = mock_models_cli.return_value

    result = runner.invoke(cli, ["update", "models"])

    assert result.exit_code == 0
    mock_models.refresh_models_list.assert_called_once()
    mock_secho.assert_called_with("Models list updated.", fg="green")
