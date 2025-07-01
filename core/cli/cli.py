import re
from pathlib import Path

import questionary

from core.config.config import EnvFile
from core.constants import PROVIDER_INSTRUCTIONS
from core.models import SupportedModel
from core.templates import Template, TemplateDirectory
from core.utils import qprint


class TemplatesCLI:
    def __init__(self):
        self.templates_dir = TemplateDirectory()
    
    def setup_interactive(self) -> Template:
        qprint("\n=== Commit Template Setup ===")

        handlers = {
            "default": self.templates_dir.default_template,
            "list": self._select_from_existing,
            "custom": self._create_custom_template,
            "file": self._load_from_external_file
        }

        choices = [
            questionary.Choice("Use the default template", value="default"),
            questionary.Choice("Select from existing templates", value="list"),
            questionary.Choice("Create a custom template", value="custom"),
            questionary.Choice("Load template from file", value="file")
        ]

        choice = questionary.select(
            "Select an option for the commit template:",
            choices=choices
        ).ask()

        return handlers[choice]()
    

    def _select_from_existing(self) -> Template:
        templates = self.templates_dir.all_templates()
        if not templates:
            raise FileNotFoundError("No templates available")

        choices = [
            questionary.Choice(title=template.name, value=template)
            for template in templates
        ]

        selected = questionary.select(
            "Select a template from the list:",
            choices=choices
        ).ask()

        return selected
    
    def _create_custom_template(self) -> Template:
        content = self._get_content_from_input()
        name = self._get_name_from_input()

        return self.templates_dir.create_template(name, content)
    
    def _load_from_external_file(self) -> Template:
        file_path = questionary.path(
            "Specify the path to the template file:",
            validate=lambda x: Path(x).exists() or "File not found"
        ).ask()

        path = Path(file_path)
        return self.templates_dir.create_template(path.stem, path.read_text())
    
    def _get_content_from_input(self) -> str:
        qprint("Enter template lines (empty line to finish):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)

    def _get_name_from_input(self) -> str:
        name = questionary.text(
            "Enter the filename to save the template (without extension):",
            default="custom_template"
        ).ask()

        if not re.match(r"^[\w\-\.]+$", name):
            raise ValueError("Invalid filename")

        return name


class ModelsCLI:

    def select_model(self) -> SupportedModel:
        qprint("\n Select a model for commit generation:")
        
        choices = self._build_model_choices()
        
        return questionary.select(
            "Select model",
            choices=choices,
            use_indicator=True,
            use_shortcuts=True,
        ).ask()
    
    def _build_model_choices(self) -> list:
        choices = []
        
        free_models = SupportedModel.get_free_models()
        paid_models = SupportedModel.get_paid_models()

        if free_models:
            choices.append(questionary.Separator("=== Free models ==="))
            choices.extend([
                questionary.Choice(
                    title=f"{model.value.name} | {model.value.description}", 
                    value=model
                ) for model in free_models
            ])

        if paid_models:
            choices.append(questionary.Separator("=== Paid models ==="))
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
            qprint(f"\n{model_name}: {PROVIDER_INSTRUCTIONS[provider]}\n")
    
    def _should_replace_key(self, provider: str) -> bool:
        return questionary.confirm(
            f"An API key for {provider} was already found. Do you want to replace it?",
            default=False
        ).ask()
    
    def _get_api_key_from_user(self, provider: str) -> str:
        return questionary.text(
            f"Enter the API key for {provider}",
            validate=lambda x: len(x.strip()) > 0 or "The API key cannot be empty"
        ).ask()
