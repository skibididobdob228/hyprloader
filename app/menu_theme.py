import json
from pathlib import Path
import re


BOUNDS = {
    "menuWidth": (160, 2400),
    "rowHeight": (0, 240),
    "rowRadius": (0, 120),
    "iconSize": (8, 96),
    "textSize": (8, 80),
    "horizontalOffset": (-40, 40),
    "verticalOffset": (-600, 600),
}
IMAGE_MODES = {"cover", "contain", "stretch"}


def theme_file(base, name):
    if not isinstance(name, str) or not name:
        return None
    path = (base / Path(name).expanduser()).absolute()
    if not path.is_file():
        raise ValueError(f"файл темы недоступен: {path}")
    return path


def load_theme(app, config, report):
    theme = json.loads((app / "theme.json").read_text(encoding="utf-8"))
    path = config / "theme.json"
    try:
        changes = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(changes, dict):
            raise ValueError("ожидается объект JSON")
    except FileNotFoundError:
        return theme
    except (OSError, ValueError) as error:
        report(f"{path}: {error}")
        return theme

    for key in ("title", "subtitle", "fontFamily"):
        value = changes.get(key)
        if isinstance(value, str):
            theme[key] = value
    for key in ("showBackdrop", "showBrand", "showDescription", "showHints"):
        value = changes.get(key)
        if isinstance(value, bool):
            theme[key] = value
    for key, (minimum, maximum) in BOUNDS.items():
        value = changes.get(key)
        if (type(value) in (int, float) and minimum <= value <= maximum
                and (key != "rowHeight" or value == 0 or value >= 24)):
            theme[key] = value
    mode = changes.get("backgroundMode")
    if isinstance(mode, str) and mode in IMAGE_MODES:
        theme["backgroundMode"] = mode

    colors = changes.get("colors")
    if isinstance(colors, dict):
        for key in theme["colors"]:
            value = colors.get(key)
            if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", value):
                theme["colors"][key] = value

    for key in ("backgroundImage", "layout", "rofiTheme"):
        try:
            asset = theme_file(config, changes.get(key))
            if asset:
                theme[key] = asset.as_uri() if key == "backgroundImage" else str(asset)
        except (OSError, RuntimeError, ValueError) as error:
            report(f"{path}: {error}")

    icons = changes.get("icons")
    if isinstance(icons, dict):
        for key, value in icons.items():
            try:
                asset = theme_file(config, value)
                if asset:
                    theme["icons"][key] = asset.as_uri()
            except (OSError, RuntimeError, ValueError) as error:
                report(f"{path}: {error}")
    return theme
