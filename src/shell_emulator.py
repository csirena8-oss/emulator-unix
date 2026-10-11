"""Эмулятор командной строки UNIX-подобной ОС.

Вариант 25, этапы 1 и 2. Реализованы REPL, раскрытие переменных  
окружения, обработка ошибок, заглушки команд ls и cd, а также  
разбор параметров командной строки, отладочный вывод параметров и  
выполнение стартового скрипта в режиме диалога.
"""

import getpass  
import os  
import re  
import socket  
import sys  
from functools import partial  
from typing import Callable, Dict, List, Optional, Tuple

from .config import Config, format_debug, parse_args  
from .script_runner import ScriptError, load_script, run_script

PROMPT_END = "$ "
HOME_SHORTCUT = "~"
MAX_CD_ARGS = 1  
EXIT_COMMAND = "exit"
ENV_PATTERN = re.compile(r"\$(\w+)|\$\{(\w+)\}")
SCRIPT_TAG = "script"

Handler = Callable[[List[str]], int]
Registry = Dict[str, Handler]


def current_user() -> str:
    """Вернуть имя пользователя реальной ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return os.environ.get("USER", "user")


def current_host() -> str:
    """Вернуть имя хоста реальной ОС."""
    return socket.gethostname() or "localhost"


def display_cwd() -> str:
    """Вернуть текущий каталог, сократив домашний путь до ~."""
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if not home or home == os.sep:
        return cwd  
    if cwd == home:
        return HOME_SHORTCUT  
    if cwd.startswith(home + os.sep):
        return HOME_SHORTCUT + cwd[len(home):]
    return cwd


def build_prompt() -> str:
    """Сформировать приглашение вида user@host:dir$."""
    user = current_user()
    host = current_host()
    return f"{user}@{host}:{display_cwd()}{PROMPT_END}"


def expand_env(token: str) -> str:
    """Раскрыть переменные окружения вида $NAME и ${NAME} в токене."""

    def replace(match: "re.Match") -> str:
        name = match.group(1) or match.group(2)
        return os.environ.get(name, "")

    return ENV_PATTERN.sub(replace, token)


def parse_line(line: str) -> Tuple[Optional[str], List[str]]:
    """Разобрать строку ввода на имя команды и список аргументов."""
    tokens = line.split()
    if not tokens:
        return None, []
    return tokens[0], [expand_env(item) for item in tokens[1:]]

  
def report_error(command: str, message: str) -> None:
    """Сообщить об ошибке выполнения команды в поток stderr."""
    print(f"{command}: {message}", file=sys.stderr)


def command_ls(args: List[str]) -> int:
    """Заглушка ls: вывести имя команды и её аргументы."""
    print("ls:", args)
    return 0


def command_cd(args: List[str]) -> int:
    """Заглушка cd: вывести имя команды и её аргументы."""
    if len(args) > MAX_CD_ARGS:
        report_error("cd", "слишком много аргументов")
        return 1  
    print("cd:", args)
    return 0


def build_registry() -> Registry:
    """Собрать таблицу поддерживаемых команд."""
    return {"ls": command_ls, "cd": command_cd}


def dispatch(registry: Registry, command: str, args: List[str]) -> None:
    """Найти и выполнить команду, сообщив об ошибке при её отсутствии."""
    handler = registry.get(command)
    if handler is None:
        report_error(command, "команда не найдена")
        return  
    handler(args)


def execute_line(line: str, registry: Registry) -> bool:
    """Выполнить одну строку ввода, вернуть False при выходе."""
    command, args = parse_line(line)
    if command is None:
        return True  
    if command == EXIT_COMMAND:
        return False  
    dispatch(registry, command, args)
    return True


def run_interactive(registry: Registry) -> None:
    """Запустить интерактивный цикл чтения-выполнения-печати."""
    while True:
        try:
            line = input(build_prompt())
        except EOFError:
            print()
            return  
        except KeyboardInterrupt:
            print()
            continue  
        if not execute_line(line, registry):
            return


def run_from_script(registry: Registry, commands: List[str]) -> None:
    """Выполнить команды из стартового скрипта."""
    executor = partial(execute_line, registry=registry)
    run_script(commands, executor, build_prompt)


def run_script_mode(script_path: str) -> int:
    """Загрузить стартовый скрипт и выполнить его команды."""
    try:
        commands = load_script(script_path)
    except ScriptError as exc:
        report_error(SCRIPT_TAG, str(exc))
        return 1  
    print("Эмулятор оболочки ОС. Режим стартового скрипта.")
    run_from_script(build_registry(), commands)
    return 0


def run_interactive_mode() -> int:
    """Запустить интерактивный режим эмулятора."""
    print("Эмулятор оболочки ОС. Введите 'exit' для выхода.")
    run_interactive(build_registry())
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа: разбор параметров, отладка, выбор режима."""
    config: Config = parse_args(argv)
    print(format_debug(config))
    if config.script_path:
        return run_script_mode(config.script_path)
    return run_interactive_mode()


if __name__ == "__main__":
    sys.exit(main())
