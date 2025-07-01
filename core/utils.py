import re

import questionary


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
        diff = '\n'.join(truncated_lines) + '\n\n[... diff truncated for length ...]'

    return diff


def clean_message(message: str) -> str:
    message = re.sub(r'^```.*?\n', '', message, flags=re.MULTILINE)
    message = re.sub(r'\n```$', '', message)
    return message.strip()


def qprint(content: str) -> None:
    questionary.print(content, style="bold")