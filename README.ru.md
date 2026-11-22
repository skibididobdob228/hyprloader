# Hyprloader

[English](README.md) · **Русский**

Hyprloader показывает полноэкранное меню профилей после входа в систему. У каждого профиля своя конфигурация Hyprland и Quickshell. Стрелки меняют выбор, Enter или клик запускает профиль, Esc выбирает профиль по умолчанию, а `/` открывает поиск.

## Установка

Нужны Python 3.10+, Hyprland с поддержкой Lua-конфигурации, Quickshell и `dbus-run-session`. Rofi используется как запасное меню.

```sh
./install.sh
~/.local/bin/hyprloader preview
```

Для интеграции со штатным сеансом Hyprland в SDDM запусти `./install.sh --sddm` и выбери **Hyprland** на экране входа. Из TTY меню запускается командой `hyprloader session`, а `hyprloader session work` сразу выбирает профиль `work`. Если `~/.local/bin` отсутствует в `PATH`, укажи полный путь к команде. **Super+Esc** закрывает меню при входе и продолжает загрузку с профилем по умолчанию.

В профиль «Обычный» загружается основной конфиг Hyprland. Если уже установлен Serpantinum, его режимы из `~/.config/serpantinum/modes` тоже появятся в списке.

## Добавление ZIP

Положи архив в **`~/.config/hyprloader/imports/`**. При следующем открытии меню или вызове `hyprloader list` Hyprloader распакует его и добавит профиль. Можно также импортировать архив по полному пути.

```sh
hyprloader import ~/Downloads/work.zip
hyprloader list
```

Обычный ZIP обнаруживается по `hyprland.lua` или `hyprland.conf` и `shell.qml` или `Shell.qml`. Сохраняй структуру каталогов, чтобы внутри профиля оставались рабочими относительные ссылки на скрипты, модули и картинки.

```text
work.zip
└── work/
    ├── hypr/
    │   └── hyprland.lua
    └── quickshell/
        └── shell.qml
```

Положи `hyprloader.json` в корень архива или в общую верхнюю папку, если хочешь изменить название, добавить иконку или явно выбрать файлы запуска. Пути считаются от папки с манифестом. Поля `name`, `description` и `icon` необязательны.

```json
{
  "name": "Работа",
  "description": "Профиль с отдельной панелью",
  "hyprland": "hypr/hyprland.lua",
  "quickshell": "quickshell/shell.qml",
  "icon": "assets/work.svg"
}
```

Готовый профиль сохраняется в `~/.local/share/hyprloader/profiles/<id>/`. Идентификатор получается из имени ZIP. Архив можно убрать из папки импорта после добавления. Повторный импорт того же имени сохраняет установленную версию. Чтобы добавить вторую версию рядом, дай ZIP новое имя. В манифесте установленного профиля `profile.json` можно изменить название и описание.

Импорт сохраняет весь пакет в папке профиля. Для запуска Hyprloader использует два файла из архива, а их настройки и скрипты выполняются при выборе профиля. Если архив поставляется как установщик, ему всё равно нужна собственная установка зависимостей и файлов, на которые конфиги ссылаются через абсолютные пути. Для такого пакета можно зарегистрировать уже установленные файлы командой `hyprloader add`.

```sh
hyprloader add work ~/.config/hypr-work/hyprland.lua ~/.config/quickshell/work/shell.qml --name "Работа"
```

Если Quickshell нужен особый запуск, манифест поддерживает `quickshell_runner`. Это путь к исполняемому файлу внутри архива. Он получает абсолютный путь к QML первым аргументом.

## Оформление меню

Меняй **`~/.config/hyprloader/theme.json`** и запускай `hyprloader preview`. Достаточно указать параметры, которые хочешь изменить.

```json
{
  "title": "Выбор рабочего стола",
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

| Настройка | Что меняет |
| --- | --- |
| `backgroundImage`, `backgroundMode` | Фон и режим изображения `cover`, `contain` или `stretch` |
| `showBackdrop` | Геометрический фон, когда изображения нет |
| `showBrand`, `showDescription`, `showHints` | Фирменный знак, описание профиля и подсказки по клавишам |
| `menuWidth`, `rowHeight`, `rowRadius`, `iconSize`, `textSize` | Размеры интерфейса. `rowHeight: 0` подбирает высоту автоматически |
| `horizontalOffset`, `verticalOffset` | Сдвиг меню от центра. Горизонтальный задаётся в процентах на широком экране, вертикальный в пикселях |
| `icons` | Иконки по идентификаторам из `hyprloader list`. Подходят SVG и PNG |
| `layout`, `rofiTheme` | Пути к своему QML-макету и запасной теме Rofi |

Пути к обоям, иконкам и макетам считаются от каталога с `theme.json`. Абсолютные пути и `~` тоже поддерживаются. Hyprloader учитывает `XDG_CONFIG_HOME`, `XDG_DATA_HOME` и `XDG_STATE_HOME`.

Для полной переделки макета скопируй `app/menu.qml`, `app/ProfileIcon.qml` и `app/Backdrop.qml` в свой каталог темы и укажи путь к копии `menu.qml` в поле `layout`. Меню читает JSON из файла, указанного в `HYPRLOADER_MENU_DATA`, записывает `id` выбранного профиля в файл `HYPRLOADER_MENU_CHOICE` и завершает Quickshell через `Qt.quit()`. Встроенный макет служит запасным вариантом.
