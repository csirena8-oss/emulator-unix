#!/usr/bin/env python3

import argparse
import datetime
import getpass
import os
import posixpath
import re
import shlex
import socket
import stat
import sys
import zipfile


class ShellError(Exception):
    """Ошибка выполнения команды."""


class VFS:
    """
    Виртуальная файловая система.

    Все файлы и каталоги хранятся в оперативной памяти.
    """

    def __init__(self):
        self.files = {}
        self.dirs = {"/"}
        self.modes = {}

    @staticmethod
    def normalize(path: str, cwd: str = "/") -> str:
        """
        Преобразует путь в нормализованный абсолютный путь.
        """

        if not path:
            return cwd

        if not path.startswith("/"):
            path = posixpath.join(cwd, path)

        result = posixpath.normpath(path)

        if not result.startswith("/"):
            result = "/" + result

        return result

    def add_dir(self, path: str):
        """
        Добавляет каталог и все его родительские каталоги.
        """

        path = self.normalize(path)
        self.dirs.add(path)

        parent = posixpath.dirname(path)

        if parent and parent != path:
            self.add_dir(parent)

    def add_file(self, path: str, data: bytes, mode: int = 0o644):
        """
        Добавляет файл в VFS.
        """

        path = self.normalize(path)

        self.files[path] = data
        self.modes[path] = mode

        parent = posixpath.dirname(path)
        self.add_dir(parent)

    def exists(self, path: str) -> bool:
        return path in self.files or path in self.dirs

    def is_file(self, path: str) -> bool:
        return path in self.files

    def is_dir(self, path: str) -> bool:
        return path in self.dirs

    def read_file(self, path: str) -> bytes:
        if not self.is_file(path):
            raise ShellError(f"cat: {path}: No such file")

        return self.files[path]

    def list_dir(self, path: str):
        """
        Возвращает список непосредственных элементов каталога.
        """

        if not self.is_dir(path):
            raise ShellError(f"ls: {path}: No such directory")

        result = set()

        for item in self.files:
            parent = posixpath.dirname(item)

            if parent == path:
                result.add(posixpath.basename(item))

        for item in self.dirs:
            if item == "/" or item == path:
                continue

            parent = posixpath.dirname(item)

            if parent == path:
                result.add(posixpath.basename(item))

        return sorted(result)

    @classmethod
    def from_zip(cls, filename: str):
        """
        Загружает виртуальную файловую систему из ZIP-архива.
        """

        vfs = cls()

        try:
            with zipfile.ZipFile(filename, "r") as archive:
                for info in archive.infolist():
                    name = "/" + info.filename.lstrip("/")
                    name = posixpath.normpath(name)

                    if info.is_dir() or info.filename.endswith("/"):
                        vfs.add_dir(name)
                        continue

                    data = archive.read(info.filename)

                    mode = (info.external_attr >> 16) & 0o777

                    if mode == 0:
                        mode = 0o644

                    vfs.add_file(name, data, mode)

        except FileNotFoundError:
            raise ShellError(f"vfs: file not found: {filename}")

        except zipfile.BadZipFile:
            raise ShellError(f"vfs: invalid ZIP archive: {filename}")

        except OSError as exc:
            raise ShellError(f"vfs: cannot load archive: {exc}")

        return vfs

    def save_zip(self, filename: str):
        """
        Сохраняет виртуальную файловую систему в ZIP-архив.
        """

        try:
            with zipfile.ZipFile(
                filename,
                "w",
                compression=zipfile.ZIP_DEFLATED
            ) as archive:

                for directory in sorted(self.dirs):
                    if directory == "/":
                        continue

                    name = directory.lstrip("/") + "/"

                    info = zipfile.ZipInfo(name)
                    info.external_attr = (0o755 & 0xFFFF) << 16

                    archive.writestr(info, b"")

                for path, data in sorted(self.files.items()):
                    name = path.lstrip("/")

                    info = zipfile.ZipInfo(name)

                    mode = self.modes.get(path, 0o644)
                    info.external_attr = (mode & 0xFFFF) << 16

                    archive.writestr(info, data)

        except OSError as exc:
            raise ShellError(f"vfs-save: cannot save archive: {exc}")


