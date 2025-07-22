import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.config.config import EnvFile, GitkConfig
from core.config.files import CacheFile
from core.models import OpenRouterRawModel, Provider
from core.utils import is_chat_model


def test_envfile_save_and_read():
    with tempfile.TemporaryDirectory() as tempdir:
        env = EnvFile()
        env._config_dir._base = Path(tempdir)
        env.env_file = Path(tempdir) / ".env"

        env.save_key("openai", "test-api-key")

        content = env._read_env_file()
        assert content["GITK_OPENAI_API_KEY"] == "test-api-key"

        env.load_to_environment()
        assert os.environ["GITK_OPENAI_API_KEY"] == "test-api-key"

        del os.environ["GITK_OPENAI_API_KEY"]


@patch("core.config.config.EnvFile")
@patch("core.config.config.Config")
def test_save_config(ConfigMock, EnvFileMock):
    provider = Provider[OpenRouterRawModel](
        name="openrouter",
        api_base="https://openrouter.ai/api/v1",
        api_key="dummy_api_key",
        raw_model_cls=OpenRouterRawModel,
        cache_file=CacheFile("openrouter"),
    )

    provider.fetch_models = MagicMock(
        return_value=[
            OpenRouterRawModel(
                id="free-model",
                name="Free Model",
                description="Free model",
                context_length=4096,
                pricing_prompt=0.0,
            ).to_model_config(),
            OpenRouterRawModel(
                id="paid-model",
                name="Paid Model",
                description="Paid model",
                context_length=4096,
                pricing_prompt=0.1,
            ).to_model_config(),
        ]
    )

    top_model = provider.get_top_models(filter_fn=is_chat_model)["free"][0]

    template_mock = MagicMock()
    template_mock.path = "template.txt"

    config_obj = MagicMock()
    ConfigMock.build_config.return_value = config_obj

    envfile_instance = EnvFileMock.return_value

    gitk_config = GitkConfig()
    gitk_config.save_config(top_model, template_mock, "some-key")

    config_obj.save_to_file.assert_called_once()
    envfile_instance.save_key.assert_called_once_with(top_model.provider, "some-key")
