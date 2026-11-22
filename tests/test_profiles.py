import json
import os
from pathlib import Path
import stat
import subprocess
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "app/hyprloader"
CONFIGS = {
    "bundle/.config/hypr/hyprland.lua": "hl.monitor({output = ''})",
    "bundle/.config/quickshell/work/Shell.qml": "import Quickshell\nShellRoot {}\n",
    "bundle/.config/quickshell/work/assets/background.txt": "asset",
}


class ImportTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.config = self.home / "config/hyprloader"
        self.inbox = self.config / "imports"
        self.installed = self.home / "data/hyprloader/profiles"
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.config.parent),
            "XDG_DATA_HOME": str(self.installed.parent.parent),
        }

    def run_loader(self, *args, check=True):
        return subprocess.run(
            [LAUNCHER, *args], env=self.env, text=True, capture_output=True, check=check,
        )

    def write_zip(self, name, entries):
        self.inbox.mkdir(parents=True, exist_ok=True)
        with ZipFile(path := self.inbox / name, "w") as archive:
            for entry, content in entries.items():
                archive.writestr(entry, content)
        return path

    def test_drop_zip_preserves_structure_and_survives_removal(self):
        path = self.write_zip("Work profile.ZIP", CONFIGS)
        self.assertIn("work-profile\tWork profile", self.run_loader("list").stdout)
        profile = self.installed / "work-profile"
        info = json.loads((profile / "profile.json").read_text())
        self.assertTrue((profile / info["hyprland"]).is_file())
        self.assertTrue((profile / info["quickshell"]).is_file())
        self.assertEqual((profile / "files" / list(CONFIGS)[-1]).read_text(), "asset")
        path.unlink()
        self.assertIn("work-profile\tWork profile", self.run_loader("list").stdout)

    def test_manifest_selects_entry_and_preserves_executable(self):
        runner = ZipInfo("bundle/scripts/launch")
        runner.create_system = 3
        runner.external_attr = (stat.S_IFREG | 0o755) << 16
        archive = self.write_zip("choice.zip", CONFIGS | {
            "bundle/alternate/shell.qml": "import Quickshell\nShellRoot {}\n",
            "bundle/hyprloader.json": json.dumps({
                "name": "Choice",
                "hyprland": ".config/hypr/hyprland.lua",
                "quickshell": "alternate/shell.qml",
                "quickshell_runner": "scripts/launch",
                "icon": "icon.svg",
            }),
            "bundle/icon.svg": "<svg/>",
            runner: "#!/bin/sh\nexit 0\n",
        })
        self.assertIn("choice", self.run_loader("import", archive).stdout)
        profile = self.installed / "choice"
        info = json.loads((profile / "profile.json").read_text())
        self.assertEqual(info["quickshell"], "files/bundle/alternate/shell.qml")
        self.assertEqual(info["icon"], "files/bundle/icon.svg")
        self.assertTrue(os.access(profile / info["quickshell_runner"], os.X_OK))
        self.assertIn("choice\tChoice", self.run_loader("list").stdout)

    def test_bad_zip_does_not_block_menu_and_can_be_retried(self):
        path = self.write_zip("retry.zip", CONFIGS)
        path.write_bytes(b"unfinished")
        result = self.run_loader("list")
        self.assertIn("retry.zip", result.stderr)
        self.assertIn("serpantinum:default", result.stdout)
        self.assertFalse((self.installed / "retry").exists())
        self.write_zip("retry.zip", CONFIGS)
        self.assertIn("retry\tretry", self.run_loader("list").stdout)

    def test_path_escape_leaves_no_import(self):
        self.write_zip("escape.zip", CONFIGS | {"../outside": "unexpected"})
        result = self.run_loader("list")
        self.assertIn("недопустимый путь", result.stderr)
        self.assertFalse((self.installed / "escape").exists())
        self.assertFalse(list(self.installed.glob(".import-*")))

    def test_symlink_escape_leaves_no_import(self):
        link = ZipInfo("bundle/escape")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.write_zip("symlink.zip", CONFIGS | {link: "../../outside"})
        result = self.run_loader("list")
        self.assertIn("выходит за пределы профиля", result.stderr)
        self.assertFalse((self.installed / "symlink").exists())

    def test_ambiguous_zip_requires_manifest(self):
        self.write_zip("ambiguous.zip", CONFIGS | {"bundle/other/shell.qml": ""})
        result = self.run_loader("list")
        self.assertIn("Укажи нужный путь в hyprloader.json", result.stderr)
        self.assertFalse((self.installed / "ambiguous").exists())

    def test_concurrent_imports_register_once(self):
        archive = self.write_zip("parallel.zip", CONFIGS)
        command = [LAUNCHER, "import", archive]
        with subprocess.Popen(command, env=self.env, text=True, stdout=subprocess.PIPE) as first:
            second = self.run_loader("import", archive)
            output, _ = first.communicate(timeout=10)
        self.assertEqual(first.returncode, 0)
        self.assertIn("уже добавлен", output + second.stdout)
        self.assertEqual(self.run_loader("list").stdout.count("parallel\tparallel"), 1)


if __name__ == "__main__":
    unittest.main()
