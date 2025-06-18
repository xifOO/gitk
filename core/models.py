from dataclasses import dataclass
from enum import Enum


@dataclass
class ModelConfig:
    name: str
    provider: str
    api_base: str
    model_id: str
    is_free: bool
    max_tokens: int = 150
    temperature: float = 0.4
    description: str = ""


class SupportedModel(Enum):
    
    QWEN_MODEL = ModelConfig(
        name="Qwen 2.5",
        provider="openrouter",
        api_base="https://openrouter.ai/api/v1",  
        model_id="qwen/qwen-2.5-72b-instruct:free", 
        is_free=True,
        description="Бесплатная модель от Qwen с лимитами."
    )

    MISTRALAI_MODEL = ModelConfig(
        name="Google Gemma",
        provider="openrouter",
        api_base="https://openrouter.ai/api/v1",
        model_id="google/gemma-3n-e4b-it:free",
        is_free=True,
        description="Поддерживает мультимодальные входные данные, что позволяет выполнять различные задачи, такие как генерация текста."
    )

    @classmethod
    def get_free_models(cls):
        return [model for model in cls if model.value.is_free]

    @classmethod
    def get_paid_models(cls):
        return [model for model in cls if not model.value.is_free]
    
