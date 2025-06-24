import argparse
import sys
import re
from typing import Optional
from core.config import GitkConfig
from core.models import ModelConfig
from core.adapters import ModelFactory
from core.utils import clean_diff



def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate git commit messages from diff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
         epilog="""
                Examples:
                git diff | python generator.py
                git diff | python generator.py --detailed
                git diff | python generator.py --instruction "use conventional commits"
                git diff | python generator.py --template-file custom_template.txt
            """
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Generate detailed commit message with body"
    )
    
    parser.add_argument(
        "--instruction",
        type=str,
        help="Additional instruction for commit message generation"
    )

    parser.add_argument(
        "--template-file",
        type=str,
        help="Path to custom commit template file (overrides config template)"
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Inline custom commit template (overrides config template)"
    )

    return parser.parse_args()


def get_commit_template(args, config_data: dict, config_loader: GitkConfig) -> Optional[str]:
    if args.template:
        return args.template
    
    if args.template_file:
        return config_loader.load_template_from_file(args.template_file)
    
    template_path = config_data.get("commit_template_path")
    if template_path:
        return config_loader.load_template_from_file(template_path)
    
    return 


def main():
    try:
        if sys.stdin.isatty():
            print("Использование: git diff | python generator.py [--detailed]", file=sys.stderr)
            sys.exit(1)
        
        args = parse_arguments()

        diff = sys.stdin.read()

        cleaned_diff = clean_diff(diff)

        config_loader = GitkConfig()
        config_data = config_loader.load_config()

        model_json = config_data.get("model_config", {})

        provider = config_data.get("provider")
        
        if provider is None:
            raise ValueError("Провайдер отсутствует")
        
        model_config = ModelConfig(
            name=model_json.get("name"),
            provider=provider,
            api_base=model_json.get("api_base"),
            model_id=model_json.get("model_id"),
            is_free=model_json.get("is_free"),
            max_tokens=model_json.get("max_tokens", 150),
            temperature=model_json.get("temperature", 0.4),
            description=""
        )
        
        commit_template = get_commit_template(args, config_data, config_loader)
        
        adapter = ModelFactory.create_adapter(model_config)
        commit_message = adapter.generate_commit_message(
            diff=cleaned_diff,
            detailed=args.detailed,
            commit_template=commit_template,
            instruction=args.instruction
        )

        commit_message = re.sub(r'^```.*?\n', '', commit_message, flags=re.MULTILINE)
        commit_message = re.sub(r'\n```$', '', commit_message)
        commit_message = commit_message.strip()

        print(commit_message)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()