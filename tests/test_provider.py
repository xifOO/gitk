from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
import requests

from core.exceptions import APIError
from core.models import ModelConfig, Provider
from tests.test_cache_file import make_dummy_model


class MockRawModel:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockRawModel":
        return cls()

    def to_model_config(self) -> ModelConfig:
        return make_dummy_model()


def test_provider_uses_cache_file():
    cached_models = [make_dummy_model()]

    mock_cache_file = MagicMock()
    mock_cache_file.load_models.return_value = cached_models

    provider = Provider(
        name="test",
        api_base="https://api.test.com",
        api_key="test_key",
        raw_model_cls=MockRawModel,
        cache_file=mock_cache_file,
    )

    models = list(provider.fetch_models())
    assert models == cached_models
    assert not mock_cache_file.save_models.called


def test_provider_falls_back_to_api_when_cache_empty():
    api_models = [make_dummy_model()]

    mock_cache_file = MagicMock()
    mock_cache_file.load_models.return_value = []

    provider = Provider(
        name="test",
        api_base="https://api.test.com",
        api_key="test_key",
        raw_model_cls=MockRawModel,
        cache_file=mock_cache_file,
    )

    with patch.object(provider, "_fetch_models_from_api", return_value=api_models):
        models = list(provider.fetch_models())
        assert models == api_models
        mock_cache_file.save_models.assert_called_once_with(api_models)


def test_provider_api_error_handling():
    mock_cache_file = MagicMock()
    mock_cache_file.load_models.return_value = []

    provider = Provider(
        name="test",
        api_base="https://api.test.com",
        api_key="test_key",
        raw_model_cls=MockRawModel,
        cache_file=mock_cache_file,
    )

    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(APIError, match="Connection error"):
            list(provider.fetch_models())


def test_filter_fn_works_correctly():
    models = [
        make_dummy_model(model_id="chat-model", name="Chat Model"),
        make_dummy_model(model_id="other-model", name="Other Model"),
    ]

    mock_cache_file = MagicMock()
    mock_cache_file.load_models.return_value = models

    provider = Provider(
        name="test",
        api_base="https://api.test.com",
        api_key="test_key",
        raw_model_cls=MockRawModel,
        cache_file=mock_cache_file,
    )

    filtered = list(provider.fetch_models(filter_fn=lambda m: "chat" in m.model_id))

    assert len(filtered) == 1
    assert filtered[0].model_id == "chat-model"
