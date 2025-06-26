import sys
from typing import Optional
from core.config import GitkConfig
from core.models import Config
from core.adapters import ModelFactory
from core.args_parser import parse_arguments
from core.utils import clean_diff, clean_message


class CommitGenerator:

    def __init__(self):
        self.config = GitkConfig()

    def get_commit_template(self, args, config_data: dict) -> Optional[str]:
        if args.template:
            return args.template
        
        if args.template_file:
            return self.config.load_template_from_file(args.template_file)
        
        template_path = config_data.get("commit_template_path")
        if template_path:
            return self.config.load_template_from_file(template_path)
        
        return None
    
    def generate_commit_message(self, args) -> str:
        diff = self._read_diff_from_stdin()
        cleaned_diff = clean_diff(diff)

        config: Config = self.config.load_config()
        config_data = config.model_dump()

        model_config = self.config.load_model_config(config_data)

        commit_template = self.get_commit_template(args, config_data)

        adapter = ModelFactory.create_adapter(model_config)

        commit_message = adapter.generate_commit_message(
            diff=cleaned_diff,
            detailed=args.detailed,
            commit_template=commit_template,
            instruction=args.instruction
        )

        return clean_message(commit_message)
    
    @staticmethod
    def _read_diff_from_stdin() -> str:
        if sys.stdin.isatty():
            raise ValueError("Данные должны поступать через pipe. Использование: git diff | python generator.py")
        
        diff = sys.stdin.read().strip()
        
        if not diff:
            raise ValueError("Пустой diff. Нет изменений для анализа.")
        
        return diff


def main():
    try:
        args = parse_arguments()

        generator = CommitGenerator()
        commit_message = generator.generate_commit_message(args)

        print(commit_message)
        
    except Exception as e:
        raise Exception
    

if __name__ == "__main__":
    main()