class Shell:
    def __init__(self, vfs: VFS):
        self.vfs = vfs
        self.cwd = "/"
        self.running = True

    def prompt(self) -> str:
        """
        Формирует приглашение командной строки.
        """

        username = getpass.getuser()
        hostname = socket.gethostname()

        display_cwd = "~" if self.cwd == "/" else self.cwd

        return f"{username}@{hostname}:{display_cwd}$ "

    def expand_environment(self, text: str) -> str:
        """
        Раскрывает переменные окружения:

        $HOME
        $USER
        ${HOME}
        """

        pattern = r"\$(\w+|\{[^}]+\})"

        def replace(match):
            name = match.group(1)

            if name.startswith("{") and name.endswith("}"):
                name = name[1:-1]

            return os.environ.get(name, "")

        return re.sub(pattern, replace, text)

    def parse(self, line: str):
        """
        Разбирает командную строку с учётом кавычек.
        """

        line = self.expand_environment(line)

        try:
            return shlex.split(line)

        except ValueError as exc:
            raise ShellError(f"parse error: {exc}")

    def execute(self, line: str):
        """
        Выполняет одну команду.
        """

        args = self.parse(line)

        if not args:
            return ""

        command = args[0]
        command_args = args[1:]

        commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "pwd": self.cmd_pwd,
            "date": self.cmd_date,
            "uniq": self.cmd_uniq,
            "chmod": self.cmd_chmod,
            "vfs-save": self.cmd_vfs_save,
            "exit": self.cmd_exit,
        }

        if command not in commands:
            raise ShellError(f"{command}: command not found")

        return commands[command](command_args)

    def cmd_exit(self, args):
        if args:
            raise ShellError("exit: too many arguments")

        self.running = False

        return ""

    def cmd_pwd(self, args):
        if args:
            raise ShellError("pwd: too many arguments")

        return self.cwd

    def cmd_cd(self, args):
        if len(args) > 1:
            raise ShellError("cd: too many arguments")

        target = args[0] if args else "/"
        path = self.vfs.normalize(target, self.cwd)

        if not self.vfs.is_dir(path):
            raise ShellError(f"cd: {target}: No such directory")

        self.cwd = path

        return ""

    def cmd_ls(self, args):
        long_format = False
        paths = []

        for arg in args:
            if arg == "-l":
                long_format = True

            elif arg.startswith("-"):
                raise ShellError(f"ls: invalid option: {arg}")

            else:
                paths.append(arg)

        if not paths:
            paths = ["."]

        output = []

        for item in paths:
            path = self.vfs.normalize(item, self.cwd)

            if self.vfs.is_file(path):
                names = [posixpath.basename(path)]

            elif self.vfs.is_dir(path):
                names = self.vfs.list_dir(path)

            else:
                raise ShellError(
                    f"ls: cannot access '{item}': "
                    "No such file or directory"
                )

            for name in names:
                full_path = posixpath.join(path, name)

                display_name = name

                if self.vfs.is_dir(full_path):
                    display_name += "/"

                if long_format:
                    mode = self.vfs.modes.get(full_path, 0o755)
                    permissions = stat.filemode(stat.S_IFREG | mode)
                    output.append(f"{permissions} {display_name}")

                else:
                    output.append(display_name)

        return "\n".join(output)

    def cmd_date(self, args):
        if args:
            raise ShellError(
                "date: this emulator does not support arguments"
            )

        return datetime.datetime.now().astimezone().strftime(
            "%a %b %d %H:%M:%S %Z %Y"
        )

    def cmd_uniq(self, args):
        if len(args) != 1:
            raise ShellError("uniq: usage: uniq FILE")

        path = self.vfs.normalize(args[0], self.cwd)
        data = self.vfs.read_file(path)

        lines = data.decode(
            "utf-8",
            errors="replace"
        ).splitlines()

        result = []
        previous = object()

        for line in lines:
            if line != previous:
                result.append(line)
                previous = line

        return "\n".join(result)

    def cmd_chmod(self, args):
        if len(args) < 2:
            raise ShellError("chmod: usage: chmod MODE FILE")

        mode_text = args[0]

        try:
            mode = int(mode_text, 8)

        except ValueError:
            raise ShellError(f"chmod: invalid mode: {mode_text}")

        if mode < 0 or mode > 0o777:
            raise ShellError(f"chmod: invalid mode: {mode_text}")

        for filename in args[1:]:
            path = self.vfs.normalize(filename, self.cwd)

            if not self.vfs.exists(path):
                raise ShellError(
                    f"chmod: cannot access '{filename}': No such file"
                )

            self.vfs.modes[path] = mode

        return ""

    def cmd_vfs_save(self, args):
        if len(args) != 1:
            raise ShellError("vfs-save: usage: vfs-save PATH")

        self.vfs.save_zip(args[0])

        return f"VFS saved to {args[0]}"

    def run_line(self, line: str, show_input: bool = False):
        """
        Выполняет одну строку скрипта или интерактивного ввода.
        """

        line = line.rstrip("\n")

        if not line.strip():
            return True

        if line.lstrip().startswith("#"):
            return True

        if show_input:
            print(f"{self.prompt()}{line}")

        try:
            output = self.execute(line)

            if output:
                print(output)

            return True

        except ShellError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return False

    def run_interactive(self):
        """
        Запускает интерактивный режим.
        """

        while self.running:
            try:
                line = input(self.prompt())

            except EOFError:
                print()
                break

            except KeyboardInterrupt:
                print()
                continue

            self.run_line(line)

    def run_script(self, filename: str):
        """
        Выполняет команды из текстового файла.
        """

        try:
            with open(filename, "r", encoding="utf-8") as script:
                for line_number, line in enumerate(script, start=1):
                    success = self.run_line(line, show_input=True)

                    if not success:
                        print(
                            f"script error: "
                            f"{filename}:{line_number}",
                            file=sys.stderr
                        )

                    if not self.running:
                        break

        except FileNotFoundError:
            raise ShellError(
                f"startup script not found: {filename}"
            )


def create_default_vfs():
    """
    Создаёт VFS, используемую без параметра --vfs.
    """

    vfs = VFS()

    vfs.add_dir("/home")
    vfs.add_dir("/home/user")
    vfs.add_dir("/tmp")

    vfs.add_file(
        "/README.txt",
        b"Virtual file system\n"
    )

    vfs.add_file(
        "/home/user/example.txt",
        b"one\none\ntwo\ntwo\nthree\n"
    )

    return vfs


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="UNIX-like shell emulator"
    )

    parser.add_argument(
        "--vfs",
        help="path to ZIP archive with virtual file system"
    )

    parser.add_argument(
        "--startup",
        help="path to startup script"
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("Emulator configuration:")
    print(f"  VFS: {args.vfs or '<default in-memory VFS>'}")
    print(
        "  Startup script: "
        f"{args.startup or '<interactive mode>'}"
    )

    try:
        if args.vfs:
            vfs = VFS.from_zip(args.vfs)
        else:
            vfs = create_default_vfs()

        shell = Shell(vfs)

        if args.startup:
            shell.run_script(args.startup)

        if shell.running and not args.startup:
            shell.run_interactive()

        return 0

    except ShellError as exc:
        print(f"fatal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
if __name__ == "__main__":
    sys.exit(main())
