import sys

from core.cli.cli import ApiKeyCLI, ModelsCLI, TemplatesCLI
from core.config.config import GitkConfig
from core.models import Config
from core.adapters import ModelFactory
from core.cli.args_parser import parse_arguments
from core.templates import TemplateDirectory
from core.utils import clean_diff, clean_message, qprint


class CommitGenerator:

    def __init__(self, config: GitkConfig):
        self.config = config

    def generate_commit_message(self, args) -> str:
        diff = self._read_diff_from_stdin()
        cleaned_diff = clean_diff(diff)

        config: Config = self.config.load_config()
        config_data = config.model_dump()

        model_config = self.config.load_model_config(config_data)

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
    
    @staticmethod
    def _read_diff_from_stdin() -> str:
        if sys.stdin.isatty():
            raise ValueError("Data must be provided via pipe. Usage: git diff | python generator.py")
        
        diff = sys.stdin.read().strip()
        
        if not diff:
            raise ValueError("Empty diff. No changes to analyze.")
        
        return diff


def main():
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

        generator = CommitGenerator(config)
        commit_message = generator.generate_commit_message(args)

        qprint(commit_message)

    except Exception as e:
        raise Exception
    

if __name__ == "__main__":
    main()