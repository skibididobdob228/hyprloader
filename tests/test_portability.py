import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SHELL = "/bin/sh"


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="hyprloader portable ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bin = self.root / "tools"
        self.bin.mkdir()
        self.env = {
            **os.environ,
            "HOME": str(self.root),
            "PATH": f"{self.bin}{os.pathsep}{os.defpath}",
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }

    def fake(self, name, script):
        path = self.bin / name
        path.write_text(f"#!{SHELL}\n{script}", encoding="utf-8")
        path.chmod(0o755)
        return path

    def python_runtime(self, script):
        return subprocess.check_output(
            [sys.executable, "-c", script], cwd=ROOT / "app",
            env=self.env | {"PATH": str(self.bin)}, text=True,
        ).strip()

    def test_old_hyprland_uses_direct_launcher_and_legacy_bootstrap(self):
        self.fake("Hyprland", "printf '%s\\n' 'Hyprland, built from branch v0.54.3.'\n")
        result = self.python_runtime(
            'from pathlib import Path; from hyprland_runtime import *; import json; '
            'config = bootstrap_path(Path(".")); print(json.dumps(compositor_command(config)))',
        )
        self.assertEqual(result, f'["{self.bin}/Hyprland", "--config", "bootstrap.conf"]')

    def test_new_hyprland_uses_wrapper_and_lua_bootstrap(self):
        self.fake("Hyprland", "printf '%s\\n' 'Hyprland 0.57.2'\n")
        self.fake("start-hyprland", "exit 0\n")
        result = self.python_runtime(
            'from pathlib import Path; from hyprland_runtime import *; import json; '
            'config = bootstrap_path(Path(".")); print(json.dumps(compositor_command(config)))',
        )
        self.assertEqual(result, f'["{self.bin}/start-hyprland", "--", "--config", "bootstrap.lua"]')

    def test_dispatch_syntax_follows_config_extension(self):
        self.fake("hyprctl", "printf '%s\\n' \"$@\"\n")
        result = self.python_runtime(
            'from pathlib import Path; from hyprland_runtime import control; '
            'print(control("session", Path("hyprland.conf"), "qs --path shell.qml").stdout, end=""); '
            'print(control("session", Path("hyprland.lua")).stdout, end="")',
        )
        self.assertEqual(
            result.splitlines(),
            ["-i", "session", "dispatch", "exec", "qs --path shell.qml",
             "-i", "session", "dispatch", "hl.dsp.exit()"],
        )

    def test_direct_compositor_is_found_without_a_child_process(self):
        self.fake(
            "hyprctl",
            """if [ "$2" = instances ]; then
    printf '[{"pid":%s,"instance":"test"}]\\n' "$PORTABILITY_TEST_PID"
else
    printf '%s\\n' 'Hyprland 0.54.3'
fi
""",
        )
        result = self.python_runtime(
            'from hyprland_runtime import wait_for_compositor; from types import SimpleNamespace; '
            'import os; os.environ["PORTABILITY_TEST_PID"] = str(os.getpid()); '
            'print(wait_for_compositor(SimpleNamespace(pid=os.getpid(), poll=lambda: None), timeout=2))',
        )
        self.assertEqual(result, "test")

    def test_system_install_registers_a_session_without_user_files(self):
        staged_root = self.root / "image"
        env = self.env | {"DESTDIR": str(staged_root)}
        subprocess.run([ROOT / "install.sh", "--system"], env=env, check=True, capture_output=True)
        install = staged_root / "usr/local"
        entry = install / "share/wayland-sessions/hyprloader.desktop"
        self.assertIn("Exec=/usr/local/bin/hyprloader session", entry.read_text())
        self.assertEqual((install / "bin/hyprloader").readlink(), Path("/usr/local/share/hyprloader/hyprloader"))
        self.assertTrue((install / "share/hyprloader/bootstrap.conf").is_file())
        self.assertFalse((self.root / "config").exists())
        self.assertFalse((self.root / ".profile").exists())


if __name__ == "__main__":
    unittest.main()
