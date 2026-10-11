"""Выполнение стартовых скриптов эмулятора оболочки.

Вариант 25, этап 2: стартовый скрипт содержит команды эмулятора,
поддерживает комментарии языка Python ('#') и пустые строки.
При выполнении на экран выводятся как команды (в виде диалога),
так и результаты их выполнения.
"""

from typing import Callable, Iterable, List

COMMENT_PREFIX = "#"
SCRIPT_ERROR_PREFIX = "script"

LineExecutor = Callable[[str], bool]
PromptBuilder = Callable[[], str]


class ScriptError(Exception):
    """Ошибка выполнения стартового скрипта."""


def is_comment(line: str) -> bool:
    """Проверить, начинается ли строка с комментария."""
    return line.lstrip().startswith(COMMENT_PREFIX)


def is_blank(line: str) -> bool:
    """Проверить, является ли строка пустой или из пробелов."""
    return not line.strip()


def clean_lines(raw_lines: Iterable[str]) -> List[str]:
    """Убрать из строк комментарии и пустые строки."""
    result: List[str] = []
    for raw in raw_lines:
        line = raw.rstrip("\n")
        if is_blank(line) or is_comment(line):
            continue  
        result.append(line)
    return result


def load_script(path: str) -> List[str]:
    """Прочитать и очистить стартовый скрипт."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return clean_lines(handle.readlines())
    except FileNotFoundError as exc:
        raise ScriptError(f"файл не найден: {path}") from exc  
    except OSError as exc:
        raise ScriptError(f"ошибка чтения: {exc}") from exc


def run_script(commands: Iterable[str], execute: LineExecutor,
               prompt_builder: PromptBuilder) -> None:
    """Выполнить команды скрипта, имитируя диалог с пользователем."""
    for command in commands:
        print(f"{prompt_builder()}{command}")
        if not execute(command):
            return
