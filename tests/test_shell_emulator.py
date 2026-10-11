"""Тесты эмулятора оболочки (Вариант 25, этапы 1 и 2)."""

import os

import pytest

from src import shell_emulator as sh


def test_current_user_returns_string() -> None:
    """Имя пользователя — непустая строка."""
    user = sh.current_user()
    assert isinstance(user, str)
    assert user


def test_current_host_returns_string() -> None:
    """Имя хоста — непустая строка."""
    host = sh.current_host()
    assert isinstance(host, str)
    assert host


def test_display_cwd_home_shortcut(monkeypatch) -> None:
    """Домашний каталог отображается как тильда."""
    home = os.path.expanduser("~")
    monkeypatch.setattr(os, "getcwd", lambda: home)
    assert sh.display_cwd() == sh.HOME_SHORTCUT


def test_display_cwd_outside_home(monkeypatch) -> None:
    """Путь вне дома выводится полностью."""
    monkeypatch.setattr(os, "getcwd", lambda: os.sep)
    assert sh.display_cwd() == os.sep


def test_build_prompt_contains_parts() -> None:
    """Приглашение содержит @ и завершающий символ."""
    prompt = sh.build_prompt()
    assert "@" in prompt  
    assert prompt.endswith(sh.PROMPT_END)


def test_expand_env_simple(monkeypatch) -> None:
    """Простая подстановка $NAME."""
    monkeypatch.setenv("MY_VAR", "value")
    assert sh.expand_env("$MY_VAR") == "value"


def test_expand_env_braces(monkeypatch) -> None:
    """Подстановка ${NAME}."""
    monkeypatch.setenv("MY_VAR", "value")
    assert sh.expand_env("${MY_VAR}") == "value"


def test_expand_env_unknown() -> None:
    """Неизвестная переменная раскрывается в пустую строку."""
    assert sh.expand_env("$NO_SUCH_VAR_12345") == ""


def test_parse_line_empty() -> None:
    """Пустая строка — нет команды и аргументов."""
    assert sh.parse_line("") == (None, [])


def test_parse_line_with_args(monkeypatch) -> None:
    """Аргументы раскрываются и возвращаются списком."""
    monkeypatch.setenv("F", "file.txt")
    assert sh.parse_line("ls $F -l") == ("ls", ["file.txt", "-l"])


def test_command_ls_prints(capsys) -> None:
    """ls выводит имя команды и аргументы, код возврата 0."""
    assert sh.command_ls(["-l"]) == 0  
    assert "ls:" in capsys.readouterr().out


def test_command_cd_ok(capsys) -> None:
    """cd с одним аргументом возвращает 0."""
    assert sh.command_cd(["/tmp"]) == 0  
    assert "cd:" in capsys.readouterr().out


def test_command_cd_too_many(capsys) -> None:
    """cd с лишними аргументами сообщает об ошибке."""
    assert sh.command_cd(["a", "b"]) == 1  
    assert "cd:" in capsys.readouterr().err


def test_dispatch_unknown(capsys) -> None:
    """Неизвестная команда сообщает об ошибке в stderr."""
    sh.dispatch({}, "nope", [])
    assert "не найдена" in capsys.readouterr().err


def test_execute_line_continues() -> None:
    """execute_line возвращает True на обычной команде."""
    assert sh.execute_line("ls", sh.build_registry())


def test_execute_line_exit() -> None:
    """execute_line возвращает False на команде exit."""
    assert not sh.execute_line("exit", sh.build_registry())


def test_execute_line_blank() -> None:
    """Пустая строка не завершает цикл."""
    assert sh.execute_line("", sh.build_registry())


def test_run_script_mode_runs_commands(tmp_path, capsys) -> None:
    """Режим скрипта выполняет команды из файла."""
    path = tmp_path / "demo.esh"
    path.write_text("# note\nls -l\n", encoding="utf-8")
    assert sh.run_script_mode(str(path)) == 0  
    assert "ls:" in capsys.readouterr().out


def test_run_script_mode_missing(capsys) -> None:
    """Отсутствующий скрипт завершает работу с кодом 1."""
    assert sh.run_script_mode("no.esh") == 1  
    assert "script:" in capsys.readouterr().err


def test_main_script_mode(tmp_path, capsys) -> None:
    """main в режиме скрипта возвращает 0."""
    path = tmp_path / "s.esh"
    path.write_text("exit\n", encoding="utf-8")
    assert sh.main(["--script", str(path)]) == 0  
    out = capsys.readouterr().out  
    assert "Отладка" in out  
    assert str(path) in out


def test_main_interactive_exit(monkeypatch) -> None:
    """main в интерактивном режиме читает строки из stdin."""

    def fake_input(*args):
        raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    assert sh.main([]) == 0
