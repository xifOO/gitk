from pathlib import Path


class ConfigDirectory:

    def __init__(self) -> None:
        self._base = Path.home() / ".gitk_config"
    
    def ensure(self):
        self._base.mkdir(parents=True, exist_ok=True)
    
    def config_dir(self) -> Path:
        return self._base
    
    def config_file(self) -> Path:
        return self._base / "config.yaml"