from pathlib import Path
import re

import questionary

from core.config.config import EnvFile
from core.constants import PROVIDER_INSTRUCTIONS
from core.models import SupportedModel
from core.templates import TemplateDirectory, Template


class TemplatesCLI:
    def __init__(self):
        self.templates_dir = TemplateDirectory()
    
    def setup_interactive(self) -> Template:
        print("\n=== Настройка шаблона коммитов ===")

        handlers = {
            "default": self.templates_dir.default_template,
            "list": self.templates_dir.all_templates,
            "custom": self._create_custom_template,
            "file": self._load_from_external_file
        }

        choices = [
            questionary.Choice("Использовать стандартный шаблон", value="default"),
            questionary.Choice("Выбрать из созданных шаблонов", value="list"),
            questionary.Choice("Создать собственный шаблон", value="custom"),
            questionary.Choice("Загрузить шаблон из файла", value="file")
        ]

        choice = questionary.select(
            "Выберите опцию для шаблона коммитов:",
            choices=choices
        ).ask()

        return handlers[choice]()
    

    def _select_from_existing(self) -> Template:
        templates = self.templates_dir.all_templates()
        if not templates:
            raise FileNotFoundError("Нет доступных шаблонов")

        choices = [
            questionary.Choice(title=template.name, value=template)
            for template in templates
        ]

        selected = questionary.select(
            "Выберите шаблон из списка:",
            choices=choices
        ).ask()

        return selected
    
    def _create_custom_template(self) -> Template:
        content = self._get_content_from_input()
        name = self._get_name_from_input()

        return self.templates_dir.create_template(name, content)
    
    def _load_from_external_file(self) -> Template:
        file_path = questionary.path(
            "Укажите путь к файлу шаблона:",
            validate=lambda x: Path(x).exists() or "Файл не найден"
        ).ask()

        path = Path(file_path)
        return self.templates_dir.create_template(path.stem, path.read_text())
    
    def _get_content_from_input(self) -> str:
        print("Введите строки шаблона (пустая строка — завершить):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)

    def _get_name_from_input(self) -> str:
        name = questionary.text(
            "Введите имя файла для сохранения шаблона (без расширения):",
            default="custom_template"
        ).ask()

        if not re.match(r"^[\w\-\.]+$", name):
            raise ValueError("Недопустимое имя файла")

        return name


class ModelsCLI:

    def select_model(self) -> SupportedModel:
        print("\n Выберите модель для генерации коммитов:")
        
        choices = self._build_model_choices()
        
        return questionary.select(
            "Выберите модель",
            choices=choices,
            use_indicator=True,
            use_shortcuts=True,
        ).ask()
    
    def _build_model_choices(self) -> list:
        choices = []
        
        free_models = SupportedModel.get_free_models()
        paid_models = SupportedModel.get_paid_models()

        if free_models:
            choices.append(questionary.Separator("=== Бесплатные модели ==="))
            choices.extend([
                questionary.Choice(
                    title=f"{model.value.name} | {model.value.description}", 
                    value=model
                ) for model in free_models
            ])

        if paid_models:
            choices.append(questionary.Separator("=== Платные модели ==="))
            choices.extend([
                questionary.Choice(
                    title=f"{model.value.name} | {model.value.description}", 
                    value=model
                ) for model in paid_models
            ])

        return choices


class ApiKeyCLI:
    def __init__(self):
        self.env_file = EnvFile()
    
    def setup_api_key(self, model: SupportedModel) -> str:
        provider = model.value.provider
        
        self._show_provider_instructions(provider, model.value.name)
        
        env_var = self.env_file.get_env_var_name(provider)
        
        if self.env_file.key_exists(env_var):
            if not self._should_replace_key(provider):
                return self.env_file.read_key(env_var)
        
        return self._get_api_key_from_user(provider)

    def _show_provider_instructions(self, provider: str, model_name: str):
        if provider in PROVIDER_INSTRUCTIONS:
            print(f"\n{model_name}: {PROVIDER_INSTRUCTIONS[provider]}\n")
    
    def _should_replace_key(self, provider: str) -> bool:
        return questionary.confirm(
            f"API ключ для {provider} уже найден. Хотите заменить его?",
            default=False
        ).ask()
    
    def _get_api_key_from_user(self, provider: str) -> str:
        return questionary.text(
            f"Введите API ключ для {provider}",
            validate=lambda x: len(x.strip()) > 0 or "API ключ не может быть пустым"
        ).ask()
