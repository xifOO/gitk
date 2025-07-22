import pytest

from core.models import Config, ModelConfig


def test_modelconfig_build_model_config_valid():
    config_data = {
        "model_config_data": {
            "name": "TestModel",
            "provider": "testprovider",
            "api_base": "https://api.test.com",
            "model_id": "test/model-id",
            "is_free": False,
            "context_length": 1000,
            "temperature": 0.7,
            "description": "test description",
        }
    }

    config = ModelConfig.build_model_config(config_data)

    assert config.name == "TestModel"
    assert config.provider == "testprovider"
    assert config.api_base == "https://api.test.com"
    assert config.model_id == "test/model-id"
    assert not config.is_free
    assert config.context_length == 1000
    assert config.temperature == 0.7
    assert config.description == "test description"


def test_modelconfig_build_model_config_missing():
    with pytest.raises(ValueError, match="Model configuration is missing"):
        ModelConfig.build_model_config({})


def test_config_build_config(tmp_path):
    selected_model = ModelConfig(
        name="TestModel",
        provider="testprovider",
        api_base="https://api.test.com",
        model_id="test/model-id",
        is_free=True,
        context_length=2048,
        temperature=0.4,
        description="desc",
    )
    path = tmp_path / "template.txt"
    path.write_text("some content")

    config = Config.build_config(selected_model, path)

    assert config.model == selected_model.name
    assert config.provider == selected_model.provider
    assert config.model_config_data == selected_model
    assert str(path) == config.commit_template_path


def test_config_save_and_load(tmp_path):
    selected_model = ModelConfig(
        name="TestModel",
        provider="testprovider",
        api_base="https://api.test.com",
        model_id="test/model-id",
        is_free=True,
        context_length=2048,
        temperature=0.4,
        description="desc",
    )
    path = tmp_path / "template.txt"
    path.write_text("some content")

    config = Config.build_config(selected_model, path)
    config_path = tmp_path / "config.yaml"
    config.save_to_file(config_path)

    loaded_config = Config.from_yaml(config_path)

    assert loaded_config.model == config.model
    assert loaded_config.provider == config.provider
    assert loaded_config.model_config_data.model_id == config.model_config_data.model_id
    assert loaded_config.commit_template_path == config.commit_template_path
