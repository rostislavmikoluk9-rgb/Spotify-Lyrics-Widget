import sys
import subprocess
import syncedlyrics
import re
import os
import json
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout,
                             QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QAction

# Форсируем X11 для KDE
os.environ["QT_QPA_PLATFORM"] = "xcb"

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсам (нужно для PyInstaller) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint |
            Qt.WindowType.Tool |             # Скрывает из панели задач
            Qt.WindowType.SubWindow          # Помогает игнорировать Meta+D
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.layout = QVBoxLayout()
        self.label = QLabel("", self)
        self.shadow = QGraphicsDropShadowEffect()
        self.label.setGraphicsEffect(self.shadow)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.setFixedSize(800, 150)
        self.load_config()

        self.current_track = ""
        self.lyrics_dict = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

        self.config_timer = QTimer(self)
        self.config_timer.timeout.connect(self.load_config)
        self.config_timer.start(2000)

    def load_config(self):
        try:
            # Используем resource_path для конфига
            config_file = resource_path("config.json")
            if not os.path.exists(config_file):
                default_config = {"font_name": "Segoe UI", "font_size": 24, "text_color": "white", "x": 550, "y": 200, "shadow_blur": 7}
                with open(config_file, "w") as f: json.dump(default_config, f)

            with open(config_file, "r") as f:
                conf = json.load(f)
                self.label.setStyleSheet(f"color: {conf['text_color']}; font-size: {conf['font_size']}px; font-weight: bold; font-family: '{conf['font_name']}', sans-serif; qproperty-alignment: AlignCenter;")
                self.shadow.setBlurRadius(conf['shadow_blur'])
                self.shadow.setColor(QColor(0, 0, 0, 255))
                self.move(conf['x'], conf['y'])
        except: pass

    def get_player_data(self, command):
        try:
            return subprocess.check_output(["playerctl", "-p", "spotify", "metadata", command]).decode("utf-8").strip()
        except: return ""

    def update_ui(self):
        artist = self.get_player_data("artist")
        title = self.get_player_data("title")
        track_id = f"{artist} - {title}"

        if track_id != self.current_track:
            self.current_track = track_id
            self.lyrics_dict = {}
            if artist:
                try:
                    raw_lrc = syncedlyrics.search(track_id)
                    if raw_lrc:
                        for line in raw_lrc.splitlines():
                            match = re.search(r'\[(\d+):(\d+)', line)
                            if match:
                                seconds = int(match.group(1)) * 60 + int(match.group(2))
                                text = re.sub(r'\[.*?\]', '', line).strip()
                                if text: self.lyrics_dict[seconds] = text
                except: pass

        try:
            pos_raw = subprocess.check_output(["playerctl", "-p", "spotify", "position"]).decode("utf-8").strip()
            current_sec = int(float(pos_raw))
            display_text = ""
            for s in sorted(self.lyrics_dict.keys()):
                if s <= current_sec: display_text = self.lyrics_dict[s]
                else: break
            self.label.setText(display_text)
        except: self.label.setText("")

class TrayApp:
    def __init__(self, widget_window):
        self.widget = widget_window
        # Используем resource_path для иконки
        self.tray = QSystemTrayIcon(QIcon(resource_path("icon.png")), parent=app)
        self.tray.setToolTip("Spotify Sky Lyrics")

        menu = QMenu()
        show_settings = QAction("Настройки", menu)
        show_settings.triggered.connect(self.open_settings)
        menu.addAction(show_settings)

        exit_action = QAction("Выход", menu)
        exit_action.triggered.connect(sys.exit)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def open_settings(self):
        # Пробуем запустить через системный python
        try:
            if os.path.exists("settings.py"):
                subprocess.Popen(["python", "settings.py"])
            else:
                # Если файла нет рядом, пробуем найти его путь относительно бинарника
                base_dir = os.path.dirname(sys.argv[0])
                settings_path = os.path.join(base_dir, "settings.py")
                subprocess.Popen(["python", settings_path])
        except Exception as e:
            print(f"Не удалось запустить настройки: {e}")

if __name__ == "__main__":
    # Фикс путей: принудительно переходим в папку, где лежит сам файл
    target_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(target_dir)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = SpotifyWidget()
    window.show()

    tray = TrayApp(window)
    sys.exit(app.exec())
