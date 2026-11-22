# Hyprloader

[English](README.md) · **Русский**

Hyprloader показывает полноэкранное меню профилей после входа в систему. У каждого профиля своя конфигурация Hyprland и Quickshell. Стрелки меняют выбор, Enter или клик запускает профиль, Esc выбирает профиль по умолчанию, а `/` открывает поиск.

## Установка

Нужны Python 3.10+, Hyprland с `hyprctl`, Quickshell и `dbus-run-session` в `PATH`. В качестве запасного меню подойдёт Rofi с поддержкой Wayland. Hyprloader использует `start-hyprland`, если он доступен, иначе запускает `Hyprland` напрямую.

```sh
git clone https://github.com/skibididobdob228/hyprloader.git
cd hyprloader
./install.sh
~/.local/bin/hyprloader doctor
~/.local/bin/hyprloader preview
```

Из TTY меню запускается командой `~/.local/bin/hyprloader session`. Чтобы сразу загрузить нужный профиль, передай его ID, например `hyprloader session work`. **Super+Esc** закрывает меню при входе и продолжает загрузку с профилем по умолчанию.

Если экран входа ищет сеансы в `/usr/local/share/wayland-sessions`, как SDDM, установи системный запуск и выбери **Hyprloader** на экране входа. У каждого пользователя будут свои профили и тема. [Каталоги сеансов SDDM](https://github.com/sddm/sddm/blob/develop/data/man/sddm.conf.rst.in)

```sh
sudo ./install.sh --system
```

Флаг `--sddm` по-прежнему доступен для установок, где используется прежний способ подключения через профиль пользователя.

Для меню Hyprloader использует Hyprlang на версиях Hyprland до 0.55 и Lua начиная с 0.55. Для профилей выбирай формат, который читает установленная версия Hyprland. В Hyprland 0.57 используется Lua. [Анонс перехода на Lua](https://hypr.land/news/26_lua/) · [Конфигурация Hyprland 0.57](https://wiki.hypr.land/0.57.0/configuring/core/)

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

Положи `hyprloader.json` в корень архива или в общую верхнюю папку, если хочешь изменить название, добавить иконку или явно выбрать файлы запуска. Пути считаются от папки с манифестом. Достаточно указать нужные поля, остальные файлы запуска Hyprloader найдёт автоматически.

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

В одном ZIP можно держать `hyprland.lua` и `hyprland.conf` в одной папке. На версиях Hyprland до 0.55 будет выбран `.conf`. Если файлы запуска указаны явно в манифесте, путь к запасному `.conf` можно задать полем `hyprland_legacy`.

Если оба конфига находятся внутри общей папки `.config` в ZIP, Hyprloader использует эту папку как `XDG_CONFIG_HOME` для профиля. Поле `config_home` в манифесте позволяет выбрать другую папку. `HYPRLOADER_PROFILE_DIR` указывает на корень распакованного архива, откуда конфиги и скрипты могут брать файлы. Пути, прописанные напрямую через `~/.config`, продолжают вести в домашнюю папку настройки.

## Оформление меню

Меняй **`~/.config/hyprloader/theme.json`** и запускай `hyprloader preview`. Достаточно указать параметры, которые хочешь изменить.

```json
{
  "title": "Выбор рабочего стола",
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

| Настройка | Что меняет |
| --- | --- |
| `backgroundImage`, `backgroundMode` | Фон и режим изображения `cover`, `contain` или `stretch` |
| `wallpaperDim`, `brandImage` | Затемнение фона от 0 до 1 и своя картинка рядом с заголовком |
| `monitor` | Имя экрана для меню, например `DP-1` |
| `menuAlignment`, `menuMargin` | Положение меню `left`, `center` или `right` и отступ от края. Режим `auto` использует горизонтальный сдвиг на широком экране |
| `panelPadding`, `panelRadius`, `colors.panel`, `colors.panelBorder` | Отступ, скругление, цвет и рамка панели меню. Для прозрачности используй `#AARRGGBB` |
| `showBackdrop` | Геометрический фон, когда изображения нет |
| `showBrand`, `showDescription`, `showHints` | Фирменный знак, описание профиля и подсказки по клавишам |
| `showIcons`, `showSelectionMarker` | Иконки профилей и метки выбранной строки |
| `menuWidth`, `rowHeight`, `rowRadius`, `iconSize`, `textSize` | Размеры интерфейса. `rowHeight: 0` подбирает высоту автоматически |
| `rowGap`, `titleSize` | Интервал между строками и размер заголовка. При `titleSize: 0` размер подбирается автоматически |
| `horizontalOffset`, `verticalOffset` | Сдвиг меню от центра. Горизонтальный задаётся в процентах на широком экране, вертикальный в пикселях |
| `icons` | Иконки по идентификаторам из `hyprloader list`. Подходят SVG и PNG |
| `defaultProfile`, `profileOrder` | Идентификатор профиля по умолчанию и список профилей, которые показываются первыми |
| `timeoutSeconds` | Задержка до запуска профиля по умолчанию во встроенном меню при входе. Нажатие клавиши отменяет отсчёт, `0` отключает его |
| `layout`, `rofiTheme` | Пути к своему QML-макету и запасной теме Rofi |

Пути к обоям, иконкам и макетам считаются от каталога с `theme.json`. Абсолютные пути и `~` тоже поддерживаются. Hyprloader учитывает `XDG_CONFIG_HOME`, `XDG_DATA_HOME` и `XDG_STATE_HOME`.

Для полной переделки макета скопируй `app/menu.qml`, `app/ProfileIcon.qml` и `app/Backdrop.qml` в свой каталог темы и укажи путь к копии `menu.qml` в поле `layout`. Меню читает JSON из файла, указанного в `HYPRLOADER_MENU_DATA`, записывает `id` выбранного профиля в файл `HYPRLOADER_MENU_CHOICE` и завершает Quickshell через `Qt.quit()`. Встроенный макет служит запасным вариантом.

## Если выбранный профиль не запускается

Узнай ID через `hyprloader list`, затем передай его в `hyprloader doctor work`. Команда проверяет выбранный файл Hyprland в сборках с поддержкой `--verify-config` и показывает команду запуска Quickshell. Последняя попытка запуска пользовательского профиля записывает `session.log` и `quickshell.log` в `~/.local/state/hyprloader/logs/`. В первом видны проверка конфига и запуск Hyprland, во втором вывод Quickshell с ошибками QML.
