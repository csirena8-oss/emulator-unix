"""Тесты модуля конфигурации (Вариант 25, этап 2)."""

from src import config as cfg


def test_parse_args_empty() -> None:
    """Без аргументов оба пути равны None."""
    parsed = cfg.parse_args([])
    assert parsed.vfs_path is None  
    assert parsed.script_path is None


def test_parse_args_vfs_only() -> None:
    """Задан только путь к VFS."""
    parsed = cfg.parse_args(["--vfs", "/tmp/vfs.zip"])
    assert parsed.vfs_path == "/tmp/vfs.zip"
    assert parsed.script_path is None


def test_parse_args_script_only() -> None:
    """Задан только путь к стартовому скрипту."""
    parsed = cfg.parse_args(["--script", "demo.esh"])
    assert parsed.script_path == "demo.esh"
    assert parsed.vfs_path is None


def test_parse_args_short_flags() -> None:
    """Поддерживаются короткие флаги -v и -s."""
    parsed = cfg.parse_args(["-v", "a.zip", "-s", "b.esh"])
    assert parsed.vfs_path == "a.zip"
    assert parsed.script_path == "b.esh"


def test_describe_path_empty() -> None:
    """Путь None отображается как маркер незаданности."""
    assert cfg.describe_path(None) == cfg.EMPTY_MARKER


def test_describe_path_value() -> None:
    """Непустой путь возвращается как есть."""
    assert cfg.describe_path("/x") == "/x"


def test_format_debug_empty() -> None:
    """Отладочный вывод содержит оба маркера незаданности."""
    text = cfg.format_debug(cfg.Config())
    assert text.count(cfg.EMPTY_MARKER) == 2  
    assert cfg.DEBUG_HEADER in text


def test_format_debug_full() -> None:
    """Отладочный вывод содержит оба заданных пути."""
    text = cfg.format_debug(cfg.Config("v.zip", "s.esh"))
    assert "v.zip" in text
    assert "s.esh" in text
