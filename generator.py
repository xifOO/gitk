import re
import requests
import json
import os
import sys


def get_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY не установлен в переменных окружения."
            "Установите его: export OPENAI_API_KEY=your_key_here"
        )
    
    return openai_api_key


def clean_diff(diff: str) -> str:
    if not diff.strip():
        raise ValueError("Diff пустой. Убедитесь что есть изменения для commit.")
    
    if len(diff) > 3000:
        lines = diff.split("\n")
        truncated_lines = []
        count = 0

        for line in lines:
            if count + len(line) > 2800:
                break
            truncated_lines.append(line)
            count += len(line)
        diff = '\n'.join(truncated_lines) + '\n\n[... diff truncated for length ...]'

    return diff


def create_commit_message_prompt(diff: str, detailed: bool) -> str:
    if detailed:
        return f"""Write a git commit message with title and detailed body for this git diff.

                Requirements:
                - First line: type(scope): brief description (max 50 chars)
                - Second line: empty
                - Body: detailed explanation of changes (max 72 chars per line)
                - Types: feat, fix, docs, style, refactor, test, chore
                - Use present tense and imperative mood

                Format:
                feat(scope): brief description

                - Detailed point 1
                - Detailed point 2
                - What was changed and why

                Git diff:
                {diff}

                Commit message:"""
    else:
        return f"""Write ONLY a single line commit message for this git diff.

                Requirements:
                - Use format: type(scope): brief description
                - Types: feat, fix, docs, style, refactor, test, chore
                - Maximum 50 characters total
                - No explanations, no markdown, no extra text
                - Just the commit message line

                Examples:
                feat(auth): add login validation
                fix(api): handle null user data
                docs(readme): update setup guide

                Git diff:
                {diff}

                Commit message:"""


def generate_commit_message(diff: str, detailed: bool) -> str:
    try:
        api_key = get_api_key()
        cleaned_diff = clean_diff(diff)
        prompt = create_commit_message_prompt(cleaned_diff, detailed)
        
        system_content = "You write single-line git commit messages. Respond with ONLY the commit message, no explanations." if not detailed else "You are a senior software engineer who writes excellent, detailed Git commit messages following conventional commit standards."
        temperature = 0.4 if detailed else 0.3
        max_tokens = 200 if detailed else 60

        payload = {
            "model": "qwen/qwen-2.5-72b-instruct:free", 
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": temperature,  
            "max_tokens": max_tokens,  
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload),
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if 'choices' not in result or not result['choices']:
            raise RuntimeError("API вернул пустой ответ")
        
        commit_message = result['choices'][0]['message']['content'].strip()

        commit_message = re.sub(r'^```.*?\n', '', commit_message)
        commit_message = re.sub(r'\n```$', '', commit_message)
        commit_message = commit_message.strip()

        return commit_message
    
    except requests.exceptions.Timeout:
        raise RuntimeError("Таймаут при обращении к API")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка сети: {e}")
    except json.JSONDecodeError:
        raise RuntimeError("Не удалось парсить ответ API")
    except KeyError as e:
        raise RuntimeError(f"Неожиданный формат ответа API: отсутствует ключ {e}")


def main():
    try:
        if sys.stdin.isatty():
            print("Использование: git diff | python commit_generator.py", file=sys.stderr)
            print("Или: git diff HEAD~1 | python commit_generator.py", file=sys.stderr)
            sys.exit(1)
        diff = sys.stdin.read()
        detailed: bool = "--detailed" in sys.argv
        commit_message = generate_commit_message(diff, detailed)

        print(commit_message)

    except EnvironmentError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Ошибка входных данных: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Ошибка выполнения: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПрервано пользователем", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()