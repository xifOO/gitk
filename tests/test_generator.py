from unittest.mock import MagicMock, patch

import pytest

import core.generator as generator
from core.models import Config, ModelConfig


@pytest.fixture
def dummy_args():
    return MagicMock(detailed=False, instruction=None)


@patch("core.generator.read_diff_from_stdin", return_value="diff --git a/file.py b/file.py\n...")
@patch("core.generator.TemplateDirectory")
@patch("core.generator.ModelFactory.create_adapter")
def test_generate_commit_message_success(mock_adapter_factory, mock_template_dir, mock_read_diff, dummy_args):
    mock_config = MagicMock()

    mock_config.load_config.return_value = Config(
        model="gpt-4",
        provider="openai",
        model_config_data=ModelConfig(
            name="test-model",
            provider="openai",
            api_base="https://api.example.com",
            model_id="test-id",
            is_free=False,
            context_length=2048,
            temperature=0.4,
            description=""
        ),
        commit_template_path="./templates/template.tpl"
    )

    template_mock = MagicMock()
    template_mock.load_content.return_value = "Commit template content"
    mock_template_dir.return_value.load_template_from_file.return_value = template_mock

    adapter_mock = MagicMock()
    adapter_mock.generate_commit_message.return_value = "Generated commit message"
    mock_adapter_factory.return_value = adapter_mock

    result = generator.generate_commit_message(dummy_args, mock_config)

    assert result == "Generated commit message"
