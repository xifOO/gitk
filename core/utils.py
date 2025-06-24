import os
from pathlib import Path
import re
import shlex
import subprocess

import yaml

from core import config


class BashFuntionCaller:
    def __init__(self, script: str, env=None):
        self.script = os.path.join(os.path.dirname(__file__), script)
        self.env = env or os.environ.copy()
    
    def __getattr__(self, name):
        def call_fun(*args):
            _arg = " ".join(shlex.quote(arg) for arg in args)
            cmd = f"source {self.script} && {name} {_arg}"
            return subprocess.check_output(
                ["bash", "-c", cmd],
                universal_newlines=True,
                stderr=subprocess.STDOUT,
                env=self.env
            )
        return call_fun


def clean_diff(diff: str) -> str:
    if not diff.strip():
        raise ValueError("Diff пустой. Убедитесь что есть изменения для commit.")

    if len(diff) > config.MAX_DIFF_LENGTH:
        lines = diff.split("\n")
        truncated_lines = []
        count = 0
        for line in lines:
            if count + len(line) > config.MAX_DIFF_LENGTH - 200:
                break
            truncated_lines.append(line)
            count += len(line)
        diff = '\n'.join(truncated_lines) + '\n\n[... diff truncated for length ...]'

    return diff


def read_yaml(file_path: str | Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return config


def clean_message(message: str) -> str:
    message = re.sub(r'^```.*?\n', '', message, flags=re.MULTILINE)
    message = re.sub(r'\n```$', '', message)
    return message.strip()