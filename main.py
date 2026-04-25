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
from PyQt6.QtGui import QColor, QIcon

# --- 1. СИСТЕМНЫЕ НАСТРОЙКИ ---
SYSTEM = platform.system()

def get_path(relative_path):
    """Корректный путь для файлов внутри .exe и в обычном режиме"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

if SYSTEM == "Linux":
    os.environ["QT_QPA_PLATFORM"] = "xcb"
elif SYSTEM == "Windows":
    try:
        from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as SessionManager
        HAS_WINSDK = True
    except ImportError:
        HAS_WINSDK = False

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.config_path = get_path("config.json")
        self.cache_dir = get_path("lyrics_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Окно и тени
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint
        if SYSTEM == "Windows":
            flags |= Qt.WindowType.Tool | Qt.WindowType.NoDropShadowWindowHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if SYSTEM == "Linux":
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.label = QLabel("", self)
        self.shadow = QGraphicsDropShadowEffect()
        self.label.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setFixedSize(1200, 200)

        # Состояние
        self.manager = None
        self.current_track, self.full_lyrics_text = "", ""
        self.lyrics_dict = {}
        self.offset, self.display_char_count = 0.0, 0

        # Таймеры
        self.timer = QTimer(self, timeout=self.update_logic)
        self.timer.start(100)

        self.config_timer = QTimer(self, timeout=self.load_config)
        self.config_timer.start(2000)

        self.typing_timer = QTimer(self, timeout=self.type_letter)
        self.typing_timer.setInterval(20)

        self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default = {"font_name": "Segoe UI", "font_size": 24, "text_color": "white",
                           "x": 400, "y": 800, "shadow_blur": 7, "offset": 0.8 if SYSTEM == "Windows" else 0.0}
                with open(self.config_path, "w") as f: json.dump(default, f)

            with open(self.config_path, "r", encoding="utf-8") as f:
                c = json.load(f)
                self.label.setStyleSheet(f"color: {c['text_color']}; font-size: {c['font_size']}px; "
                                         f"font-weight: bold; font-family: '{c['font_name']}'; qproperty-alignment: AlignCenter;")
                self.shadow.setBlurRadius(c['shadow_blur'])
                self.shadow.setColor(QColor(0, 0, 0, 200))
                self.move(c['x'], c['y'])
                self.offset = float(c.get('offset', 0.0))
                if SYSTEM == "Windows": self.lower()
        except: pass

    def get_media_data(self):
        """Выбор метода получения данных в зависимости от ОС"""
        if SYSTEM == "Windows" and HAS_WINSDK:
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(self.get_windows_data())
            except: return asyncio.run(self.get_windows_data())
        elif SYSTEM == "Linux":
            try:
                cmd = ["playerctl", "-p", "spotify", "metadata"]
                art = subprocess.check_output(cmd + ["artist"]).decode().strip()
                tit = subprocess.check_output(cmd + ["title"]).decode().strip()
                pos = float(subprocess.check_output(["playerctl", "-p", "spotify", "position"]).decode())
                return {"track_id": f"{art} - {tit}", "pos": pos + self.offset}
            except: return None
        return None

    async def get_windows_data(self):
        try:
            if not self.manager: self.manager = await SessionManager.request_async()
            session = self.manager.get_current_session()
            if session:
                props = await session.try_get_media_properties_async()
                time = session.get_timeline_properties()
                return {"track_id": f"{props.artist} - {props.title}", "pos": time.position.total_seconds() + self.offset}
        except: pass
        return None

    def update_logic(self):
        data = self.get_media_data()
        if not data:
            self.label.setText("")
            return

        if data['track_id'] != self.current_track:
            self.current_track = data['track_id']
            self.lyrics_dict = {}
            self.load_lyrics(data['track_id'])

        # Поиск актуальной строки текста
        curr_text = ""
        for s in sorted(self.lyrics_dict.keys()):
            if s <= (data['pos'] + 0.1): curr_text = self.lyrics_dict[s]
            else: break

        if self.full_lyrics_text != curr_text:
            self.full_lyrics_text = curr_text
            self.display_char_count = 0
            if curr_text: self.typing_timer.start()
            else: self.label.setText("")

    def load_lyrics(self, track_id):
        clean_name = re.sub(r'[\\/*?:"<>|]', "", track_id)
        cache_file = os.path.join(self.cache_dir, f"{clean_name}.lrc")

        raw = ""
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f: raw = f.read()
        else:
            try:
                raw = syncedlyrics.search(track_id)
                if raw:
                    with open(cache_file, "w", encoding="utf-8") as f: f.write(raw)
            except: pass

        if raw:
            for line in raw.splitlines():
                m = re.search(r'\[(\d+):(\d+)(?:\.(\d+))?\]', line)
                if m:
                    ts = int(m.group(1)) * 60 + int(m.group(2)) + (int(m.group(3))/100 if m.group(3) else 0)
                    txt = re.sub(r'\[.*?\]', '', line).strip()
                    if txt: self.lyrics_dict[ts] = txt
        if not self.lyrics_dict: self.lyrics_dict[0.0] = f"🎵 {track_id}"

    def type_letter(self):
        if self.display_char_count <= len(self.full_lyrics_text):
            self.label.setText(self.full_lyrics_text[:self.display_char_count])
            self.display_char_count += 1
        else: self.typing_timer.stop()

class TrayApp:
    def __init__(self, win):
        self.win = win
        self.tray = QSystemTrayIcon(QIcon(get_path("icon.png")))
        menu = QMenu()
        menu.addAction("Настройки", self.open_settings)
        menu.addAction("Выход", sys.exit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def open_settings(self):
        # Если есть файл настроек, запускаем его
        s_path = get_path("settings.py")
        if os.path.exists(s_path):
            subprocess.Popen([sys.executable, s_path])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = SpotifyWidget()
    w.show()
    t = TrayApp(w)
    sys.exit(app.exec())
