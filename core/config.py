import yaml
import os
from typing import Dict
import questionary
from pathlib import Path

from core.models import SupportedModel
from core.utils import read_yaml


MAX_DIFF_LENGTH = 3000


class ConfigPaths:
    
    def __init__(self):
        self.config_dir = Path.home() / ".gitk_config"
        self.config_file = self.config_dir / "config.yaml"
        self.env_file = self.config_dir / ".env"
        self.templates_dir = self.config_dir / "templates"
    
    def ensure_directories(self):
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)


class EnvManager:
    
    ENV_PREFIX = "GITK"
    ENV_HEADER = "# GitK API KEYS\n"
    
    def __init__(self, env_file: Path):
        self.env_file = env_file
    
    def get_env_var_name(self, provider: str) -> str:
        return f"{self.ENV_PREFIX}_{provider.upper()}_API_KEY"
    
    def key_exists(self, env_var: str) -> bool:
        env_vars = self._read_env_file()
        return env_var in env_vars
    
    def read_key(self, env_var: str) -> str:
        env_vars = self._read_env_file()
        return env_vars.get(env_var, "")
    
    def save_key(self, provider: str, api_key: str):
        env_var = self.get_env_var_name(provider)
        env_vars = self._read_env_file()
        env_vars[env_var] = api_key
        self._write_env_file(env_vars)
    
    def load_to_environment(self):
        env_vars = self._read_env_file()
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def _read_env_file(self) -> Dict[str, str]:
        env_vars = {}
        
        if not self.env_file.exists():
            return env_vars
            
        with open(self.env_file, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
                    
        return env_vars
    
    def _write_env_file(self, env_vars: Dict[str, str]):
        with open(self.env_file, 'w', encoding="utf-8") as f:
            f.write(self.ENV_HEADER)
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")


class ModelSelector:
    
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


class ApiKeyManager:
    
    PROVIDER_INSTRUCTIONS = {
        "openrouter": "OpenRouter → Получите ключ на: https://openrouter.ai",
    }
    
    def __init__(self, env_manager: EnvManager):
        self.env_manager = env_manager
    
    def setup_api_key(self, model: SupportedModel) -> str:
        provider = model.value.provider
        
        self._show_provider_instructions(provider, model.value.name)
        
        env_var = self.env_manager.get_env_var_name(provider)
        
        if self.env_manager.key_exists(env_var):
            if not self._should_replace_key(provider):
                return self.env_manager.read_key(env_var)
        
        return self._get_api_key_from_user(provider)
    
    def _show_provider_instructions(self, provider: str, model_name: str):
        if provider in self.PROVIDER_INSTRUCTIONS:
            print(f"\n{model_name}: {self.PROVIDER_INSTRUCTIONS[provider]}\n")
    
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


class TemplateManager:
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
    
    def setup_template(self) -> Path:
        print("\n=== Настройка шаблона коммитов ===")

        template_handlers = {
            "default": self._use_default_template,
            "list": self._list_templates,
            "custom": self._create_custom_template,
            "file": self._load_template_from_file
        }

        choices = [
            questionary.Choice("Использовать стандартный шаблон", value="default"),
            questionary.Choice("Выбрать из созданных шаблонов", value="list"),
            questionary.Choice("Создать собственный шаблон", value="custom"),
            questionary.Choice("Загрузить шаблон с файла", value="file")
        ]

        choice = questionary.select(
            "Выберите опцию для шаблона коммитов:",
            choices=choices
        ).ask()

        return template_handlers[choice]()
    
    def load_from_file(self, file_path: str | Path) -> str:
        try:
            return Path(file_path).read_text(encoding='utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл шаблона не найден: {file_path}")
        except Exception as e:
            raise Exception(f"Ошибка чтения файла {file_path}: {e}")
    
    def _use_default_template(self) -> Path:
        default_path = self.templates_dir / "default_template.txt"
        if not default_path.exists():
            raise FileNotFoundError(f"Шаблон default_template.txt не найден в пути {default_path}.")
        return default_path
    
    def _create_custom_template(self) -> Path:
        template_content = self._get_template_content_from_input()
        template_name = self._get_template_name()
        
        return self._save_template(template_name, template_content)
    
    def _get_template_content_from_input(self) -> str:
        print("Введите строки шаблона (пустая строка — завершить):")
        lines = []

        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        
        return "\n".join(lines)
    
    def _get_template_name(self) -> str:
        return questionary.text(
            "Введите имя файла для сохранения шаблона (без расширения):",
            default="custom_template"
        ).ask()
    
    def _save_template(self, template_name: str, content: str) -> Path:
        template_path = self.templates_dir / f"{template_name}.txt"
        
        try:
            template_path.write_text(content, encoding='utf-8')
            print(f"Шаблон сохранен в: {template_path}")
            return template_path
        except Exception as e:
            print(f"Ошибка сохранения шаблона: {e}")
            raise
    
    def _load_template_from_file(self) -> Path:
        file_path = questionary.path(
            "Укажите путь к файлу шаблона:",
            validate=lambda x: Path(x).exists() or "Файл не найден"
        ).ask()
        
        return Path(file_path)
    
    def _list_templates(self) -> Path:
        template_files = self._get_available_templates()
        
        print("\n=== Настройка шаблона коммитов ===")

        choices = [questionary.Choice(title=tpl.name, value=tpl) for tpl in template_files]

        selected = questionary.select(
            "Выберите шаблон из списка:",
            choices=choices
        ).ask()

        return Path(selected)
    
    def _get_available_templates(self) -> list[Path]:
        if not self.templates_dir.exists():
            raise FileNotFoundError("Папка шаблонов не найдена.")

        template_files = list(self.templates_dir.glob("*.txt"))

        if not template_files:
            raise FileNotFoundError("Шаблоны не найдены")

        return template_files


class ConfigBuilder:
    
    @staticmethod
    def build_config(selected_model: SupportedModel, template_path: Path) -> dict:
        return {
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
            "commit_template_path": str(template_path)
        }


class GitkConfig:
    
    def __init__(self):
        self.paths = ConfigPaths()
        self.env_manager = EnvManager(self.paths.env_file)
        self.model_selector = ModelSelector()
        self.api_key_manager = ApiKeyManager(self.env_manager)
        self.template_manager = TemplateManager(self.paths.templates_dir)
    
    def init_config(self):
        self.paths.ensure_directories()
        
        selected_model = self.model_selector.select_model()
        api_key = self.api_key_manager.setup_api_key(selected_model)
        commit_template_path = self.template_manager.setup_template()
        
        config = ConfigBuilder.build_config(selected_model, commit_template_path)
        
        self._save_config(config)
        if api_key:
            self.env_manager.save_key(selected_model.value.provider, api_key)
        
        self._print_success_message(selected_model)
    
    def load_config(self) -> dict:
        if not self.paths.config_file.exists():
            raise FileNotFoundError("GitK не инициализирован. Запустите 'gitk init'")
        
        config = read_yaml(self.paths.config_file)
        self.env_manager.load_to_environment()
        
        return config
    
    def load_template_from_file(self, file_path: str | Path) -> str:
        return self.template_manager.load_from_file(file_path)
    
    def _save_config(self, config: dict):
        with open(self.paths.config_file, 'w', encoding="utf-8") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)
    
    def _print_success_message(self, selected_model: SupportedModel):
        print(f"GITK настроен с моделью: {selected_model.value.name}")
        print(f"Файлы конфига: {self.paths.config_file} {self.paths.env_file}")
