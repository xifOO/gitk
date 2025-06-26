from pathlib import Path
from typing import Optional

from core.config.paths import ConfigDirectory


class Template:

    def __init__(self, directory: Path, name: str, content: Optional[str] = None) -> None:
        self._dir = directory
        self._name = name
        self._content = content

    @property
    def path(self) -> Path:
        if not self._name:
            raise ValueError("Template name is not specified")
        return self._dir / f"{self._name}.tpl"

    @property
    def content(self) -> str:
        if self._content is None:
            self._content = self.load_content()
        return self._content
    
    @property
    def name(self) -> str:
        return self._name

    def load_content(self) -> str:
        try:
            return self.path.read_text(encoding='utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.path}")
        except Exception as e:
            raise Exception(f"Error read file {self.path}: {e}")

    def save(self, content: Optional[str] = None) -> None:
        content_to_save = content or self._content
        if content_to_save is None:
            raise ValueError("No content to save")

        try:
            self.path.write_text(content_to_save, encoding='utf-8')
            self._content = content_to_save
        except Exception as e:
            raise

    def exists(self) -> bool:
        return self.path.exists()


class TemplateDirectory:
    def __init__(self):
        self.config_dir = ConfigDirectory().config_dir()
        self._templates_dir = self.config_dir / "templates"

    def ensure(self):
        self._templates_dir.mkdir(parents=True, exist_ok=True)
    
    def load_template_from_file(self, file_path: str | Path) -> Template:
        path = Path(file_path)
        return Template(path.parent, path.stem)

    def all_templates(self) -> list[Template]:
        return [Template(self._templates_dir, p.stem) for p in self._templates_dir.glob("*.tpl")]
    
    def get_template(self, name: str) -> Template:
        return Template(self._templates_dir, name)
    
    def create_template(self, name: str, content: str) -> Template:
        template = Template(self._templates_dir, name, content)
        template.save()
        return template

    def default_template(self) -> Template:
        return self.get_template("default_template")
    




