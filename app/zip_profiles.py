from contextlib import contextmanager
import fcntl
import hashlib
import json
import lzma
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile
import zlib


ARCHIVE_ERRORS = (OSError, RuntimeError, ValueError, EOFError, BadZipFile, lzma.LZMAError, zlib.error)


def archive_id(archive):
    slug = re.sub(r"[^a-z0-9_-]+", "-", archive.stem.lower()).strip("_-")
    if slug:
        return slug[:80]
    return "profile-" + hashlib.sha256(archive.stem.encode()).hexdigest()[:12]


def archive_path(name):
    path = PurePosixPath(name.replace("\\", "/"))
    if not path.parts or path.is_absolute() or ".." in path.parts or re.match(r"^[a-zA-Z]:", path.parts[0]):
        raise ValueError(f"недопустимый путь в ZIP: {name}")
    return path


def extract_archive(archive, folder):
    links = []
    with ZipFile(archive) as zipped:
        for info in zipped.infolist():
            path = archive_path(info.filename)
            if path.parts[0] == "__MACOSX":
                continue
            target = folder / path
            mode = info.external_attr >> 16 if info.create_system == 3 else 0
            if info.is_dir() or stat.S_ISDIR(mode):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if stat.S_ISLNK(mode):
                link = zipped.read(info).decode("utf-8")
                if not link or Path(link).is_absolute():
                    raise ValueError(f"недопустимая ссылка в ZIP: {path}")
                links.append((target, link))
                continue
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError(f"неподдерживаемый тип файла в ZIP: {path}")
            with zipped.open(info) as source, target.open("xb") as destination:
                shutil.copyfileobj(source, destination)
            if mode & 0o111:
                target.chmod(target.stat().st_mode | (mode & 0o111))

    for target, link in links:
        target.symlink_to(link)
    for target, _ in links:
        if not target.resolve().is_relative_to(folder):
            raise ValueError(f"ссылка в ZIP выходит за пределы профиля: {target.relative_to(folder)}")


def find_entry(folder, names):
    candidates = sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.name.lower() in names
        and not any(part.startswith(".") and part != ".config" for part in p.relative_to(folder).parts)
    )
    parents = {p.parent for p in candidates}
    if len(parents) == 1:
        return min(candidates, key=lambda p: names.index(p.name.lower()))
    if not candidates:
        raise ValueError(f"в ZIP отсутствует {' или '.join(names)}")
    raise ValueError(f"в ZIP несколько файлов {' / '.join(names)}. Укажи нужный путь в hyprloader.json")


def read_manifest(folder):
    root = folder / "hyprloader.json"
    manifests = [root] if root.is_file() else sorted(folder.glob("*/hyprloader.json"))
    if not manifests:
        return None, {}
    if len(manifests) > 1:
        raise ValueError("в ZIP несколько hyprloader.json")
    manifest = manifests[0]
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("в hyprloader.json ожидается объект JSON")
    return manifest, data


def archive_profile(folder, archive):
    manifest, data = read_manifest(folder)
    profile = {key: data[key] for key in ("name", "description") if key in data}
    profile.setdefault("name", archive.stem)
    profile["archive"] = archive.name
    entries = {
        "hyprland": ("hyprland.lua", "hyprland.conf"),
        "quickshell": ("shell.qml",),
        "quickshell_runner": (),
        "icon": (),
    }
    for key, names in entries.items():
        if manifest is not None:
            if key not in data and not names:
                continue
            value = data.get(key)
            if not isinstance(value, str) or not value:
                raise ValueError(f"укажи относительный путь {key} в hyprloader.json")
            path = manifest.parent / archive_path(value)
        elif names:
            path = find_entry(folder, names)
        else:
            continue
        if not path.is_file():
            raise ValueError(f"файл для {key} отсутствует: {path.relative_to(folder)}")
        if key == "hyprland" and path.suffix not in (".lua", ".conf"):
            raise ValueError("hyprland должен указывать на .lua или .conf")
        if key == "quickshell" and path.suffix != ".qml":
            raise ValueError("quickshell должен указывать на .qml")
        if key == "quickshell_runner" and not path.stat().st_mode & 0o111:
            raise ValueError("quickshell_runner должен быть исполняемым")
        profile[key] = str(Path("files") / path.relative_to(folder))
    return profile


@contextmanager
def profile_store_lock(installed):
    installed.mkdir(parents=True, exist_ok=True)
    with (installed / ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def import_archive(archive, installed, manual):
    if archive.suffix.lower() != ".zip" or not archive.is_file():
        raise ValueError("ожидается файл .zip")
    identifier = archive_id(archive)
    target = installed / identifier
    with profile_store_lock(installed):
        if (manual / f"{identifier}.json").exists():
            raise ValueError(f"профиль {identifier} уже зарегистрирован вручную")
        if target.exists():
            existing = json.loads((target / "profile.json").read_text(encoding="utf-8"))
            if existing.get("archive") == archive.name:
                return identifier, False
            raise ValueError(f"профиль {identifier} уже существует. Переименуй ZIP")
        with TemporaryDirectory(prefix=".import-", dir=installed) as directory:
            staging = Path(directory).absolute()
            files = staging / "files"
            files.mkdir()
            extract_archive(archive, files)
            profile = archive_profile(files, archive)
            (staging / "profile.json").write_text(
                json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
            )
            staging.rename(target)
    return identifier, True
