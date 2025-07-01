import tempfile
from pathlib import Path

from core.templates import Template, TemplateDirectory


def test_template_save_and_load():
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir)
        t = Template(path, "test_template", "Hello, world!")
        t.save()

        assert t.exists()
        assert t.load_content() == "Hello, world!"

def test_template_directory_create_and_get():
    with tempfile.TemporaryDirectory() as tempdir:
        td = TemplateDirectory()
        td.config_dir = Path(tempdir)
        td._templates_dir = Path(tempdir) / "templates"
        td.ensure()

        template = td.create_template("my", "test content")
        assert template.exists()
        assert template.load_content() == "test content"

        loaded = td.get_template("my")
        assert loaded.exists()
