import os
from abc import ABC, abstractmethod
from typing import Optional

import requests

from core.models import ModelConfig
from core.prompt import get_commit_instruction


class ModelAdapter(ABC):

    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_key = self._get_api_key()
    
    @abstractmethod
    def generate_commit_message(
        self, 
        diff: str, 
        detailed: bool,
        commit_template: Optional[str],
        instruction: Optional[str]
    ) -> str: ...

    def _get_api_key(self) -> Optional[str]:
        env_var = f"GITK_{self.config.provider.upper()}_API_KEY"
        return os.getenv(env_var)

    def _build_prompt(
        self, 
        diff: str, 
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
        prompt = get_commit_instruction(
            diff=diff,
            detailed=detailed,
            commit_template=commit_template,
            instruction=instruction
        )
        return prompt
    

class OpenRouterAdapter(ModelAdapter):   

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_commit_message(
        self, 
        diff: str, 
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None
    ) -> str:
    
        data = {
            "model": self.config.model_id,
            "messages": [
                {"role": "user", "content": self._build_prompt(diff, detailed, commit_template, instruction)}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }

        response = requests.post(
            f"{self.config.api_base}/chat/completions",
            headers=self.headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"{self.config.provider} API error: {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()


class ModelFactory:    
    ADAPTERS = {
        "openrouter": OpenRouterAdapter
    }
    
    @classmethod
    def create_adapter(cls, config: ModelConfig) -> ModelAdapter:
        adapter_class = cls.ADAPTERS.get(config.provider)
        
        if not adapter_class:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        return adapter_class(config)