#!/bin/sh
set -eu

with_sddm=0
case "${1:-}" in
    "") ;;
    --sddm) with_sddm=1; shift ;;
    *) printf '%s\n' "Usage: ./install.sh [--sddm]" >&2; exit 2 ;;
esac
if [ "$#" -ne 0 ]; then
    printf '%s\n' "Usage: ./install.sh [--sddm]" >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
app="${XDG_DATA_HOME:-$HOME/.local/share}/hyprloader"
config="${XDG_CONFIG_HOME:-$HOME/.config}/hyprloader"
bin="$HOME/.local/bin"

mkdir -p "$app" "$bin" "$config/imports" "$config/profiles.d"
staging=$(mktemp -d "$app/.install.XXXXXXXX")
trap 'rm -rf -- "$staging"' EXIT
trap 'exit 1' HUP INT TERM

for file in Backdrop.qml ProfileIcon.qml bootstrap.lua menu.qml menu.rasi menu_theme.py theme.json zip_profiles.py; do
    install -m 644 "$source_dir/app/$file" "$staging/$file"
    mv -fT -- "$staging/$file" "$app/$file"
done
install -m 755 "$source_dir/app/hyprloader" "$staging/hyprloader"
mv -fT -- "$staging/hyprloader" "$app/hyprloader"
ln -sfnT -- "$app/hyprloader" "$bin/hyprloader"
if [ ! -e "$config/theme.json" ] && [ ! -L "$config/theme.json" ]; then
    (set -C; cat "$source_dir/app/theme.json" > "$config/theme.json")
fi

if [ "$with_sddm" -eq 1 ] && ! grep -Fq 'set -- "$HOME/.local/bin/hyprloader" session' "$HOME/.profile" 2>/dev/null; then
    cat >> "$HOME/.profile" <<'PROFILE'

if [ "$0" = /usr/share/sddm/scripts/wayland-session ] &&
   [ "$#" -eq 1 ] && [ "$1" = /usr/bin/start-hyprland ] &&
   [ "${HYPRLOADER_SKIP:-0}" != 1 ] &&
   [ -x "$HOME/.local/bin/hyprloader" ]; then
    set -- "$HOME/.local/bin/hyprloader" session
fi
PROFILE
fi

printf '%s\n' "Hyprloader: $bin/hyprloader" "Theme: $config/theme.json" "ZIP: $config/imports"
