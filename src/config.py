"""Разбор параметров командной строки эмулятора оболочки.

Вариант 25, этап 2 (конфигурация).
Поддерживаются параметры пути к VFS и пути к стартовому скрипту,
а также отладочный вывод всех заданных параметров при запуске.
"""

import argparse  
from dataclasses import dataclass  
from typing import List, Optional

PROG_NAME = "shell_emulator"
VFS_HELP = "Путь к физическому расположению VFS."
SCRIPT_HELP = "Путь к стартовому скрипту эмулятора."
EMPTY_MARKER = "<не задан>"
DEBUG_HEADER = "Отладка: параметры запуска эмулятора"


@dataclass(frozen=True)
class Config:
    """Параметры запуска эмулятора."""

    vfs_path: Optional[str] = None  
    script_path: Optional[str] = None


def build_parser() -> argparse.ArgumentParser:
    """Собрать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="Эмулятор командной строки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "-v",
        "--vfs",
        dest="vfs_path",
        default=None,
        help=VFS_HELP,
    )
    parser.add_argument(
        "-s",
        "--script",
        dest="script_path",
        default=None,
        help=SCRIPT_HELP,
    )
    return parser


def parse_args(argv: Optional[List[str]] = None) -> Config:
    """Разобрать список аргументов в объект Config."""
    parser = build_parser()
    namespace = parser.parse_args(argv)
    return Config(
        vfs_path=namespace.vfs_path,
        script_path=namespace.script_path,
    )

  
def describe_path(value: Optional[str]) -> str:
    """Вернуть человекочитаемое представление пути."""
    return value if value else EMPTY_MARKER


def format_debug(config: Config) -> str:
    """Сформировать отладочный вывод всех параметров запуска."""
    lines = [
        DEBUG_HEADER,
        f"  VFS-путь    : {describe_path(config.vfs_path)}",
        f"  скрипт-путь : {describe_path(config.script_path)}",
    ]
    return "\n".join(lines)
