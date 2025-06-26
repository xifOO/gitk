from pytest import Config
import os
from typing import Any, Dict

from core.config.paths import ConfigDirectory
from core.models import ModelConfig, SupportedModel, Config
from core.templates import Template, TemplateDirectory


class EnvFile:
    
    ENV_PREFIX = "GITK"
    ENV_HEADER = "# GitK API KEYS\n"
    
    def __init__(self):
        self._config_dir = ConfigDirectory()
        self.env_file = self._config_dir.config_dir() / ".env"
    
    def get_env_var_name(self, provider: str) -> str:
        return f"{self.ENV_PREFIX}_{provider.upper()}_API_KEY"
    
    def key_exists(self, env_var: str) -> bool:
        env_vars = self._read_env_file()
        return env_var in env_vars
    
    def read_key(self, env_var: str) -> str:
        env_vars = self._read_env_file()
        return env_vars.get(env_var, "")
    
    def save_key(self, provider: str, api_key: str):
        env_var = self.get_env_var_name(provider)
        env_vars = self._read_env_file()
        env_vars[env_var] = api_key
        self._write_env_file(env_vars)
    
    def load_to_environment(self):
        env_vars = self._read_env_file()
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def _read_env_file(self) -> Dict[str, str]:
        env_vars = {}
        
        if not self.env_file.exists():
            return env_vars
            
        with open(self.env_file, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    
        return env_vars
    
    def _write_env_file(self, env_vars: Dict[str, str]):
        with open(self.env_file, 'w', encoding="utf-8") as f:
            f.write(self.ENV_HEADER)
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    

class GitkConfig:
    
    def __init__(self):
        self._config_dir = ConfigDirectory()
        self.env_manager = EnvFile()
        self.templates_dir = TemplateDirectory()
    
    def save_config(self, selected_model: SupportedModel, template: Template, api_key: str | None = None) -> None:
        
        config = Config.build_config(selected_model, template.path)
        config.save_to_file(self._config_dir.config_file())

        if api_key:
            self.env_manager.save_key(selected_model.value.provider, api_key)
    
    def load_config(self) -> Config:
        if not self._config_dir.config_file().exists():
            raise FileNotFoundError("Конфиг не инициализирован. Запустите 'gitk init'")
        
        config = Config.from_yaml(self._config_dir.config_file())
        self.env_manager.load_to_environment()
        return config
    
    def load_model_config(self, config_data: Dict[str, Any]) -> ModelConfig:
        return ModelConfig.build_model_config(config_data)
    


