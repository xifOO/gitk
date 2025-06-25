import sys
from typing import Optional
from core.config import GitkConfig
from core.models import ModelConfig
from core.adapters import ModelFactory
from core.args_parser import parse_arguments
from core.utils import clean_diff, clean_message


class ConfigManager:

    def __init__(self) -> None:
        self.config_loader = GitkConfig()

    def load_config(self) -> tuple[dict, ModelConfig]:
        config_data = self.config_loader.load_config()
        model_config = self._create_model_config(config_data)
        return config_data, model_config
    
    def _create_model_config(self, config_data: dict) -> ModelConfig:
        model_json = config_data.get("model_config", {})
        provider = config_data.get("provider")
        
        if not provider:
            raise ValueError("Провайдер отсутствует в конфигурации")
        
        if not model_json:
            raise ValueError("Конфигурация модели отсутствует")
        
        return ModelConfig(
            name=model_json.get("name"),
            provider=provider,
            api_base=model_json.get("api_base"),
            model_id=model_json.get("model_id"),
            is_free=model_json.get("is_free"),
            max_tokens=model_json.get("max_tokens", 150),
            temperature=model_json.get("temperature", 0.4),
            description=""
        )


class TemplateManager:

    def __init__(self, config_loader: GitkConfig):
        self.config_loader = config_loader
    
    def get_commit_template(self, args, config_data: dict) -> Optional[str]:
        if args.template:
            return args.template
        
        if args.template_file:
            return self.config_loader.load_template_from_file(args.template_file)
        
        template_path = config_data.get("commit_template_path")
        if template_path:
            return self.config_loader.load_template_from_file(template_path)
        
        return None


class CommitGenerator:

    def __init__(self):
        self.config_manager = ConfigManager()
        self.template_manager = TemplateManager(self.config_manager.config_loader)
    
    def generate_commit_message(self, args):
        diff = self._read_diff_from_stdin()
        cleaned_diff = clean_diff(diff)

        config_data, model_config = self.config_manager.load_config()

        commit_template = self.template_manager.get_commit_template(args, config_data)

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