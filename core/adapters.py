import os
from abc import ABC, abstractmethod
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from core.exceptions import (
    MissingAPIKeyError,
    ModelGenerationError,
    ProviderAPIError,
    UnsupportedProviderError,
)
from core.models import ModelConfig
from core.prompt import get_commit_instruction


class ModelAdapter(ABC):

    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise MissingAPIKeyError(
                f"API key for provider '{self.config.provider}' not found. "
                f"Make sure environment variable GITK_{self.config.provider.upper()}_API_KEY is set."
            )

    @abstractmethod
    def generate_commit_message(
        self,
        diff: str,
        detailed: bool,
        commit_template: Optional[str],
        instruction: Optional[str],
    ) -> str: ...

    def _get_api_key(self) -> Optional[str]:
        env_var = f"GITK_{self.config.provider.upper()}_API_KEY"
        return os.getenv(env_var)

    def _build_prompt(
        self,
        diff: str,
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> str:
        try:
            prompt = get_commit_instruction(
                diff=diff,
                detailed=detailed,
                commit_template=commit_template,
                instruction=instruction,
            )
            return prompt
        except Exception as e:
            raise ModelGenerationError("Failed to build prompt", cause=e) from e


class OpenRouterAdapter(ModelAdapter):

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.session = self._create_retryable_session()

    def _create_retryable_session(self) -> requests.Session:
        session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[408, 500, 502, 503, 504],
            allowed_methods=["POST"],
            raise_on_status=False,
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retries,
        )

        session.mount("https://", adapter)
        return session

    def generate_commit_message(
        self,
        diff: str,
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None,
    ) -> str:

        data = {
            "model": self.config.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": self._build_prompt(
                        diff, detailed, commit_template, instruction
                    ),
                }
            ],
            "temperature": self.config.temperature,
        }

        try:
            response = self.session.post(
                f"{self.config.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if e.response is None:
                raise ProviderAPIError(
                    "Network error - check connection", cause=e
                ) from e

            error_messages = {
                401: "Authentication failed - check API key",
                429: "Rate limit exceeded",
                403: "Access denied - check API key permissions",
            }
            message = error_messages.get(
                e.response.status_code, "Unexpected error during API request"
            )
            raise ProviderAPIError(f"{self.config.provider}: {message}", cause=e) from e

        try:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except (KeyError, ValueError) as e:
            raise ModelGenerationError("Invalid API response format", cause=e) from e

    def __del__(self) -> None:
        if hasattr(self, "session"):
            self.session.close()


class ModelFactory:
    ADAPTERS = {"openrouter": OpenRouterAdapter}

    @classmethod
    def create_adapter(cls, config: ModelConfig) -> ModelAdapter:
        adapter_class = cls.ADAPTERS.get(config.provider)

        if not adapter_class:
            raise UnsupportedProviderError(f"Unsupported provider: {config.provider}")

        return adapter_class(config)
