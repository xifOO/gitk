import sys
import re
from core.config import GitkConfig
from core.models import ModelConfig
from core.adapters import ModelFactory
from core.utils import clean_diff


def main():
    try:
        if sys.stdin.isatty():
            print("Использование: git diff | python generator.py [--detailed]", file=sys.stderr)
            sys.exit(1)

        diff = sys.stdin.read()
        detailed = "--detailed" in sys.argv

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
        
        adapter = ModelFactory.create_adapter(model_config)
        commit_message = adapter.generate_commit_message(cleaned_diff, detailed=detailed)

        commit_message = re.sub(r'^```.*?\n', '', commit_message)
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