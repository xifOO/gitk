import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.config.config import EnvFile, GitkConfig
from core.models import SupportedModel


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
    
    
@patch("core.config.config.ConfigDirectory")
@patch("core.config.config.EnvFile")
@patch("core.config.config.Config")
def test_save_config(ConfigMock, EnvFileMock, ConfigDirMock):
    selected_model = SupportedModel.QWEN_MODEL
    template_mock = MagicMock()
    template_mock.path = "template.txt"

    config_obj = MagicMock()
    ConfigMock.build_config.return_value = config_obj

    gitk_config = GitkConfig()
    gitk_config.save_config(selected_model, template_mock, "some-key")

    config_obj.save_to_file.assert_called_once()
    EnvFileMock.return_value.save_key.assert_called_once()
