import argparse
import sys

from core.adapters import ModelFactory
from core.cli.args_parser import parse_arguments
from core.cli.cli import ApiKeyCLI, ModelsCLI, TemplatesCLI
from core.config.config import GitkConfig
from core.models import Config
from core.templates import TemplateDirectory
from core.utils import clean_diff, clean_message, qprint


def generate_commit_message(args: argparse.Namespace, config: GitkConfig) -> str:
    diff = read_diff_from_stdin()
    cleaned_diff = clean_diff(diff)

    config_model: Config = config.load_config()
    config_data = config_model.model_dump()

    model_config = config.load_model_config(config_data)

    template_path = config_data.get("commit_template_path")

    if not template_path:
        raise ValueError("Commit template path not found in the config")

    template = TemplateDirectory().load_template_from_file(template_path)
    template_content = template.load_content()


    adapter = ModelFactory.create_adapter(model_config)

    commit_message = adapter.generate_commit_message(
        diff=cleaned_diff,
        detailed=args.detailed,
        commit_template=template_content,
        instruction=args.instruction
    )

    return clean_message(commit_message)
    

def read_diff_from_stdin() -> str:
    if sys.stdin.isatty():
        raise ValueError("Data must be provided via pipe. Usage: git diff | python generator.py")
    
    diff = sys.stdin.read().strip()
    
    if not diff:
        raise ValueError("Empty diff. No changes to analyze.")
    
    return diff


def main() -> None:
    try:
        args = parse_arguments()
        config = GitkConfig()
        
        if args.init:
            
            templates_cli = TemplatesCLI()
            models_cli = ModelsCLI()
            api_key_cli = ApiKeyCLI()

            selected_model = models_cli.select_model()
            api_key = api_key_cli.setup_api_key(selected_model)
            template = templates_cli.setup_interactive()

            config.save_config(selected_model, template, api_key)
            return

        commit_message = generate_commit_message(args, config)

        qprint(commit_message)

    except Exception as e:
        raise Exception from e
    

if __name__ == "__main__":
    main()