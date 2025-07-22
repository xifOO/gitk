import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

from core.config.paths import CacheDirectory, ConfigDirectory
from core.exceptions import CacheFileError, EnvFileError

if TYPE_CHECKING:
    from core.models import ModelConfig


class BaseFile:

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def ensure(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self._file_path.exists()

    @property
    def file_path(self) -> Path:
        return self._file_path


class CacheFile(BaseFile):

    def __init__(self, provider_name: str) -> None:
        cache_dir = CacheDirectory()
        cache_dir.ensure()
        cache_file_path = cache_dir.get_cache_file_path(provider_name)
        super().__init__(cache_file_path)

    def save_models(self, models: List["ModelConfig"]) -> None:
        try:
            self.ensure()
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(
                    [m.model_dump() for m in models], f, ensure_ascii=False, indent=2
                )
        except PermissionError as e:
            raise CacheFileError(
                f"Permission denied writing to cache file: {self.file_path}"
            ) from e
        except OSError as e:
            raise CacheFileError("OS error writing to cache file", cause=e) from e
        except json.JSONDecodeError as e:
            raise CacheFileError("JSON encoding error", cause=e) from e

    def load_models(self) -> List["ModelConfig"]:
        try:
            if not self.exists():
                return []

            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise CacheFileError(
                        f"Invalid JSON in cache file {self.file_path}", cause=e
                    ) from e
                finally:
                    self.file_path.unlink()

            from core.models import ModelConfig

            return [ModelConfig(**m) for m in data]

        except PermissionError as e:
            raise CacheFileError(
                f"Permission denied reading cache file: {self.file_path}"
            ) from e
        except OSError as e:
            raise CacheFileError("OS error reading cache file", cause=e) from e

    def delete_cache(self) -> None:
        try:
            if self.exists():
                self.file_path.unlink()

        except PermissionError as e:
            raise CacheFileError(
                f"Permission denied delete cache file: {self.file_path}"
            ) from e
        except OSError as e:
            raise CacheFileError("OS error delete cache file", cause=e) from e


class EnvFile(BaseFile):

    ENV_PREFIX = "GITK"
    ENV_HEADER = "# GitK API KEYS\n"

    def __init__(self) -> None:
        config_dir = ConfigDirectory()
        config_dir.ensure()
        env_file_path = config_dir.config_dir() / ".env"
        super().__init__(env_file_path)

    def get_env_var_name(self, provider: str) -> str:
        return f"{self.ENV_PREFIX}_{provider.upper()}_API_KEY"

    def key_exists(self, env_var: str) -> bool:
        env_vars = self._read_env_file()
        return env_var in env_vars

    def read_key(self, env_var: str) -> str:
        try:
            env_vars = self._read_env_file()
            return env_vars.get(env_var, "")
        except Exception as e:
            raise EnvFileError(f"Error reading key '{env_var}'", cause=e) from e

    def save_key(self, provider: str, api_key: str) -> None:
        try:
            env_var = self.get_env_var_name(provider)
            env_vars = self._read_env_file()
            env_vars[env_var] = api_key
            self._write_env_file(env_vars)
        except Exception as e:
            raise EnvFileError("Failed to save key", cause=e) from e

    def load_to_environment(self) -> None:
        try:
            env_vars = self._read_env_file()
            for key, value in env_vars.items():
                os.environ[key] = value
        except OSError as e:
            raise EnvFileError("OS error load enviroment", cause=e) from e

    def _read_env_file(self) -> Dict[str, str]:
        env_vars: Dict[str, str] = {}

        if not self.exists():
            return env_vars

        if self.file_path.stat().st_size == 0:
            return env_vars
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key] = value
            return env_vars

        except PermissionError as e:
            raise EnvFileError(
                f"Permission denied reading env file: {self.file_path}"
            ) from e
        except OSError as e:
            raise EnvFileError("OS error reading env file", cause=e) from e
        except UnicodeDecodeError as e:
            raise EnvFileError("Encoding error reading env file", cause=e) from e
        except Exception as e:
            raise EnvFileError("Failed to read env file", cause=e) from e

    def _write_env_file(self, env_vars: Dict[str, str]) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.ENV_HEADER)
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")

        except PermissionError as e:
            raise EnvFileError(
                f"Permission denied writing to env file: {self.file_path}"
            ) from e
        except OSError as e:
            raise EnvFileError("OS error writing to env file", cause=e) from e
        except Exception as e:
            raise EnvFileError("Failed to write env file", cause=e) from e
