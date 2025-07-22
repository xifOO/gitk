from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.config.paths import CacheDirectory
from core.exceptions import CacheDirectoryError


def test_init_cache_dir_success():
    fake_config = MagicMock()
    fake_path = MagicMock(spec=Path)
    fake_path.exists.return_value = False
    fake_path.is_file.return_value = False

    fake_config.config_dir.return_value.__truediv__.return_value.__truediv__.return_value = (
        fake_path
    )

    with patch("core.config.paths.ConfigDirectory", return_value=fake_config):
        with patch(
            "core.config.paths.BaseDirectory.__init__", return_value=None
        ) as mock_base_init:
            cache_dir = CacheDirectory(config_dir=fake_config)  # noqa: F841
            mock_base_init.assert_called_once_with(fake_path, CacheDirectoryError)


def test_init_cache_dir_raises_if_cache_path_is_file():
    fake_config = MagicMock()
    fake_path = MagicMock(spec=Path)
    fake_path.exists.return_value = True
    fake_path.is_file.return_value = True
    fake_config.config_dir.return_value.__truediv__.return_value.__truediv__.return_value = (
        fake_path
    )

    with patch("core.config.paths.ConfigDirectory", return_value=fake_config):
        with patch("core.config.paths.BaseDirectory.__init__") as mock_base_init:
            mock_base_init.side_effect = CacheDirectoryError(
                "Cache path exists as file"
            )
            with pytest.raises(CacheDirectoryError) as excinfo:
                CacheDirectory(config_dir=fake_config)
            assert isinstance(excinfo.value.__cause__, CacheDirectoryError)
            assert "Cache path exists as file" in str(excinfo.value.__cause__)


def test_ensure_calls_mkdir():
    mock_path = MagicMock(spec=Path)
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    cache_directory._path = mock_path

    cache_directory.ensure()
    mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_cache_file_path_returns_path():
    mock_path = MagicMock(spec=Path)
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    cache_directory._path = mock_path
    cache_directory.ensure_exists = MagicMock(return_value=mock_path)

    result = cache_directory.get_cache_file_path("provider")
    expected = mock_path / "provider_models.json"
    assert result == expected


@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("simpleName", "simpleName"),
        ("name with spaces", "name with spaces"),
        ('unsafe<>:"/\\|?*chars', "unsafe_chars"),
        ("___multiple__underscores__", "multiple_underscores"),
        (" " * 10 + "name" + " " * 10, "name"),
        ("a" * 100, "a" * 85),
    ],
)
def test_sanitize_filename(input_name, expected):
    cache_directory = CacheDirectory.__new__(CacheDirectory)
    cache_directory._path = MagicMock()
    result = cache_directory._sanitize_filename(input_name)
    assert result == expected
