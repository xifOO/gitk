from calendar import c
import json
import os
from typing import Optional
import questionary
from pathlib import Path

from core.models import SupportedModel

from core.constants import _DEFAULT_COMMIT_TEPLATE


MAX_DIFF_LENGTH = 3000


class GitkConfig:

    CONFIG_DIR = Path.home() / ".gitk_config"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    ENV_FILE = CONFIG_DIR / ".env"
    TEMPLATES_DIR = CONFIG_DIR / "templates"

    def init_config(self):

        self.CONFIG_DIR.mkdir(exist_ok=True)

        selected_model = self._select_model()

        api_key = self._setup_api_key(selected_model)
        commit_template = self._setup_commit_template()
        
        config = {
            "model": selected_model.name,
            "provider": selected_model.value.provider,
            "model_config": {
                "name": selected_model.value.name,
                "api_base": selected_model.value.api_base,
                "model_id": selected_model.value.model_id,
                "is_free": selected_model.value.is_free,
                "max_tokens": selected_model.value.max_tokens,
                "temperature": selected_model.value.temperature
            },
            "commit_template": commit_template
        }

        self._save_config(config)
        if api_key:
            self._save_api_key(selected_model.value.provider, api_key)
        
        print(f"GITK настроен с моделью: {selected_model.value.name}")
        print(f"Файлы конфига: {self.CONFIG_FILE} {self.ENV_FILE}")

    def _select_model(self) -> SupportedModel:
        print("\n Выберите модель для генерации коммитов:")

        free_models = SupportedModel.get_free_models()
        paid_models = SupportedModel.get_paid_models()

        choices = []

        if free_models:
            choices.append(questionary.Separator("=== Бесплатные модели ==="))
            for model in free_models:
                label = f"{model.value.name} | {model.value.description}"
                choices.append(questionary.Choice(title=label, value=model))

        if paid_models:
            choices.append(questionary.Separator("=== Платные модели ==="))
            for model in paid_models:
                label = f"{model.value.name} | {model.value.description}"
                choices.append(questionary.Choice(title=label, value=model))

        selected = questionary.select(
            "Выберите модель",
            choices=choices,
            use_indicator=True,
            use_shortcuts=True,
        ).ask()

        return selected
    

    def _setup_commit_template(self) -> Optional[str]:
        print("\n=== Настройка шаблона коммитов ===")

        choices = [
            questionary.Choice("Использовать стандартный шаблон", value="default"),
            questionary.Choice("Создать собственный шаблон", value="custom"),
            questionary.Choice("Загрузить шаблон с файла", value="file")
        ]

        choice = questionary.select(
            "Выберите опцию для шаблона коммитов:",
            choices=choices
        ).ask()

        match choice:
            case "default":
                return _DEFAULT_COMMIT_TEPLATE
            case "custom":
                return self._create_custom_template()
            case "file":
                return self._load_template_from_file()

    def _create_custom_template(self) -> str:
        lines = []

        while True:
            line = input()

            if line == "":
                break

            lines.append(line)
        
        template = "\n".join(lines)

        template_name = questionary.text(
            "Введите имя файла для сохранения шаблона (без расширения):",
            default="custom_template"
        ).ask()

        self.TEMPLATES_DIR.mkdir(exist_ok=True)

        template_path = self.TEMPLATES_DIR / f"{template_name}.txt"

        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"Шаблон сохранен в: {template_path}")
        except Exception as e:
            print(f"Ошибка сохранения шаблона: {e}")
            print("Шаблон будет использован без сохранения в файл")
        
        return template

    def _load_template_from_file(self) -> Optional[str]:
        file_path = questionary.path(
            "Укажите путь к файлу шаблона:",
            validate=lambda x: Path(x).exists() or "Файл не найден"
        ).ask()
        
        try:
            return self.load_template_from_file(file_path)
        except Exception as e:
            print(f"Ошибка загрузки шаблона: {e}")

    def _env_key_exists(self, env_var: str) -> bool:
        if not self.ENV_FILE.exists():
            return False
        with open(self.ENV_FILE, 'r') as f:
            for line in f:
                if line.strip().startswith(f"{env_var}="):
                    return True
        return False
    
    def _read_key_from_env_file(self, env_var: str) -> str:
        with open(self.ENV_FILE, 'r') as f:
            for line in f:
                if line.strip().startswith(f"{env_var}="):
                    return line.strip().split('=', 1)[1]
        return ""
    
    def _setup_api_key(self, model: SupportedModel) -> str:
        provider = model.value.provider

        instructions = {
            "openrouter": "OpenRouter → Получите ключ на: https://openrouter.ai",
        }

        if provider in instructions:
            print(f"\n{model.value.name}: {instructions[provider]}\n")

        env_var = f"GITK_{provider.upper()}_API_KEY"
        
        existing_key = self._env_key_exists(env_var)

        if existing_key:
            change = questionary.confirm(
                f"API ключ для {provider} уже найден. Хотите заменить его?",
                default=False
            ).ask()

            if not change:
                return self._read_key_from_env_file(env_var)

        api_key = questionary.text(
            f"Введите API ключ для {provider}",
            validate=lambda x: len(x.strip()) > 0 or "API ключ не может быть пустым"
        ).ask()

        return api_key
    
    def _save_config(self, config: dict):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _save_api_key(self, provider: str, api_key: str):
        env_var = f"GITK_{provider.upper()}_API_KEY"

        existing_vars = {}
        if self.ENV_FILE.exists():
            with open(self.ENV_FILE, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        existing_vars[key] = value
        
        existing_vars[env_var] = api_key

        with open(self.ENV_FILE, 'w') as f:
            f.write("# GitK API KEYS\n")
            for key, value in existing_vars.items():
                f.write(f"{key}={value}\n")

    def list_templates(self):
        if not self.TEMPLATES_DIR.exists():
            print("Папка с шаблонами не найдена")
            return

        template_files = list(self.TEMPLATES_DIR.glob("*.txt"))

        if not template_files:
            print("Шаблоны не найдены")
            return

        print("Доступные шаблоны: ")
        for template_file in template_files:
            print(f" - {template_file.name}")

    def load_template_from_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл шаблона не найден: {file_path}")
        except Exception as e:
            raise Exception(f"Ошибка чтения файла {file_path}: {e}")
    
    def load_config(self) -> dict:
        if not self.CONFIG_FILE.exists():
            raise FileNotFoundError("GitK не инициализирован. Запустите 'gitk init'")
        
        with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if self.ENV_FILE.exists():
            with open(self.ENV_FILE, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        return config

