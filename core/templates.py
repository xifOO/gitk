from pathlib import Path
from typing import Optional

from core.config.paths import ConfigDirectory
from core.exceptions import TemplateError, TemplateLoadError, TemplateSaveError


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
        except FileNotFoundError as file_error:
            raise TemplateLoadError(f"Template file not found: {self.path}") from file_error
        except PermissionError as e:
            raise TemplateLoadError(f"Permission denied reading template: {self.path}") from e
        except UnicodeDecodeError as e:
            raise TemplateLoadError(f"Template encoding error: {self.path}") from e
        except OSError as e:
            raise TemplateLoadError(f"OS error while reading template {self.path}", cause=e) from e
        except Exception as e:
            raise TemplateLoadError(f"Unexpected error while loading template {self.path}", cause=e) from e

    def save(self, content: Optional[str] = None) -> None:
        content_to_save = content or self._content
        if content_to_save is None:
            raise TemplateSaveError("No content to save")

        try:
            self.path.write_text(content_to_save, encoding='utf-8')
            self._content = content_to_save

        except PermissionError as e:
            raise TemplateSaveError(f"Permission denied writing to template: {self.path}") from e
        except OSError as e:
            raise TemplateSaveError(f"OS error while writing template {self.path}", cause=e) from e 
        except Exception as e:
            raise TemplateSaveError(f"Unexpected error while saving template {self.path}", cause=e) from e

    def exists(self) -> bool:
        return self.path.exists()


class TemplateDirectory:
    def __init__(self) -> None:
        self.config_dir = ConfigDirectory().config_dir()
        try:
            self._templates_dir = self.config_dir / "templates"
        except Exception as e:
            raise TemplateError("Failed to initialize TemplateDirectory", cause=e) from e

    def ensure(self) -> None:
        self._templates_dir.mkdir(parents=True, exist_ok=True)
    
    def load_template_from_file(self, file_path: str | Path) -> Template:
        path = Path(file_path)
        if not path.exists():
            raise TemplateLoadError(f"Template file not found: {file_path}")
        return Template(path.parent, path.stem)

    def all_templates(self) -> list[Template]:
        try:
            return [Template(self._templates_dir, p.stem) for p in self._templates_dir.glob("*.tpl")]
        except Exception as e:
            raise TemplateError("Failed to list templates", cause=e) from e
    
    def get_template(self, name: str) -> Template:
        return Template(self._templates_dir, name)
    
    def create_template(self, name: str, content: str) -> Template:
        try:
            template = Template(self._templates_dir, name, content)
            template.save()
            return template
        except Exception as e:
            raise TemplateSaveError(f"Failed to create template '{name}'", cause=e) from e

    def default_template(self) -> Template:
        return self.get_template("default_template")
    




