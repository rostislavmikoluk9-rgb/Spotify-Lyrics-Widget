import sys
import subprocess
import syncedlyrics
import re
import os
import json
import platform
import asyncio
from PyQt6.QtWidgets import (QApplication, QLabel, QWidget, QVBoxLayout,
                             QGraphicsDropShadowEffect, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QAction

# 1. ОПРЕДЕЛЕНИЕ СИСТЕМЫ И СПЕЦИФИЧНЫЕ НАСТРОЙКИ
SYSTEM = platform.system()

if SYSTEM == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"  # Форсируем X11 для KDE/CachyOS
elif SYSTEM == "Windows":
    try:
        from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as SessionManager
    except ImportError:
        print("Ошибка: winsdk не установлен. Запустите установщик.")

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.cache_dir = os.path.join(self.base_dir, "lyrics_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Флаги окна (Универсальные + Специфичные)
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint
        if SYSTEM == "Windows":
            flags |= Qt.WindowType.Tool | Qt.WindowType.NoDropShadowWindowHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if SYSTEM == "Linux":
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.layout = QVBoxLayout()
        self.label = QLabel("", self)

        # Эффект тени (включаем для всех)
        self.shadow = QGraphicsDropShadowEffect()
        self.label.setGraphicsEffect(self.shadow)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setFixedSize(1200, 200)

        # Переменные состояния
        self.manager = None
        self.current_track = ""
        self.lyrics_dict = {}
        self.offset = 0.0
        self.full_lyrics_text = ""
        self.display_char_count = 0

        # Таймеры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_logic)
        self.timer.start(100)

        self.config_timer = QTimer(self)
        self.config_timer.timeout.connect(self.load_config)
        self.config_timer.start(2000)

        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_letter)
        self.typing_timer.setInterval(25)

        self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default = {"font_name": "Segoe UI", "font_size": 24, "text_color": "white",
                           "x": 400, "y": 800, "shadow_blur": 7, "offset": 0.0 if SYSTEM == "Linux" else 0.8}
                with open(self.config_path, "w") as f: json.dump(default, f)

            with open(self.config_path, "r", encoding="utf-8") as f:
                conf = json.load(f)
                self.label.setStyleSheet(f"color: {conf['text_color']}; font-size: {conf['font_size']}px; "
                                         f"font-weight: bold; font-family: '{conf['font_name']}'; qproperty-alignment: AlignCenter;")
                self.shadow.setBlurRadius(conf['shadow_blur'])
                self.shadow.setColor(QColor(0, 0, 0, 255))
                self.move(conf['x'], conf['y'])
                self.offset = float(conf.get('offset', 0.0))
                if SYSTEM == "Windows": self.lower()
        except: pass

    # --- ЛОГИКА ПОЛУЧЕНИЯ ДАННЫХ ---
    def get_media_data(self):
        if SYSTEM == "Linux":
            try:
                artist = subprocess.check_output(["playerctl", "-p", "spotify", "metadata", "artist"]).decode("utf-8").strip()
                title = subprocess.check_output(["playerctl", "-p", "spotify", "metadata", "title"]).decode("utf-8").strip()
                pos = float(subprocess.check_output(["playerctl", "-p", "spotify", "position"]).decode("utf-8").strip())
                return {"track_id": f"{artist} - {title}", "pos": pos + self.offset}
            except: return None
        else:
            # Для Windows используем asyncio
            return asyncio.run(self.get_windows_data())

    async def get_windows_data(self):
        try:
            if not self.manager: self.manager = await SessionManager.request_async()
            session = self.manager.get_current_session()
            if session:
                props = await session.try_get_media_properties_async()
                timeline = session.get_timeline_properties()
                return {
                    "track_id": f"{props.artist} - {props.title}",
                    "pos": timeline.position.total_seconds() + self.offset
                }
        except: pass
        return None

    # --- ОБРАБОТКА ТЕКСТА ---
    def update_logic(self):
        data = self.get_media_data()
        if not data:
            self.label.setText("")
            return

        # Если песня изменилась
        if data['track_id'] != self.current_track:
            self.current_track = data['track_id']
            self.lyrics_dict = {}
            self.load_lyrics(data['track_id'])

        # Поиск текущей строки
        curr_pos = data['pos']
        display_text = ""
        times = sorted(self.lyrics_dict.keys())
        for s in times:
            if s <= (curr_pos + 0.1):
                display_text = self.lyrics_dict[s]
            else: break

        # Запуск анимации печати
        if self.full_lyrics_text != display_text:
            self.full_lyrics_text = display_text
            if not display_text:
                self.label.setText("")
            else:
                self.display_char_count = 0
                self.typing_timer.start()

    def load_lyrics(self, track_id):
        clean_name = re.sub(r'[\\/*?:"<>|]', "", track_id)
        cache_path = os.path.join(self.cache_dir, f"{clean_name}.lrc")

        raw_lrc = ""
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f: raw_lrc = f.read()
        else:
            try:
                raw_lrc = syncedlyrics.search(track_id)
                if raw_lrc:
                    with open(cache_path, "w", encoding="utf-8") as f: f.write(raw_lrc)
            except: pass

        if raw_lrc:
            for line in raw_lrc.splitlines():
                match = re.search(r'\[(\d+):(\d+)(?:\.(\d+))?\]', line)
                if match:
                    m, s = int(match.group(1)), int(match.group(2))
                    ms_val = match.group(3)
                    ms = int(ms_val) / (10**len(ms_val)) if ms_val else 0
                    timestamp = m * 60 + s + ms
                    txt = re.sub(r'\[.*?\]', '', line).strip()
                    if txt: self.lyrics_dict[timestamp] = txt

        if not self.lyrics_dict:
            self.lyrics_dict[0.0] = f"🎵 {track_id}"

    def type_letter(self):
        if self.display_char_count <= len(self.full_lyrics_text):
            self.label.setText(self.full_lyrics_text[:self.display_char_count])
            self.display_char_count += 1
        else:
            self.typing_timer.stop()

class TrayApp:
    def __init__(self, widget_window):
        self.widget = widget_window
        icon_p = os.path.join(self.widget.base_dir, "icon.png")
        self.tray = QSystemTrayIcon(QIcon(icon_p))

        menu = QMenu()
        menu.addAction("Настройки").triggered.connect(self.open_settings)
        menu.addAction("Выход").triggered.connect(sys.exit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def open_settings(self):
        subprocess.Popen([sys.executable, os.path.join(self.widget.base_dir, "settings.py")])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = SpotifyWidget()
    w.show()
    t = TrayApp(w)
    sys.exit(app.exec())
