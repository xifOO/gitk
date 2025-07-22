import os
import re
from pathlib import Path
from typing import List, Union

import questionary

from core.config.files import CacheFile, EnvFile
from core.constants import PROVIDER_INSTRUCTIONS
from core.models import ModelConfig, OpenRouterRawModel, Provider
from core.templates import Template, TemplateDirectory
from core.utils import is_chat_model, qprint


class TemplatesCLI:
    def __init__(self) -> None:
        self.templates_dir = TemplateDirectory()

    def setup_interactive(self) -> Template:
        qprint("\n=== Commit Template Setup ===")

        handlers = {
            "default": self.templates_dir.default_template,
            "list": self._select_from_existing,
            "custom": self._create_custom_template,
            "file": self._load_from_external_file,
        }

        choices = [
            questionary.Choice("Use the default template", value="default"),
            questionary.Choice("Select from existing templates", value="list"),
            questionary.Choice("Create a custom template", value="custom"),
            questionary.Choice("Load template from file", value="file"),
        ]

        choice = questionary.select(
            "Select an option for the commit template:", choices=choices
        ).ask()

        if choice is None:
            raise KeyboardInterrupt("User cancelled the operation")

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
            "Select a template from the list:", choices=choices
        ).ask()

        if selected is None:
            raise KeyboardInterrupt("User cancelled the operation")

        return selected

    def _create_custom_template(self) -> Template:
        content = self._get_content_from_input()
        name = self._get_name_from_input()

        return self.templates_dir.create_template(name, content)

    def _load_from_external_file(self) -> Template:
        file_path = questionary.path(
            "Specify the path to the template file:",
            validate=lambda x: Path(x).exists() or "File not found",
        ).ask()

        if file_path is None:
            raise KeyboardInterrupt("User cancelled the operation")

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
            default="custom_template",
            validate=lambda x: bool(re.match(r"^[\w\-\.]+$", x)) or "Invalid filename",
        ).ask()

        if name is None:
            raise KeyboardInterrupt("User cancelled the operation")

        return name


class ModelsCLI:

    def __init__(self, provider_name: str) -> None:
        self.cache_file = CacheFile(provider_name)
        self.provider = Provider[OpenRouterRawModel](
            name=provider_name,
            api_base="https://openrouter.ai/api/v1",
            api_key=os.getenv("GITK_OPENROUTER_API_KEY", ""),
            raw_model_cls=OpenRouterRawModel,
            cache_file=self.cache_file,
        )

    def select_model(self) -> ModelConfig:
        qprint("\nSelect a model for commit generation:")

        choices = self._build_model_choices()

        choice = questionary.select(
            "Select model",
            choices=choices,
            use_indicator=True,
            use_shortcuts=True,
        ).ask()

        if choice is None:
            raise KeyboardInterrupt("User cancelled the operation")

        return choice

    def refresh_models_list(self) -> None:
        self.cache_file.delete_cache()
        self._build_model_choices()

    def _build_model_choices(
        self,
    ) -> List[Union[questionary.Separator, questionary.Choice]]:
        top_models = self.provider.get_top_models(filter_fn=is_chat_model)
        free_models = top_models["free"]

        def format_description(desc: str, length: int = 60) -> str:
            if len(desc) > length:
                return desc[: length - 3] + "..."
            return desc

        def format_model(model: ModelConfig) -> str:
            free_flag = "🆓"
            context_length = f"Context length: {model.context_length}"
            desc = format_description(model.description)
            return f"{model.name:<25} | {desc:<60} | {free_flag} | {context_length:<15}"

        choices: List[Union[questionary.Separator, questionary.Choice]] = []

        if free_models:
            choices.append(questionary.Separator("=== Free models ==="))
            choices.extend(
                [
                    questionary.Choice(title=format_model(model), value=model)
                    for model in free_models
                ]
            )

        return choices


class ApiKeyCLI:
    def __init__(self) -> None:
        self.env_file = EnvFile()

    def setup_api_key(self, model: ModelConfig) -> str:
        provider = model.provider

        self._show_provider_instructions(provider, model.name)

        env_var = self.env_file.get_env_var_name(provider)

        if self.env_file.key_exists(env_var):
            if not self._should_replace_key(provider):
                return self.env_file.read_key(env_var)

        return self._get_api_key_from_user(provider)

    def _show_provider_instructions(self, provider: str, model_name: str) -> None:
        if provider in PROVIDER_INSTRUCTIONS:
            qprint(f"\n{model_name}: {PROVIDER_INSTRUCTIONS[provider]}\n")

    def _should_replace_key(self, provider: str) -> bool:
        choice = questionary.confirm(
            f"An API key for {provider} was already found. Do you want to replace it?",
            default=False,
        ).ask()

        if choice is None:
            raise KeyboardInterrupt("User cancelled the operation")

        return choice

    def _get_api_key_from_user(self, provider: str) -> str:
        api_key = questionary.text(
            f"Enter the API key for {provider}",
            validate=lambda x: len(x.strip()) > 0 or "The API key cannot be empty",
        ).ask()

        if api_key is None:
            raise KeyboardInterrupt("User cancelled the operation")

        return api_key
