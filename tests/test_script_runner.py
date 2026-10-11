"""Тесты выполнения стартовых скриптов (Вариант 25, этап 2)."""

import pytest

from src import script_runner as sr


def test_is_comment_true() -> None:
    """Строка, начинающаяся с '#', является комментарием."""
    assert sr.is_comment("# comment")


def test_is_comment_indented() -> None:
    """Комментарий может быть с отступом в начале строки."""
    assert sr.is_comment("   # note")


def test_is_comment_false() -> None:
    """Строка с командой не является комментарием."""
    assert not sr.is_comment("ls -l")


def test_is_blank_empty() -> None:
    """Пустая строка определяется как пустая."""
    assert sr.is_blank("")


def test_is_blank_spaces() -> None:
    """Строка из пробелов определяется как пустая."""
    assert sr.is_blank("   \t")


def test_is_blank_false() -> None:
    """Строка с командой не пустая."""
    assert not sr.is_blank("cd /tmp")


def test_clean_lines_removes_comments_and_blanks() -> None:
    """Комментарии и пустые строки удаляются."""
    source = ["# header\n", "\n", "ls\n", "   # note\n", "cd /tmp\n"]
    assert sr.clean_lines(source) == ["ls", "cd /tmp"]


def test_load_script_success(tmp_path) -> None:
    """Существующий файл читается и очищается."""
    path = tmp_path / "demo.esh"
    path.write_text("# c\nls\n", encoding="utf-8")
    assert sr.load_script(str(path)) == ["ls"]


def test_load_script_missing() -> None:
    """Отсутствующий файл приводит к ScriptError."""
    with pytest.raises(sr.ScriptError):
        sr.load_script("no_such_file.esh")


def test_run_script_executes_and_stops(capsys) -> None:
    """Команды выполняются, при False выполнение прекращается."""
    seen = []

    def execute(line: str) -> bool:
        seen.append(line)
        return line != "stop"

    sr.run_script(["ls", "stop", "cd"], execute, lambda: "p$ ")
    assert seen == ["ls", "stop"]
    assert "p$ ls" in capsys.readouterr().out


def test_run_script_echoes_prompt(capsys) -> None:
    """Перед каждым шагом выводится приглашение и команда."""
    sr.run_script(["ls"], lambda line: True, lambda: "u@h:~$ ")
    assert "u@h:~$ ls" in capsys.readouterr().out
