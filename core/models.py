from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Protocol,
    Self,
    Type,
    TypeVar,
)

import requests
import yaml
from pydantic import BaseModel, ValidationError, field_validator

from core.config.files import CacheFile
from core.exceptions import APIError, ModelConfigError


class ModelConfig(BaseModel):
    name: str
    provider: str 
    api_base: str
    model_id: str
    is_free: bool
    context_length: int
    temperature: float = 0.4
    description: str = ""

    @field_validator('name', 'provider', 'api_base', 'model_id')
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @classmethod
    def build_model_config(cls, config_data: Dict[str, Any]) -> Self:
        try:
            model_json = config_data.get("model_config_data", {})
            
            if not model_json:
                raise ValueError("Model configuration is missing")

            return cls(**model_json)    
        
        except ValidationError as e:
            raise ModelConfigError("Invalid model configuration", cause=e) from e
    
    class PydanticConfig:
        validate_assignment = True

    
class Config(BaseModel):
    model: str
    provider: str
    model_config_data: ModelConfig
    commit_template_path: str

    @field_validator('model', 'provider', 'commit_template_path')
    @classmethod
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @classmethod
    def build_config(cls, selected_model: ModelConfig, template_path: Path) -> Self:
        try:
            return cls(
                model=selected_model.name,
                provider=selected_model.provider,
                model_config_data=selected_model, 
                commit_template_path=str(template_path)
            )
        except ValidationError as e:
            raise ModelConfigError("Invalid config data", cause=e) from e
    
    @classmethod
    def from_yaml(cls, file_path: Path) -> Self:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = yaml.safe_load(f)
            
            if not raw_data:
                raise ModelConfigError("Config file is empty or invalid")

            return cls(
                model=raw_data["model"],
                provider=raw_data["provider"],
                model_config_data=ModelConfig(**raw_data["model_config_data"]),
                commit_template_path=raw_data["commit_template_path"]
            )
        except FileNotFoundError:
            raise
        except yaml.YAMLError as e:
            raise ModelConfigError("Invalid YAML format", cause=e) from e
        except ValidationError as e:
            raise ModelConfigError("Invalid config structure", cause=e) from e

    def save_to_file(self, file_path: Path) -> None:
        try:
            with open(file_path, 'w', encoding="utf-8") as f:
                yaml.safe_dump(self.model_dump(), f, sort_keys=False, allow_unicode=True)
        except PermissionError as e:
            raise ModelConfigError(f"Permission denied writing to {file_path}") from e
        except OSError as e:
            raise ModelConfigError(f"OS error writing to {file_path}", cause=e) from e
        except Exception as e:
            raise ModelConfigError(f"Failed to save config to {file_path}", cause=e) from e
    
    class PydanticConfig:
        validate_assignment = True


class RawModel(Protocol): 
    @classmethod
    def from_dict(cls, data: Dict) -> Self: ... 
    def to_model_config(self) -> ModelConfig: ... 


T = TypeVar("T", bound=RawModel)


@dataclass
class Provider(Generic[T]):
    name: str
    api_base: str
    api_key: str
    raw_model_cls: Type[T]
    cache_file: CacheFile

    def fetch_models(
        self,
        filter_fn: Optional[Callable[[ModelConfig], bool]] = None
    ) -> Generator[ModelConfig, None, None]:
        cached_models = self.cache_file.load_models()

        if cached_models:
            models = cached_models
        else:
            models = list(self._fetch_models_from_api())
            self.cache_file.save_models(models)

        for model in models:
            if not filter_fn or filter_fn(model):
                yield model

    def _fetch_models_from_api(self) -> Generator[ModelConfig, None, None]:
        try:
            response = requests.get(
                f"{self.api_base}/models",
                headers= {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )

            if response.status_code == 401:
                raise APIError("Invalid API key")

            response.raise_for_status()

            try:
                response_data = response.json()
            except ValueError as e:
                raise APIError("Invalid JSON response", cause=e) from e
            
            models_data = response_data.get("data", [])
        
        except requests.ConnectTimeout as e:
            raise APIError("Connection timeout - API server is not responding") from e
        except requests.ConnectionError as e:
            raise APIError("Connection error - unable to reach API server") from e
        except requests.RequestException as e:
            raise APIError("Request failed", cause=e) from e
        except Exception as e:
            raise APIError("Unexpected error during API request", cause=e) from e

        for model_dict in models_data:
            raw = self.raw_model_cls.from_dict(model_dict)
            yield raw.to_model_config()
    
    def get_top_models(self, filter_fn: Optional[Callable[[ModelConfig], bool]] = None, free_count: int = 5, paid_count: int = 5) -> Dict[str, List[ModelConfig]]:
        free_models = []
        paid_models = []

        for model_config in self.fetch_models(filter_fn):
            if model_config.is_free:
                free_models.append(model_config)
            else:
                paid_models.append(model_config)
        
        free_models.sort(key=self._calculate_model_score, reverse=True)
        paid_models.sort(key=self._calculate_model_score, reverse=True)

        return {
            'free': free_models[:free_count],
            'paid': paid_models[:paid_count]
        }
    
    def _calculate_model_score(self, model: ModelConfig) -> float:
        score = 0.0

        if model.context_length:
            if model.context_length >= 1000000: 
                score += 20
            elif model.context_length >= 200000:  
                score += 15
            elif model.context_length >= 100000:  
                score += 10
            elif model.context_length >= 32000:  
                score += 5
            else:
                score += model.context_length / 10000 
    
        model_name_lower = model.name.lower()
        model_id_lower = model.model_id.lower()
        
        top_tier_models = {
            'gpt-4': 25,
            'claude': 25,
            'gemini': 20,
            'llama-3': 20,
            'mixtral': 18,
            'qwen': 15,
            'deepseek': 15,
            'phi-3': 12,
            'mistral': 12,
        }

        for indicator, points in top_tier_models.items():
            if indicator in model_name_lower or indicator in model_id_lower:
                score += points
                break
        
        size_indicators = {
            '405b': 15,
            '300b': 14,
            '175b': 13,
            '70b': 12,
            '34b': 10,
            '13b': 8,
            '8b': 7,
            '7b': 6,
            '3b': 4,
            '1b': 2,
        }

        for size, points in size_indicators.items():
            if size in model_name_lower or size in model_id_lower:
                score += points
                break

        low_quality_indicators = ['test', 'experimental', 'preview', 'alpha', 'beta', 'dev']

        for indicator in low_quality_indicators:
            if indicator in model_name_lower or indicator in model_id_lower:
                score -= 5
        
        if '2024' in model.description or '2025' in model.description:
            score += 5
        
        return score


@dataclass
class OpenRouterRawModel:
    id: str
    name: str
    description: str 
    context_length: int
    pricing_prompt: float

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        try:
            return cls(
                id=data["id"],
                name=data.get("name", data["id"]),
                description=data.get("description", ""),
                context_length=data.get("context_length", 4096),
                pricing_prompt=float(data.get("pricing", {}).get("prompt", 0.0))
            )
        except (ValueError, TypeError, KeyError) as e:
            raise ValueError(f"Invalid model data: {e}") from e

    def is_free(self) -> bool:
        return ":free" in self.id or self.pricing_prompt == 0.0
    
    def to_model_config(self) -> ModelConfig:
        return ModelConfig(
            name=self.name,
            provider="openrouter",
            api_base="https://openrouter.ai/api/v1",
            model_id=self.id,
            is_free=self.is_free(),
            context_length=self.context_length,
            temperature=0.4,
            description=self.description.strip()
        )