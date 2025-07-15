import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from core.config.files import CacheFile
from core.exceptions import CacheFileError
from core.models import ModelConfig


def make_dummy_model():
    return ModelConfig(
        model_id="id1",
        name="model1",
        api_base="https://api",
        provider="test",
        description="",
        context_length=512,
        is_free=True,
    )


def test_save_models_success():
    dummy_models = [make_dummy_model()]
    m_dump = [m.model_dump() for m in dummy_models]

    m_open = mock_open()
    with patch("builtins.open", m_open), patch("json.dump") as mock_json_dump:
        cache = CacheFile("testprovider")
        cache.save_models(dummy_models)
        mock_json_dump.assert_called_once_with(m_dump, m_open(), ensure_ascii=False, indent=2)


def test_save_models_permission_error():
    dummy_models = [make_dummy_model()]
    m_open = mock_open()
    m_open.side_effect = PermissionError

    with patch("builtins.open", m_open):
        cache = CacheFile("testprovider")
        with pytest.raises(CacheFileError, match="Permission denied"):
            cache.save_models(dummy_models)


def test_save_models_os_error():
    dummy_models = [make_dummy_model()]
    m_open = mock_open()
    m_open.side_effect = OSError

    with patch("builtins.open", m_open):
        cache = CacheFile("testprovider")
        with pytest.raises(CacheFileError, match="OS error"):
            cache.save_models(dummy_models)


def test_save_models_json_decode_error():
    dummy_models = [make_dummy_model()]

    with patch("builtins.open", mock_open()), patch("json.dump", side_effect=json.JSONDecodeError("msg", "doc", 0)):
        cache = CacheFile("testprovider")
        with pytest.raises(CacheFileError, match="JSON encoding error"):
            cache.save_models(dummy_models)


def test_load_models_file_not_exists(monkeypatch):
    cache = CacheFile("testprovider")
    monkeypatch.setattr(Path, "exists", lambda self: False)

    result = cache.load_models()
    assert result == []


def test_load_models_success(monkeypatch):
    dummy_data = [
        {
            "model_id": "id1",
            "name": "m",
            "api_base": "b",
            "provider": "p",
            "description": "",
            "context_length": 512,
            "is_free": True,
        }
    ]

    cache = CacheFile("testprovider")
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "unlink", lambda self: None)

    m_open = mock_open(read_data=json.dumps(dummy_data))
    with patch("builtins.open", m_open):
        models = cache.load_models()

    assert all(isinstance(m, ModelConfig) for m in models)
    assert models[0].model_id == "id1"


def test_load_models_json_decode_error(monkeypatch):
    cache = CacheFile("testprovider")
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "unlink", lambda self: None)

    m_open = mock_open(read_data="invalid json")
    with patch("builtins.open", m_open):
        with pytest.raises(CacheFileError, match="Invalid JSON"):
            cache.load_models()


def test_load_models_permission_error(monkeypatch):
    cache = CacheFile("testprovider")
    monkeypatch.setattr(Path, "exists", lambda self: True)

    m_open = mock_open()
    m_open.side_effect = PermissionError

    with patch("builtins.open", m_open):
        with pytest.raises(CacheFileError, match="Permission denied"):
            cache.load_models()


def test_load_models_os_error(monkeypatch):
    cache = CacheFile("testprovider")
    monkeypatch.setattr(Path, "exists", lambda self: True)

    m_open = mock_open()
    m_open.side_effect = OSError

    with patch("builtins.open", m_open):
        with pytest.raises(CacheFileError, match="OS error"):
            cache.load_models()
