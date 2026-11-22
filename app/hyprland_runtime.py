import json
from pathlib import Path
import re
import shutil
import subprocess
import time


def find_program(*names):
    return next((path for name in names if (path := shutil.which(name))), None)


def compositor_command(config=None):
    wrapper = find_program("start-hyprland")
    program = wrapper or find_program("Hyprland")
    if not program:
        raise FileNotFoundError("Install Hyprland and make it available on PATH.")
    command = [program]
    if config is not None:
        if wrapper:
            command.append("--")
        command.extend(("--config", str(config)))
    return command


def bootstrap_path(app):
    hyprland = find_program("Hyprland")
    if not hyprland:
        raise FileNotFoundError("Hyprland executable not found on PATH.")
    result = subprocess.run([hyprland, "--version"], text=True, capture_output=True, check=False)
    version = re.search(r"\bv?(\d+)\.(\d+)\.\d+", result.stdout)
    uses_lua = not version or tuple(map(int, version.groups())) >= (0, 55)
    return app / ("bootstrap.lua" if uses_lua else "bootstrap.conf")


def focused_monitor():
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        return ""
    try:
        result = subprocess.run(
            [hyprctl, "-j", "monitors"], text=True, capture_output=True, check=False, timeout=2,
        )
        return next((monitor["name"] for monitor in json.loads(result.stdout) if monitor["focused"]), "")
    except (OSError, subprocess.TimeoutExpired, KeyError, TypeError, ValueError):
        return ""


def control(instance, config, command=None):
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        raise FileNotFoundError("hyprctl executable not found on PATH.")
    if config.suffix == ".lua":
        args = [f"hl.dsp.exec_cmd({json.dumps(command, ensure_ascii=False)})"] if command else ["hl.dsp.exit()"]
    else:
        args = ["exec", command] if command else ["exit"]
    return subprocess.run(
        [hyprctl, "-i", instance, "dispatch", *args], text=True, capture_output=True, check=False,
    )


def belongs_to(pid, launcher_pid):
    while pid > 1:
        if pid == launcher_pid:
            return True
        try:
            status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8", errors="replace")
            parent = re.search(r"^PPid:\s+(\d+)$", status, re.MULTILINE)
            if not parent:
                return False
            pid = int(parent[1])
        except OSError:
            return False
    return False


def wait_for_compositor(launcher, timeout=20):
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        raise FileNotFoundError("hyprctl executable not found on PATH.")
    deadline = time.monotonic() + timeout
    while launcher.poll() is None and time.monotonic() < deadline:
        result = subprocess.run([hyprctl, "-j", "instances"], text=True, capture_output=True, check=False)
        try:
            instances = json.loads(result.stdout)
            for instance in instances:
                if belongs_to(int(instance["pid"]), launcher.pid):
                    identifier = instance["instance"]
                    ready = subprocess.run(
                        [hyprctl, "-i", identifier, "version"], text=True, capture_output=True, check=False,
                    )
                    if ready.returncode == 0 and ready.stdout.strip():
                        return identifier
        except (KeyError, TypeError, ValueError):
            pass
        time.sleep(0.2)
    return None
