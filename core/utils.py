import re

import questionary

from core.models import ModelConfig


def clean_diff(diff: str) -> str:
    MAX_DIFF_LENGTH = 3000

    if len(diff) > MAX_DIFF_LENGTH:
        lines = diff.split("\n")
        truncated_lines = []
        count = 0
        for line in lines:
            if count + len(line) > MAX_DIFF_LENGTH - 200:
                break
            truncated_lines.append(line)
            count += len(line)
        diff = "\n".join(truncated_lines) + "\n\n[... diff truncated for length ...]"

    return diff


def clean_message(message: str) -> str:
    message = re.sub(r"^```.*?\n", "", message, flags=re.MULTILINE)
    message = re.sub(r"\n```$", "", message)
    return message.strip()


def qprint(content: str) -> None:
    questionary.print(content, style="bold")


def is_chat_model(model: ModelConfig) -> bool:
    name = model.name.lower()

    include = [
        "chat",
        "gpt",
        "claude",
        "mistral",
        "llama",
        "gemini",
        "command",
        "deepseek",
        "mixtral",
    ]
    exclude = [
        "embed",
        "embedding",
        "experimental",
        "rerank",
        "search",
        "tts",
        "whisper",
        "instruct",
        "vision",
        "image",
        "speech",
        "nvidia",
        "0324",
    ]

    return any(x in name for x in include) and not any(x in name for x in exclude)


def is_safe_filename(filename: str) -> bool:
    return bool(re.match(r"^[\w\-.\\/]+$", filename))
