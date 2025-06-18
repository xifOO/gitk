from abc import ABC, abstractmethod
import os
from typing import Optional

import requests
from core.models import ModelConfig


class ModelAdapter(ABC):

    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_key = self._get_api_key()
    
    @abstractmethod
    def generate_commit_message(self, diff: str, detailed: bool) -> str: ...

    def _get_api_key(self) -> Optional[str]:
        env_var = f"GITK_{self.config.provider.upper()}_API_KEY"
        return os.getenv(env_var)

    def _build_prompt(self, diff: str, detailed: bool) -> str:
        if detailed:
            return f"""Write a git commit message with title and detailed body for this git diff.

                Requirements:
                - First line: type: brief description (max 50 chars)
                - Second line: empty
                - Body: detailed explanation of changes (max 72 chars per line)
                - Types: feat, fix, docs, style, refactor, test, chore
                - Use present tense and imperative mood

                Format:
                feat: brief description

                - Detailed point 1
                - Detailed point 2
                - What was changed and why

                Git diff:
                {diff}

                Commit message:"""
        else:
            return f"""Write ONLY a single line commit message for this git diff.

                    Requirements:
                    - Use format: type: brief description
                    - Types: feat, fix, docs, style, refactor, test, chore
                    - Maximum 50 characters total
                    - No explanations, no markdown, no extra text
                    - Just the commit message line

                    Examples:
                    feat: add login validation
                    fix: handle null user data
                    docs: update setup guide

                    Git diff:
                    {diff}

                    Commit message:"""
        

class QwenAdapter(ModelAdapter):   
    def generate_commit_message(self, diff: str, detailed: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model_id,
            "messages": [
                {"role": "user", "content": self._build_prompt(diff, detailed)}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = requests.post(
            f"{self.config.api_base}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Qwen API error: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()


class OpenAIAdapter(ModelAdapter):
    def generate_commit_message(self, diff: str, detailed: bool = False) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model_id,
            "messages": [
                {"role": "user", "content": self._build_prompt(diff, detailed)}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = requests.post(
            f"{self.config.api_base}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()


class ModelFactory:    
    ADAPTERS = {
        "qwen": QwenAdapter,
        "openai": OpenAIAdapter
    }
    
    @classmethod
    def create_adapter(cls, config: ModelConfig) -> ModelAdapter:
        adapter_class = cls.ADAPTERS.get(config.provider)
        
        if not adapter_class:
            raise ValueError(f"Неподдерживаемый провайдер: {config.provider}")
        
        return adapter_class(config)