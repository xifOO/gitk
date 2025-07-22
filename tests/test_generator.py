from unittest.mock import MagicMock, patch

import pytest

import core.generator as generator
from core.models import Config, ModelConfig


@pytest.fixture
def dummy_args():
    return MagicMock(
        detailed=False, instruction=None, template=None, template_file=None
    )


@patch("core.generator.clean_diff", side_effect=lambda x: x)
@patch("core.generator.clean_message", side_effect=lambda x: x)
@patch("core.generator.ModelFactory.create_adapter")
@patch("core.generator.Template")
def test_generate_commit_message_success(
    mock_template,
    mock_adapter_factory,
    mock_clean_message,
    mock_clean_diff,
    dummy_args,
):
    mock_config = MagicMock()
    config_data = {
        "model": "gpt-4",
        "provider": "openai",
        "model_config_data": ModelConfig(
            name="test-model",
            provider="openai",
            api_base="https://api.example.com",
            model_id="test-id",
            is_free=False,
            context_length=2048,
            temperature=0.4,
            description="",
        ),
        "commit_template_path": "./templates/template.tpl",
    }
    mock_config.load_config.return_value = Config(**config_data)
    mock_config.load_model_config.return_value = config_data["model_config_data"]

    template_instance_mock = MagicMock()
    template_instance_mock.get_content.return_value = "Commit template content"
    mock_template.from_file.return_value = template_instance_mock

    adapter_mock = MagicMock()
    adapter_mock.generate_commit_message.return_value = "Generated commit message"
    mock_adapter_factory.return_value = adapter_mock

    diff_input = "diff --git a/file.py b/file.py\n..."

    result = generator.generate_commit_message(dummy_args, mock_config, diff_input)

    mock_clean_diff.assert_called_once_with(diff_input)
    mock_template.from_file.assert_called_once_with("./templates/template.tpl")
    template_instance_mock.get_content.assert_called_once()
    adapter_mock.generate_commit_message.assert_called_once_with(
        diff=diff_input,
        detailed=dummy_args.detailed,
        commit_template="Commit template content",
        instruction=dummy_args.instruction,
    )
    mock_clean_message.assert_called_once_with("Generated commit message")
    assert result == "Generated commit message"
