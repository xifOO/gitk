from enum import Enum
from pathlib import Path
from typing import Any, Dict, Self

import yaml
from pydantic import BaseModel, field_validator


class ModelConfig(BaseModel, validate_assignment = True):
    name: str
    provider: str 
    api_base: str
    model_id: str
    is_free: bool
    max_tokens: int = 150
    temperature: float = 0.4
    description: str = ""

    @field_validator('name', 'provider', 'api_base', 'model_id')
    def strip_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @classmethod
    def build_model_config(cls, config_data: Dict[str, Any]) -> Self:
        model_json = config_data.get("model_config_data", {})
        
        if not model_json:
            raise ValueError("Model configuration is missing")

        return cls(
            **model_json
        )    


class SupportedModel(Enum):
    
    QWEN_MODEL = ModelConfig(
        name="Qwen 2.5",
        provider="openrouter",
        api_base="https://openrouter.ai/api/v1",  
        model_id="qwen/qwen-2.5-72b-instruct:free", 
        is_free=True,
        description="Free model from Qwen with limits."
    )

    GEMMA_MODEL = ModelConfig(
        name="Google Gemma",
        provider="openrouter",
        api_base="https://openrouter.ai/api/v1",
        model_id="google/gemma-3n-e4b-it:free",
        is_free=True,
        description="Supports multimodal input, enabling various tasks such as text generation."
    )

    @classmethod
    def get_free_models(cls) -> list["SupportedModel"]:
        return [model for model in cls if model.value.is_free]

    @classmethod
    def get_paid_models(cls) -> list["SupportedModel"]:
        return [model for model in cls if not model.value.is_free]
    

class Config(BaseModel, validate_assignment = True):
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
    def build_config(cls, selected_model: SupportedModel, template_path: Path) -> Self:
        model_config = selected_model.value

        return cls(
            model=model_config.name,
            provider=model_config.provider,
            model_config_data=model_config, 
            commit_template_path=str(template_path)
        )
    
    @classmethod
    def from_yaml(cls, file_path: Path) -> "Config":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        return cls(
            model=raw_data["model"],
            provider=raw_data["provider"],
            model_config_data=ModelConfig(**raw_data["model_config_data"]),
            commit_template_path=raw_data["commit_template_path"]
        )

    def save_to_file(self, file_path: Path) -> None:
        with open(file_path, 'w', encoding="utf-8") as f:
            yaml.safe_dump(self.model_dump(), f, sort_keys=False, allow_unicode=True)