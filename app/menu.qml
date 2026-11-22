pragma ComponentBehavior: Bound

import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

ShellRoot {
    id: root
    readonly property var data: JSON.parse(profileData.text())
    readonly property var theme: data.theme
    readonly property var palette: theme.colors
    readonly property color accent: palette.accent
    property bool choosing: false
    property bool searching: false
    readonly property string query: searchInput.text.trim().toLowerCase()
    readonly property var choices: query === "" ? data.profiles : data.profiles.filter(
        profile => (profile.name + " " + profile.description).toLowerCase().includes(query))
    readonly property int defaultIndex: data.profiles.findIndex(profile => profile.id === data.defaultId)
    readonly property string monitorName: data.monitorName ?? ""

    function select(id: string): void {
        if (!choosing) {
            choosing = true
            result.setText(id)
        }
    }

    function changeSelection(delta: int): void {
        if (choices.length > 0)
            options.currentIndex = (options.currentIndex + delta + choices.length) % choices.length
    }

    function showSearch(): void {
        searching = true
        searchInput.forceActiveFocus()
    }

    function closeSearch(): void {
        searching = false
        searchInput.clear()
        options.currentIndex = defaultIndex
        surface.forceActiveFocus()
    }

    function handleKey(event: KeyEvent): void {
        switch (event.key) {
        case Qt.Key_Up:
            changeSelection(-1)
            break
        case Qt.Key_Down:
            changeSelection(1)
            break
        case Qt.Key_Return:
        case Qt.Key_Enter:
            if (options.currentIndex >= 0)
                select(choices[options.currentIndex].id)
            break
        case Qt.Key_Escape:
            if (searching)
                closeSearch()
            else
                select(data.defaultId)
            break
        default:
            if (!searching && (event.key === Qt.Key_Slash || event.matches(StandardKey.Find))) {
                showSearch()
                break
            }
            return
        }
        event.accepted = true
    }

    FileView {
        id: profileData
        path: Quickshell.env("HYPRLOADER_MENU_DATA")
        blockLoading: true
    }

    FileView {
        id: result
        path: Quickshell.env("HYPRLOADER_MENU_CHOICE")
        preload: false
        onSaved: Qt.quit()
        onSaveFailed: Qt.exit(1)
    }

    PanelWindow {
        id: panel
        screen: Quickshell.screens.find(output => output.name === root.monitorName)
                ?? Quickshell.screens[0] ?? null
        anchors { left: true; right: true; top: true; bottom: true }
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
        WlrLayershell.namespace: "hyprloader"
        color: root.palette.background

        FocusScope {
            id: surface
            anchors.fill: parent
            focus: true
            Keys.onPressed: event => root.handleKey(event)

            readonly property int rowHeight: root.theme.rowHeight || (height < 580 ? 44 : 54)
            readonly property string typeface: root.theme.fontFamily
            readonly property real interfaceScale: Math.max(1, Math.min(1.3, height / 920))

            Backdrop {
                anchors.fill: parent
                background: root.palette.background
                visible: root.theme.showBackdrop && wallpaper.status !== Image.Ready
            }

            Image {
                id: wallpaper
                anchors.fill: parent
                source: root.theme.backgroundImage
                fillMode: root.theme.backgroundMode === "contain" ? Image.PreserveAspectFit
                        : root.theme.backgroundMode === "stretch" ? Image.Stretch : Image.PreserveAspectCrop
                asynchronous: true
            }

            Column {
                id: content
                anchors.centerIn: parent
                readonly property real offsetLimit: Math.max(0, (surface.width - width * scale - 32) / 2)
                anchors.horizontalCenterOffset: surface.width > 950
                    ? Math.max(-offsetLimit, Math.min(offsetLimit, surface.width * root.theme.horizontalOffset / 100)) : 0
                anchors.verticalCenterOffset: root.theme.verticalOffset
                width: Math.max(0, Math.min(root.theme.menuWidth, (surface.width - 44) / scale))
                scale: surface.interfaceScale
                spacing: 12

                Column {
                    width: parent.width
                    spacing: 5

                    Row {
                        spacing: 12
                        visible: root.theme.showBrand || root.theme.title !== ""

                        Item {
                            id: brand
                            width: 24
                            height: 30
                            anchors.verticalCenter: parent.verticalCenter
                            visible: root.theme.showBrand

                            Rectangle {
                                x: 3; y: 6; width: 5; height: 19
                                radius: 1
                                rotation: 24
                                color: root.accent
                            }
                            Rectangle {
                                x: 12; y: 2; width: 5; height: 26
                                radius: 1
                                rotation: 24
                                color: Qt.lighter(root.accent, 1.18)
                            }
                        }
                        Text {
                            id: title
                            text: root.theme.title
                            textFormat: Text.PlainText
                            visible: text !== ""
                            width: Math.max(0, content.width - (root.theme.showBrand ? brand.width + 12 : 0))
                            elide: Text.ElideRight
                            color: root.palette.text
                            font.family: surface.typeface
                            font.pixelSize: surface.height < 580 ? 32 : 40
                            font.weight: Font.DemiBold
                            font.letterSpacing: -1.3
                        }
                    }

                    Text {
                        width: parent.width
                        text: root.theme.subtitle
                        textFormat: Text.PlainText
                        visible: text !== ""
                        elide: Text.ElideRight
                        color: root.palette.muted
                        font.family: surface.typeface
                        font.pixelSize: 15
                    }
                }

                Item {
                    width: parent.width
                    height: 9
                    visible: !root.searching
                }

                Rectangle {
                    width: parent.width
                    height: 36
                    visible: root.searching
                    radius: 6
                    color: root.palette.search
                    border.color: root.accent

                    Text {
                        anchors.fill: searchInput
                        verticalAlignment: Text.AlignVCenter
                        visible: searchInput.text === ""
                        text: "Название профиля"
                        color: root.palette.muted
                        font: searchInput.font
                    }
                    TextInput {
                        id: searchInput
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        verticalAlignment: TextInput.AlignVCenter
                        color: root.palette.text
                        selectionColor: Qt.darker(root.accent, 1.5)
                        font.family: surface.typeface
                        font.pixelSize: 15
                        clip: true
                        selectByMouse: true
                        Keys.onPressed: event => root.handleKey(event)
                        onTextChanged: {
                            if (root.searching)
                                options.currentIndex = root.choices.length ? 0 : -1
                        }
                    }
                }

                ListView {
                    id: options
                    width: parent.width
                    height: Math.min(Math.max(1, count) * (surface.rowHeight + spacing) - spacing,
                                     Math.max(surface.rowHeight, surface.height / surface.interfaceScale - 260))
                    clip: true
                    spacing: 4
                    model: root.choices
                    boundsBehavior: Flickable.StopAtBounds
                    keyNavigationEnabled: false
                    Component.onCompleted: currentIndex = root.defaultIndex

                    delegate: Rectangle {
                        id: row
                        required property int index
                        required property var modelData
                        readonly property bool selected: ListView.isCurrentItem
                        readonly property real glyphSize: Math.min(root.theme.iconSize, height - 8)
                        width: options.width
                        height: surface.rowHeight
                        radius: root.theme.rowRadius
                        color: selected ? root.palette.selected : "transparent"
                        Behavior on color { ColorAnimation { duration: 90 } }

                        Rectangle {
                            anchors.left: parent.left
                            anchors.leftMargin: 2
                            anchors.verticalCenter: parent.verticalCenter
                            width: 3
                            height: Math.min(23, row.height - 6)
                            radius: 1.5
                            color: root.accent
                            visible: row.selected
                        }

                        ProfileIcon {
                            visible: profileImage.status !== Image.Ready
                            anchors.left: parent.left
                            anchors.leftMargin: 17
                            anchors.verticalCenter: parent.verticalCenter
                            width: row.glyphSize
                            height: width
                            kind: row.modelData.icon
                            ink: row.selected ? root.palette.text : root.palette.profile
                        }

                        Image {
                            id: profileImage
                            anchors.left: parent.left
                            anchors.leftMargin: 17
                            anchors.verticalCenter: parent.verticalCenter
                            width: row.glyphSize
                            height: width
                            source: row.modelData.iconSource
                            fillMode: Image.PreserveAspectFit
                            sourceSize: Qt.size(Math.ceil(width * 2), Math.ceil(height * 2))
                        }

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 33 + row.glyphSize
                            anchors.right: parent.right
                            anchors.rightMargin: 42
                            anchors.verticalCenter: parent.verticalCenter
                            text: row.modelData.name
                            textFormat: Text.PlainText
                            elide: Text.ElideRight
                            color: row.selected || pointer.containsMouse ? root.palette.text : root.palette.profile
                            font.family: surface.typeface
                            font.pixelSize: Math.min(root.theme.textSize, row.height - 6)
                            font.weight: row.selected ? Font.Medium : Font.Normal
                        }

                        Text {
                            anchors.right: parent.right
                            anchors.rightMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            text: "↵"
                            visible: row.selected
                            color: root.palette.muted
                            font.pixelSize: 18
                        }

                        MouseArea {
                            id: pointer
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.select(row.modelData.id)
                        }
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 17
                        anchors.verticalCenter: parent.verticalCenter
                        visible: options.count === 0
                        text: "Профили не найдены"
                        color: root.palette.profile
                        font.family: surface.typeface
                        font.pixelSize: 16
                    }
                }

                Text {
                    width: parent.width
                    visible: root.theme.showDescription
                    leftPadding: 17
                    text: root.choices[options.currentIndex]?.description ?? ""
                    textFormat: Text.PlainText
                    elide: Text.ElideRight
                    color: root.palette.muted
                    font.family: surface.typeface
                    font.pixelSize: 13
                }
            }

            Row {
                visible: root.theme.showHints
                anchors.bottom: parent.bottom
                anchors.bottomMargin: surface.height < 580 ? 19 : 34
                anchors.horizontalCenter: content.horizontalCenter
                spacing: surface.width < 510 ? 7 : 15

                Repeater {
                    model: ["↑ ↓  Выбор", "Enter  Загрузить",
                            root.searching ? "Esc  Назад" : "Esc  По умолчанию",
                            ...(surface.width >= 380 && !root.searching ? ["/  Поиск"] : [])]
                    Text {
                        required property string modelData
                        text: modelData
                        color: root.palette.muted
                        font.family: surface.typeface
                        font.pixelSize: surface.width < 510 ? 11 : Math.round(12 * surface.interfaceScale)
                    }
                }
            }
        }
    }
}
