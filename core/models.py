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
        provider="qwen",
        api_base="https://openrouter.ai/api/v1",  
        model_id="qwen/qwen-2.5-72b-instruct:free", 
        is_free=True,
        description="Бесплатная модель от Qwen с лимитами."
    )

    OPENAI_GPT4 = ModelConfig(
        name="GPT-4 Turbo",
        provider="openai",
        api_base="https://api.openai.com/v1",
        model_id="gpt-4-turbo-preview", 
        is_free=False,
        description="Лучшее качество генерации коммитов."
    )

    CLAUDE_SONNET = ModelConfig(
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        api_base="https://api.anthropic.com",
        model_id="claude-3-5-sonnet-20241022",
        is_free=False,
        description="Отличное понимание кода и контекста."
    )

    GEMINI_PRO = ModelConfig(
        name="Gemini Pro",
        provider="google",
        api_base="https://generativelanguage.googleapis.com/v1beta",
        model_id="gemini-pro",
        is_free=False,
        description="Хорошее соотношение цена/качество."
    )

    @classmethod
    def get_free_models(cls):
        return [model for model in cls if model.value.is_free]

    @classmethod
    def get_paid_models(cls):
        return [model for model in cls if not model.value.is_free]
    
