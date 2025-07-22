import argparse

from core.adapters import ModelFactory
from core.config.config import GitkConfig
from core.models import Config
from core.templates import Template
from core.utils import clean_diff, clean_message


def generate_commit_message(
    args: argparse.Namespace, config: GitkConfig, diff: str
) -> str:
    cleaned_diff = clean_diff(diff)

    config_model: Config = config.load_config()
    config_data = config_model.model_dump()

    model_config = config.load_model_config(config_data)

    if args.template:
        template_content = args.template
    else:
        template_path = args.template_file or config_data.get("commit_template_path")

        if not template_path:
            raise ValueError(
                "No commit template provided. Specify --template, --template-file, or set it in config."
            )

        template = Template.from_file(template_path)
        template_content = template.get_content()

    adapter = ModelFactory.create_adapter(model_config)

    commit_message = adapter.generate_commit_message(
        diff=cleaned_diff,
        detailed=args.detailed,
        commit_template=template_content,
        instruction=args.instruction,
    )

    return clean_message(commit_message)
