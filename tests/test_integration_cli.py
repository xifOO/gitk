from typing import cast

import pytest
import questionary

from core.cli.cli import ApiKeyCLI, ModelsCLI, TemplatesCLI
from core.config.config import EnvFile
from core.models import SupportedModel
from core.templates import Template


class DummySelect:
    def __init__(self, return_value):
        self.return_value = return_value

    def ask(self):
        return self.return_value


class DummyPrompt:
    def __init__(self, return_value):
        self.return_value = return_value

    def ask(self):
        return self.return_value


def test_templatescli_select_from_existing(monkeypatch, tmp_path):
    cli = TemplatesCLI()
    dummy_template = Template(directory=tmp_path, name="dummy", content="test content")

    monkeypatch.setattr(cli.templates_dir, "all_templates", lambda: [dummy_template])

    select_calls = []

    def fake_select(*args, **kwargs):
        if not select_calls:
            select_calls.append(1)
            return DummySelect("list")
        return DummySelect(dummy_template)

    monkeypatch.setattr(questionary, "select", fake_select)

    selected = cli.setup_interactive()
    assert isinstance(selected, Template)
    assert selected == dummy_template


def test_templatescli_default_template(monkeypatch):
    cli = TemplatesCLI()
    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect("default"))

    template = cli.setup_interactive()
    assert isinstance(template, Template)

    default_template = cli.templates_dir.default_template
    if callable(default_template):
        default_template = default_template()

    assert template.name == default_template.name
    assert template.content == default_template.content


def test_templatescli_select_from_existing_no_templates(monkeypatch):
    cli = TemplatesCLI()
    monkeypatch.setattr(cli.templates_dir, "all_templates", lambda: [])
    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect("list"))

    with pytest.raises(FileNotFoundError):
        cli.setup_interactive()


def test_templatescli_create_custom(monkeypatch):
    cli = TemplatesCLI()
    inputs = iter(["line 1", "line 2", ""])

    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect("custom"))
    monkeypatch.setattr(cli, "_get_content_from_input", lambda: "\n".join([next(inputs) for _ in range(3)]))
    monkeypatch.setattr(cli, "_get_name_from_input", lambda: "valid_name")

    template = cli.setup_interactive()
    assert isinstance(template, Template)
    assert template.name == "valid_name"
    assert "line 1" in template.content


def test_templatescli_create_custom_invalid_name(monkeypatch):
    cli = TemplatesCLI()

    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect("custom"))
    monkeypatch.setattr(cli, "_get_content_from_input", lambda: "content")
    monkeypatch.setattr(questionary, "text", lambda *a, **k: DummyPrompt("invalid name!"))

    with pytest.raises(ValueError):
        cli.setup_interactive()


def test_templatescli_load_from_file(monkeypatch, tmp_path):
    cli = TemplatesCLI()
    file = tmp_path / "template.txt"
    file.write_text("file template content")

    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect("file"))
    monkeypatch.setattr(questionary, "path", lambda *a, **k: DummySelect(str(file)))

    template = cli.setup_interactive()
    assert isinstance(template, Template)
    assert "file template content" in template.content


def test_modelscli_select_model(monkeypatch):
    cli = ModelsCLI()
    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummySelect(SupportedModel.get_free_models()[0]))

    selected = cli.select_model()
    assert selected in SupportedModel


class DummyEnvFile:
    def __init__(self):
        self._storage = {"API_KEY_TESTPROVIDER": "existing_key"}

    def get_env_var_name(self, provider):
        return f"API_KEY_{provider.upper()}"

    def key_exists(self, env_var):
        return env_var in self._storage

    def read_key(self, env_var):
        return self._storage.get(env_var)

    def write_key(self, env_var, key):
        self._storage[env_var] = key


def test_apikeycli_return_existing_key(monkeypatch):
    cli = ApiKeyCLI()
    dummy_env = DummyEnvFile()
    cli.env_file = cast(EnvFile, dummy_env)

    model = SupportedModel.get_free_models()[0]
    env_var = dummy_env.get_env_var_name(model.value.provider)
    dummy_env.write_key(env_var, "existing_key")

    monkeypatch.setattr(questionary, "confirm", lambda *a, **k: DummySelect(False))

    key = cli.setup_api_key(model)
    assert key == "existing_key"


def test_apikeycli_replace_key(monkeypatch):
    cli = ApiKeyCLI()
    dummy_env = DummyEnvFile()
    dummy_env.write_key("API_KEY_TESTPROVIDER", "old_key")
    cli.env_file = cast(EnvFile, dummy_env)

    monkeypatch.setattr(questionary, "confirm", lambda *a, **k: DummySelect(True))
    monkeypatch.setattr(questionary, "text", lambda *a, **k: DummySelect("new_key"))

    key = cli.setup_api_key(SupportedModel.get_free_models()[0])
    assert key == "new_key"


def test_apikeycli_get_new_key(monkeypatch):
    cli = ApiKeyCLI()
    dummy_env = DummyEnvFile()
    cli.env_file = cast(EnvFile, dummy_env)

    monkeypatch.setattr(questionary, "text", lambda *a, **k: DummySelect("some_api_key"))

    key = cli.setup_api_key(SupportedModel.get_free_models()[0])
    assert key == "some_api_key"
