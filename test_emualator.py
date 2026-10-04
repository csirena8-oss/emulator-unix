import unittest

from emulator import Shell, VFS, create_default_vfs, ShellError


class EmulatorTests(unittest.TestCase):

    def setUp(self):
        self.shell = Shell(create_default_vfs())

    def test_pwd(self):
        self.assertEqual(self.shell.execute("pwd"), "/")

    def test_cd(self):
        self.shell.execute("cd /home/user")
        self.assertEqual(self.shell.cwd, "/home/user")

    def test_cd_error(self):
        with self.assertRaises(ShellError):
            self.shell.execute("cd /missing")

    def test_ls(self):
        result = self.shell.execute("ls /")
        self.assertIn("README.txt", result)
        self.assertIn("home", result)

    def test_uniq(self):
        result = self.shell.execute("uniq /home/user/example.txt")
        self.assertEqual(result, "one\ntwo\nthree")

    def test_chmod(self):
        self.shell.execute("chmod 755 /home/user/example.txt")
        self.assertEqual(
            self.shell.vfs.modes["/home/user/example.txt"],
            0o755
        )

    def test_unknown_command(self):
        with self.assertRaises(ShellError):
            self.shell.execute("unknown-command")


if __name__ == "__main__":
    unittest.main()
