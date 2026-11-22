# Hyprloader

**English** · [Русский](README.ru.md)

Hyprloader opens a full-screen profile menu after you sign in. Each profile has its own Hyprland and Quickshell configuration. Use the arrow keys to move between profiles, Enter or a click to launch the selected profile, Esc to load the default, and `/` to search.

## Installation

You need Python 3.10 or newer, Hyprland with Lua configuration support, Quickshell, and `dbus-run-session`. Rofi serves as the fallback menu.

```sh
./install.sh
~/.local/bin/hyprloader preview
```

To integrate with the standard Hyprland session in SDDM, run `./install.sh --sddm` and choose **Hyprland** on the login screen. From a TTY, run `hyprloader session` to open the menu, or `hyprloader session work` to launch the `work` profile directly. If `~/.local/bin` is missing from your `PATH`, use the full path to the command. Press **Super+Esc** to close the login menu and continue with the default profile.

The base profile, labeled **Обычный** (Standard), loads your main Hyprland configuration. If Serpantinum is installed, its modes from `~/.config/serpantinum/modes` also appear in the list.

## Importing ZIP profiles

Drop a ZIP file into **`~/.config/hyprloader/imports/`**. Hyprloader extracts the archive and adds the profile the next time you open the menu or run `hyprloader list`. You can also import an archive by passing its path directly.

```sh
hyprloader import ~/Downloads/work.zip
hyprloader list
```

Hyprloader looks for `hyprland.lua` or `hyprland.conf` and `shell.qml` or `Shell.qml`. Keep the directory structure so relative references to scripts, modules, and images still work.

```text
work.zip
└── work/
    ├── hypr/
    │   └── hyprland.lua
    └── quickshell/
        └── shell.qml
```

Put `hyprloader.json` at the archive root or in its top-level folder to set a display name, add an icon, or select the configuration files explicitly. Paths are relative to the manifest. The `name`, `description`, and `icon` fields are optional.

```json
{
  "name": "Work",
  "description": "A profile with its own panel",
  "hyprland": "hypr/hyprland.lua",
  "quickshell": "quickshell/shell.qml",
  "icon": "assets/work.svg"
}
```

The imported profile is stored in `~/.local/share/hyprloader/profiles/<id>/`. Its ID comes from the ZIP filename. You can remove the ZIP from the import folder once it is installed. Importing a ZIP with the same name keeps the installed version. Give the archive a new name to install a second version alongside it. Edit the installed `profile.json` to rename the profile or change its description.

Hyprloader stores the entire archive in the profile directory. When you select the profile, it loads the two configuration files, including the scripts those files run. If a bundle ships with an installer, use it to set up any dependencies and files referenced by absolute paths. You can then register those configurations with `hyprloader add`.

```sh
hyprloader add work ~/.config/hypr-work/hyprland.lua ~/.config/quickshell/work/shell.qml --name "Work"
```

If Quickshell needs a custom launcher, set `quickshell_runner` to an executable path inside the archive. The launcher receives the absolute path to the QML file as its first argument.

## Customizing the menu

Edit **`~/.config/hyprloader/theme.json`** and run `hyprloader preview`. Include only the settings you want to change.

```json
{
  "title": "Choose your desktop",
  "subtitle": "",
  "fontFamily": "Inter",
  "backgroundImage": "wallpapers/menu.jpg",
  "backgroundMode": "cover",
  "menuWidth": 560,
  "rowHeight": 56,
  "rowRadius": 12,
  "iconSize": 30,
  "textSize": 21,
  "horizontalOffset": 0,
  "verticalOffset": -24,
  "colors": {
    "background": "#181820",
    "accent": "#9fbaff",
    "text": "#ffffff",
    "muted": "#bac1d0",
    "profile": "#d8dde8",
    "selected": "#323c52",
    "search": "#212736"
  },
  "icons": {
    "work": "icons/work.svg",
    "serpantinum:default": "icons/default.svg"
  }
}
```

| Setting | What it controls |
| --- | --- |
| `backgroundImage`, `backgroundMode` | Background image and how it fits the screen. Choose `cover`, `contain`, or `stretch` |
| `showBackdrop` | Geometric backdrop when no background image is set |
| `showBrand`, `showDescription`, `showHints` | Hyprloader logo, profile descriptions, and keyboard hints |
| `menuWidth`, `rowHeight`, `rowRadius`, `iconSize`, `textSize` | Interface dimensions. Set `rowHeight` to `0` for automatic sizing |
| `horizontalOffset`, `verticalOffset` | Menu offset from the center. The horizontal offset is a percentage on wide screens, and the vertical offset is in pixels |
| `icons` | SVG or PNG icons keyed by the profile IDs from `hyprloader list` |
| `layout`, `rofiTheme` | Paths to a custom QML layout and fallback Rofi theme |

Wallpaper, icon, and layout paths are relative to the directory containing `theme.json`. Absolute paths and `~` are also supported. Hyprloader respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME`.

To redesign the whole menu, copy `app/menu.qml`, `app/ProfileIcon.qml`, and `app/Backdrop.qml` into your theme directory and set `layout` to your copy of `menu.qml`. The layout reads JSON from the file named by `HYPRLOADER_MENU_DATA`, writes the selected profile ID to the file named by `HYPRLOADER_MENU_CHOICE`, and exits Quickshell with `Qt.quit()`. The bundled layout serves as a fallback.
