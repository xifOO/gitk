from pathlib import Path
from typing import Generic, Optional, Type, TypeVar

from core.exceptions import BaseError, CacheDirectoryError, ConfigDirectoryError

E = TypeVar("E", bound=BaseError)


class BaseDirectory(Generic[E]):
    def __init__(self, path: Path, error_class: Type[E]) -> None:
        self._path = path
        self._error_class = error_class
        self._validate_path()

    def _validate_path(self) -> None:
        try:
            if self._path.exists() and self._path.is_file():
                raise self._error_class(
                    f"Path exists as file, not directory: {self._path}"
                )

        except PermissionError as e:
            raise self._error_class(
                f"Permission denied accessing path: {self._path}", cause=e
            ) from e
        except OSError as e:
            raise self._error_class(f"OS error with path: {self._path}", cause=e) from e

    def ensure_exists(self) -> Path:
        try:
            self._path.mkdir(parents=True, exist_ok=True)
            return self._path
        except PermissionError as e:
            raise self._error_class(
                f"Permission denied creating directory: {self._path}", cause=e
            ) from e
        except OSError as e:
            raise self._error_class(
                f"Failed to create directory: {self._path}", cause=e
            ) from e

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists() and self._path.is_dir()

    def ensure(self) -> None:
        self.ensure_exists()


class ConfigDirectory(BaseDirectory[ConfigDirectoryError]):
    def __init__(self) -> None:
        try:
            home_dir = Path.home()
            if not home_dir.exists():
                raise ConfigDirectoryError(f"Home directory does not exist: {home_dir}")
            base_path = home_dir / ".gitk_config"
        except OSError as e:
            raise ConfigDirectoryError(
                "OS error accessing home directory", cause=e
            ) from e

        try:
            super().__init__(base_path, ConfigDirectoryError)
        except Exception as e:
            raise ConfigDirectoryError(
                "Failed to initialize config directory", cause=e
            ) from e

    def config_dir(self) -> Path:
        return self._path

    def config_file(self, filename: str = "config.yaml") -> Path:
        return self._path / filename


class CacheDirectory(BaseDirectory[CacheDirectoryError]):

    def __init__(self, config_dir: Optional[ConfigDirectory] = None) -> None:
        if config_dir is None:
            config_dir = ConfigDirectory()

        cache_path = config_dir.config_dir() / "cache" / "providers"

        try:
            super().__init__(cache_path, CacheDirectoryError)
        except Exception as e:
            raise CacheDirectoryError(
                "Failed to initialize cache directory", cause=e
            ) from e

    def get_cache_file_path(self, provider_name: str) -> Path:
        try:
            safe_name = self._sanitize_filename(provider_name)
            if not safe_name:
                raise ValueError(f"Invalid provider name: '{provider_name}'")

            cache_file = self.ensure_exists() / f"{safe_name}_models.json"
            return cache_file

        except Exception as e:
            raise CacheDirectoryError(
                f"Failed to get cache file path for provider '{provider_name}'", cause=e
            ) from e

    def _sanitize_filename(self, filename: str) -> str:
        if not filename or not filename.strip():
            return ""

        sanitized = filename.strip()

        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            sanitized = sanitized.replace(char, "_")

        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")

        sanitized = sanitized.strip("_")

        if len(sanitized) > 85:
            sanitized = sanitized[:85].rstrip("_")

        if not sanitized:
            sanitized = "unknown"

        return sanitized
