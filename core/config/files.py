import json
import os
from typing import TYPE_CHECKING, Dict, List

from core.config.paths import CacheDirectory, ConfigDirectory

if TYPE_CHECKING:
    from core.models import ModelConfig


class CacheFile:

    def __init__(self, provider_name: str) -> None:
        self._cache_dir = CacheDirectory()
        self._cache_dir.ensure()
        self.cache_file = self._cache_dir.get_cache_file_path(provider_name)

    def save_models(self, models: List["ModelConfig"]) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump([m.model_dump() for m in models], f, ensure_ascii=False, indent=2)
    
    def load_models(self) -> List["ModelConfig"]:
        if not self.cache_file.exists():
            return []
        
        with open(self.cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        from core.models import ModelConfig
        return [ModelConfig(**m) for m in data]


class EnvFile:
    
    ENV_PREFIX = "GITK"
    ENV_HEADER = "# GitK API KEYS\n"
    
    def __init__(self) -> None:
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
    
    def save_key(self, provider: str, api_key: str) -> None:
        env_var = self.get_env_var_name(provider)
        env_vars = self._read_env_file()
        env_vars[env_var] = api_key
        self._write_env_file(env_vars)
    
    def load_to_environment(self) -> None:
        env_vars = self._read_env_file()
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def _read_env_file(self) -> Dict[str, str]:
        env_vars: Dict[str, str] = {}
        
        if not self.env_file.exists():
            return env_vars
            
        with open(self.env_file, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    
        return env_vars
    
    def _write_env_file(self, env_vars: Dict[str, str]) -> None:
        with open(self.env_file, 'w', encoding="utf-8") as f:
            f.write(self.ENV_HEADER)
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")