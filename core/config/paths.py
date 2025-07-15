from pathlib import Path

from core.exceptions import CacheDirectoryError, ConfigDirectoryError


class ConfigDirectory:

    def __init__(self) -> None:
        try:
            home_dir = Path.home()
            if not home_dir.exists():
                raise ConfigDirectoryError(f"Home directory does not exist: {home_dir}")
            
            self._base = home_dir / ".gitk_config"

            if self._base.exists() and self._base.is_file():
                raise ConfigDirectoryError(f"Config path exists as file, not directory: {self._base}")
            
        except OSError as e:
            raise ConfigDirectoryError("OS error accessing home directory", cause=e) from e
        except Exception as e:
            raise ConfigDirectoryError("Failed to initialize config directory", cause=e) from e
        
    def ensure(self) -> None:
        self._base.mkdir(parents=True, exist_ok=True)
    
    def config_dir(self) -> Path:
        return self._base
    
    def config_file(self) -> Path:
        return self._base / "config.yaml"


class CacheDirectory:

    def __init__(self) -> None:
        self._config_dir = ConfigDirectory()
        try:
            self._cache_dir = self._config_dir.config_dir() / "cache/providers"

            if self._cache_dir.exists() and self._cache_dir.is_file():
                raise CacheDirectoryError(f"Cache path exists as file, not directory: {self._cache_dir}")
                
        except CacheDirectoryError:
            raise
        except Exception as e:
            raise CacheDirectoryError("Failed to initialize cache directory", cause=e) from e
    
    def ensure(self) -> None:
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_file_path(self, provider_name: str) -> Path:
        try:
            safe_provider_name = self._sanitize_filename(provider_name)
            cache_file_path = self._cache_dir / f"{safe_provider_name}_models.json"
            return cache_file_path
        except Exception as e:
            raise CacheDirectoryError(f"Failed to get cache file path for provider '{provider_name}'", cause=e) from e
    
    def _sanitize_filename(self, filename: str) -> str:
        unsafe_chars = '<>:"/\\|?*'
        sanitized = filename.strip()

        for char in unsafe_chars:
            sanitized = sanitized.replace(char, '_')
        
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        
        sanitized = sanitized.strip('_')

        if len(sanitized) > 85:
            sanitized = sanitized[:85]

        return sanitized

