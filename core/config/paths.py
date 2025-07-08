from pathlib import Path


class ConfigDirectory:

    def __init__(self) -> None:
        self._base = Path.home() / ".gitk_config"
    
    def ensure(self) -> None:
        self._base.mkdir(parents=True, exist_ok=True)
    
    def config_dir(self) -> Path:
        return self._base
    
    def config_file(self) -> Path:
        return self._base / "config.yaml"


class CacheDirectory:

    def __init__(self) -> None:
        self._config_dir = ConfigDirectory()
        self._cache_dir = self._config_dir.config_dir() / "cache/providers"
    
    def ensure(self) -> None:
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_file_path(self, provider_name: str) -> Path:
        return self._cache_dir / f"{provider_name}_models.json"
