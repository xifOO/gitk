from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.config.paths import CacheDirectory
from core.exceptions import CacheDirectoryError


def test_init_cache_dir_success():
    fake_base_dir = MagicMock(spec=Path)
    fake_cache_dir = MagicMock(spec=Path)

    fake_base_dir.exists.return_value = False
    fake_base_dir.is_file.return_value = False
    fake_base_dir.__truediv__.return_value = fake_cache_dir

    fake_cache_dir.exists.return_value = False
    fake_cache_dir.is_file.return_value = False

    with patch("core.config.paths.ConfigDirectory.__init__", return_value=None):
        with patch("core.config.paths.ConfigDirectory.config_dir", return_value=fake_base_dir):
            cache_dir = CacheDirectory()
            assert cache_dir._cache_dir == fake_cache_dir
            fake_cache_dir.exists.assert_called_once()


def test_init_cache_dir_raises_if_cache_path_is_file():
    fake_base_dir = MagicMock(spec=Path)
    fake_cache_dir = MagicMock(spec=Path)

    fake_base_dir.__truediv__.return_value = fake_cache_dir

    fake_cache_dir.exists.return_value = True
    fake_cache_dir.is_file.return_value = True

    with patch("core.config.paths.ConfigDirectory.__init__", return_value=None):
        with patch("core.config.paths.ConfigDirectory.config_dir", return_value=fake_base_dir):
            cache_dir = CacheDirectory.__new__(CacheDirectory)
            cache_dir._config_dir = MagicMock(config_dir=MagicMock(return_value=fake_base_dir))
            cache_dir._cache_dir = fake_cache_dir
            with pytest.raises(CacheDirectoryError) as excinfo:
                CacheDirectory.__init__(cache_dir)
            assert "Cache path exists as file" in str(excinfo.value)


def test_init_cache_dir_wraps_config_error():
    class DummyConfigError(Exception):
        pass

    def raise_error():
        raise DummyConfigError()

    with patch("core.config.paths.ConfigDirectory.__init__", return_value=None):
        with patch("core.config.paths.ConfigDirectory.config_dir", side_effect=raise_error):
            with pytest.raises(CacheDirectoryError) as excinfo:
                CacheDirectory()
            assert "Failed to initialize cache directory" in str(excinfo.value)
            assert isinstance(excinfo.value.__cause__, DummyConfigError)


def test_ensure_calls_mkdir():
    mock_cache_dir = MagicMock(spec=Path)
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    cache_directory._cache_dir = mock_cache_dir

    cache_directory.ensure()
    mock_cache_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_cache_file_path_returns_path():
    mock_cache_dir = Path("/fake/cache/dir")
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    cache_directory._cache_dir = mock_cache_dir

    path = cache_directory.get_cache_file_path("provider")
    assert path == mock_cache_dir / "provider_models.json"


@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("simpleName", "simpleName"),
        ("name with spaces", "name with spaces"),
        ("unsafe<>:\"/\\|?*chars", "unsafe_chars"),
        ("___multiple__underscores__", "multiple_underscores"),
        (" " * 10 + "name" + " " * 10, "name"),
        ("a" * 100, "a" * 85),
    ]
)
def test_sanitize_filename(input_name, expected):
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    result = cache_directory._sanitize_filename(input_name)
    assert result == expected
