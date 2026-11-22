import json
import os
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


def installed_version():
    hyprland = find_program("Hyprland")
    if not hyprland:
        raise FileNotFoundError("Hyprland executable not found on PATH.")
    result = subprocess.run([hyprland, "--version"], text=True, capture_output=True, check=False)
    version = re.search(r"\bv?(\d+)\.(\d+)\.\d+", result.stdout)
    return tuple(map(int, version.groups())) if version else None


def bootstrap_path(app):
    version = installed_version()
    return app / ("bootstrap.conf" if version and version < (0, 55) else "bootstrap.lua")


def profile_config(primary, legacy):
    version = installed_version()
    if primary.suffix.lower() == ".lua" and version and version < (0, 55):
        if legacy:
            return legacy
        raise ValueError(f"{primary}: Hyprland {'.'.join(map(str, version))} requires a .conf profile.")
    return primary


def verify_config(config, env, log):
    hyprland = find_program("Hyprland")
    if not hyprland:
        raise FileNotFoundError("Hyprland executable not found on PATH.")
    options = subprocess.run(
        [hyprland, "--help"], env=env, text=True, capture_output=True, check=False, timeout=8,
    )
    if options.returncode:
        print(options.stderr or options.stdout, file=log, flush=True)
        return False
    if "--verify-config" not in options.stdout + options.stderr:
        print("This Hyprland build has no --verify-config. Starting without a preflight check.", file=log, flush=True)
        return True
    result = subprocess.run(
        [hyprland, "--verify-config", "--config", str(config)], env=env, stdout=log,
        stderr=subprocess.STDOUT, check=False, timeout=25,
    )
    if result.returncode and config.suffix.lower() == ".conf":
        print("Check whether your Hyprland version supports Hyprlang (.conf).", file=log, flush=True)
    return result.returncode == 0


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


def runtime_socket_path_too_long(runtime):
    longest_instance = "0" * 40 + "_" + "0" * 10 + "_" + "0" * 10
    return len(os.fsencode(Path(runtime) / "hypr" / longest_instance / ".socket2.sock")) >= 108


def control(instance, config, command=None):
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        raise FileNotFoundError("hyprctl executable not found on PATH.")
    if config.suffix.lower() == ".lua":
        args = [f"hl.dsp.exec_cmd({json.dumps(command, ensure_ascii=False)})"] if command else ["hl.dsp.exit()"]
    else:
        args = ["exec", command] if command else ["exit"]
    return subprocess.run(
        [hyprctl, "-i", instance, "dispatch", *args], text=True, capture_output=True, check=False, timeout=5,
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


def compositor_process(launcher):
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        return None
    try:
        result = subprocess.run(
            [hyprctl, "-j", "instances"], text=True, capture_output=True, check=False, timeout=2,
        )
        for instance in json.loads(result.stdout):
            pid = int(instance["pid"])
            if belongs_to(pid, launcher.pid):
                return instance["instance"], pid
    except (OSError, subprocess.TimeoutExpired, KeyError, TypeError, ValueError):
        pass
    return None


def wait_for_compositor(launcher, timeout=20):
    hyprctl = find_program("hyprctl")
    if not hyprctl:
        raise FileNotFoundError("hyprctl executable not found on PATH.")
    deadline = time.monotonic() + timeout
    while launcher.poll() is None and time.monotonic() < deadline:
        instance = compositor_process(launcher)
        if instance:
            identifier, _ = instance
            try:
                ready = subprocess.run(
                    [hyprctl, "-i", identifier, "version"], text=True, capture_output=True, check=False, timeout=2,
                )
                if ready.returncode == 0 and ready.stdout.strip():
                    return identifier
            except subprocess.TimeoutExpired:
                pass
        time.sleep(0.2)
    return None
