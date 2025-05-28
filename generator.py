import requests
import json
import os
import sys


def get_api_key():
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise EnvironmentError("OPENAI_API_KEY не установлен в переменных окружения.")
    
    return openai_api_key


def create_request():
    openai_api_key = get_api_key()
    diff = sys.stdin.read()
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "model": "qwen/qwen3-32b:free",
        "messages": [
        {
            "role": "user",
            "content": f"Write a concise Git commit message (max 2 lines) for the following git diff:\n{diff}"
        }
        ],
        
    })
    )

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise RuntimeError(f"OpenRouter API error {response.status_code}: {response.text}")


if __name__ == "__main__":
    print(create_request())
