from typing import Any, Dict

from core.config.files import EnvFile
from core.config.paths import ConfigDirectory
from core.exceptions import ConfigFileError
from core.models import Config, ModelConfig
from core.templates import Template, TemplateDirectory


class GitkConfig:
    
    def __init__(self) -> None:
        self._config_dir = ConfigDirectory()
        self.env_file = EnvFile()
        self.templates_dir = TemplateDirectory()
    
    def save_config(self, selected_model: ModelConfig, template: Template, api_key: str | None = None) -> None:
        try:
            config = Config.build_config(selected_model, template.path)
            config.save_to_file(self._config_dir.config_file())
        except (OSError, ValueError) as e:
            raise ConfigFileError("Failed to save config file", cause=e) from e

        if api_key:
            self.env_file.save_key(selected_model.provider, api_key)
    
    def load_config(self) -> Config:
        config_path = self._config_dir.config_file()
        if not config_path.exists():
            raise FileNotFoundError("Config is not initialized. Run 'gitk init'")
        
        config = Config.from_yaml(self._config_dir.config_file())
        self.env_file.load_to_environment()
        return config
    
    def load_model_config(self, config_data: Dict[str, Any]) -> ModelConfig:
        return ModelConfig.build_model_config(config_data)
    