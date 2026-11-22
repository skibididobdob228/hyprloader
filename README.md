# Hyprloader

**English** · [Русский](README.ru.md)

Hyprloader opens a full-screen profile menu after you sign in. Each profile has its own Hyprland and Quickshell configuration. Use the arrow keys to move between profiles, Enter or a click to launch the selected profile, Esc to load the default, and `/` to search.

## Installation

You need Python 3.10 or newer, Hyprland with `hyprctl`, Quickshell, and `dbus-run-session` on your `PATH`. A Wayland-capable Rofi serves as the fallback menu. Hyprloader uses `start-hyprland` when it is available and launches `Hyprland` directly otherwise.

```sh
git clone https://github.com/skibididobdob228/hyprloader.git
cd hyprloader
./install.sh
~/.local/bin/hyprloader doctor
~/.local/bin/hyprloader preview
```

From a TTY, run `~/.local/bin/hyprloader session` to open the menu. To launch a specific profile directly, pass its ID as in `hyprloader session work`. **Super+Esc** closes the login menu and continues with the default profile.

For a login screen that discovers sessions from `/usr/local/share/wayland-sessions`, such as SDDM, install the system-wide launcher and then select **Hyprloader** on the login screen. Each user keeps their own profiles and theme. [SDDM session directories](https://github.com/sddm/sddm/blob/develop/data/man/sddm.conf.rst.in)

```sh
sudo ./install.sh --system
```

The `--sddm` flag remains available for installations that use the original SDDM profile hook.

Hyprloader uses a Hyprlang menu config for Hyprland versions before 0.55 and a Lua menu config from 0.55 onward. Use profile files that your installed Hyprland version can read. Hyprland 0.57 uses Lua configs. [Hyprland's Lua announcement](https://hypr.land/news/26_lua/) · [Hyprland 0.57 configuration](https://wiki.hypr.land/0.57.0/configuring/core/)

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

Put `hyprloader.json` at the archive root or in its top-level folder to set a display name, add an icon, or select the configuration files explicitly. Paths are relative to the manifest. You can specify only the fields you need. Any omitted entry files are detected automatically.

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

A ZIP with both `hyprland.lua` and `hyprland.conf` in the same directory can serve both config formats. Hyprloader uses the `.conf` on versions before 0.55. In a manifest with explicit file paths, you can set `hyprland_legacy` to the alternate `.conf` path.

When both configuration files sit inside a shared `.config` directory in the archive, Hyprloader sets `XDG_CONFIG_HOME` to that directory for the profile. You can set `config_home` in the manifest to select a different directory. `HYPRLOADER_PROFILE_DIR` points to the root of the extracted archive so configs and scripts can find bundled files. Paths hardcoded to `~/.config` still refer to the user's home configuration.

## Customizing the menu

Edit **`~/.config/hyprloader/theme.json`** and run `hyprloader preview`. Include only the settings you want to change.

```json
{
  "title": "Choose your desktop",
  "subtitle": "",
  "fontFamily": "Inter",
  "backgroundImage": "wallpapers/menu.jpg",
  "backgroundMode": "cover",
  "wallpaperDim": 0.3,
  "brandImage": "icons/brand.svg",
  "menuAlignment": "right",
  "menuWidth": 560,
  "panelPadding": 20,
  "rowHeight": 56,
  "rowGap": 8,
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
    "search": "#212736",
    "panel": "#cc181820",
    "panelBorder": "#323c52"
  },
  "icons": {
    "work": "icons/work.svg",
    "serpantinum:default": "icons/default.svg"
  },
  "defaultProfile": "work",
  "profileOrder": ["work", "serpantinum:default"],
  "timeoutSeconds": 5
}
```

| Setting | What it controls |
| --- | --- |
| `backgroundImage`, `backgroundMode` | Background image and how it fits the screen. Choose `cover`, `contain`, or `stretch` |
| `wallpaperDim`, `brandImage` | Backdrop dimming from 0 to 1 and a custom image beside the title |
| `monitor` | Screen name for the menu, for example `DP-1` |
| `menuAlignment`, `menuMargin` | Align the menu `left`, `center`, or `right`, and set the edge margin. `auto` uses the wide-screen horizontal offset |
| `panelPadding`, `panelRadius`, `colors.panel`, `colors.panelBorder` | Menu panel inset, corner radius, background, and border. Use `#AARRGGBB` for transparency |
| `showBackdrop` | Geometric backdrop when no background image is set |
| `showBrand`, `showDescription`, `showHints` | Hyprloader logo, profile descriptions, and keyboard hints |
| `showIcons`, `showSelectionMarker` | Profile icons and markers around the selected row |
| `menuWidth`, `rowHeight`, `rowRadius`, `iconSize`, `textSize` | Interface dimensions. Set `rowHeight` to `0` for automatic sizing |
| `rowGap`, `titleSize` | Spacing between entries and title size. Set `titleSize` to `0` for automatic sizing |
| `horizontalOffset`, `verticalOffset` | Menu offset from the center. The horizontal offset is a percentage on wide screens, and the vertical offset is in pixels |
| `icons` | SVG or PNG icons keyed by the profile IDs from `hyprloader list` |
| `defaultProfile`, `profileOrder` | Default profile ID and profile IDs that should appear first |
| `timeoutSeconds` | Delay before the built-in login menu launches the default. A keypress cancels the countdown. Set to `0` to disable it |
| `layout`, `rofiTheme` | Paths to a custom QML layout and fallback Rofi theme |

Wallpaper, icon, and layout paths are relative to the directory containing `theme.json`. Absolute paths and `~` are also supported. Hyprloader respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME`.

To redesign the whole menu, copy `app/menu.qml`, `app/ProfileIcon.qml`, and `app/Backdrop.qml` into your theme directory and set `layout` to your copy of `menu.qml`. The layout reads JSON from the file named by `HYPRLOADER_MENU_DATA`, writes the selected profile ID to the file named by `HYPRLOADER_MENU_CHOICE`, and exits Quickshell with `Qt.quit()`. The bundled layout serves as a fallback.

## When a profile fails to start

Run `hyprloader list` to find its ID, then run `hyprloader doctor work` with that ID. It checks the selected Hyprland file on builds that provide `--verify-config` and prints the Quickshell command. The last customized session attempt writes `session.log` and `quickshell.log` in `~/.local/state/hyprloader/logs/`. The first shows config verification and compositor startup, and the second shows Quickshell output, including QML errors.
