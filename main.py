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

class SpotifyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnBottomHint
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

        # Инициализируем настройки задержки по умолчанию
        self.offset = 0.0
        self.load_config()

        self.current_track = ""
        self.lyrics_dict = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

        self.config_timer = QTimer(self)
        self.config_timer.timeout.connect(self.load_config)
        self.config_timer.start(1000) # Проверяем конфиг раз в секунду, чтобы не грузить диск
        # Параметры анимации
        self.full_lyrics_text = ""
        self.display_char_count = 0
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self.type_letter)
        # Скорость печати (мс между буквами).
        # 20-30 мс — золотая середина для плавности.
        self.typing_timer.setInterval(25)

    def type_letter(self):
        if self.display_char_count <= len(self.full_lyrics_text):
            # Показываем часть текста от 0 до текущего символа
            self.label.setText(self.full_lyrics_text[:self.display_char_count])
            self.display_char_count += 1
        else:
            self.typing_timer.stop()

    def load_config(self):
        try:
            if not os.path.exists("config.json"):
                # Добавили "offset": 0.0 в стандартный конфиг
                default_config = {"font_name": "Segoe UI", "font_size": 24, "text_color": "white", "x": 550, "y": 200, "shadow_blur": 7, "offset": 0.0}
                with open("config.json", "w") as f: json.dump(default_config, f)

            with open("config.json", "r") as f:
                conf = json.load(f)
                self.label.setStyleSheet(f"color: {conf['text_color']}; font-size: {conf['font_size']}px; font-weight: bold; font-family: '{conf['font_name']}', sans-serif; qproperty-alignment: AlignCenter;")
                self.shadow.setBlurRadius(conf['shadow_blur'])
                self.shadow.setColor(QColor(0, 0, 0, 255))
                self.move(conf['x'], conf['y'])
                # Читаем смещение времени
                self.offset = float(conf.get('offset', 0.0))
        except: pass

    def get_player_data(self, command):
        try:
            return subprocess.check_output(["playerctl", "-p", "spotify", "metadata", command]).decode("utf-8").strip()
        except: return ""

    def update_ui(self):
        # 1. Получаем данные о треке
        artist = self.get_player_data("artist")
        title = self.get_player_data("title")
        track_id = f"{artist} - {title}"

        # 2. Если трек сменился — сброс и поиск (кэш/сеть)
        if track_id != self.current_track:
            self.current_track = track_id
            self.lyrics_dict = {}
            self.label.setText("")

            if artist:
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    cache_dir = os.path.join(base_dir, "lyrics_cache")
                    os.makedirs(cache_dir, exist_ok=True)
                    clean_name = re.sub(r'[\\/*?:"<>|]', "", track_id)
                    cache_file = os.path.join(cache_dir, f"{clean_name}.lrc")

                    raw_lrc = ""
                    if os.path.exists(cache_file):
                        with open(cache_file, "r", encoding="utf-8") as f:
                            raw_lrc = f.read()
                    else:
                        raw_lrc = syncedlyrics.search(track_id, providers=["NetEase", "Musixmatch"])
                        if raw_lrc:
                            with open(cache_file, "w", encoding="utf-8") as f:
                                f.write(raw_lrc)

                    if raw_lrc:
                        for line in raw_lrc.splitlines():
                            match = re.search(r'\[(\d+):(\d+)(?:\.(\d+))?\]', line)
                            if match:
                                m, s = int(match.group(1)), int(match.group(2))
                                ms_val = match.group(3)
                                ms = int(ms_val) / (10**len(ms_val)) if ms_val else 0
                                timestamp = m * 60 + s + ms
                                text = re.sub(r'\[.*?\]', '', line).strip()
                                if text:
                                    self.lyrics_dict[timestamp] = text

                    if not self.lyrics_dict:
                        self.lyrics_dict[0.0] = f"🎵 {artist} — {title}"

                except Exception as e:
                    print(f"Ошибка загрузки: {e}")
                    self.lyrics_dict[0.0] = f"🎵 {artist} — {title}"

        # 3. Вычисление текущей строки (display_text)
        if not self.lyrics_dict:
            return

        try:
            # ИСПРАВЛЕНО: используем DEVNULL вместо NULL
            pos_raw = subprocess.check_output(["playerctl", "-p", "spotify", "position"],
                                            stderr=subprocess.DEVNULL).decode("utf-8").strip()
            current_sec = float(pos_raw) + self.offset

            display_text = ""
            times = sorted(self.lyrics_dict.keys())
            for s in times:
                if s <= (current_sec + 0.1):
                    display_text = self.lyrics_dict[s]
                else:
                    break

            # 4. ФИНАЛ: ЗАПУСК АНИМАЦИИ
            if self.full_lyrics_text != display_text:
                # Если текста нет (пауза между строками), просто очищаем
                if not display_text:
                    self.label.setText("")
                    self.full_lyrics_text = ""
                else:
                    self.full_lyrics_text = display_text
                    self.display_char_count = 0
                    self.typing_timer.start()
        except Exception as e:
            # Можно раскомментировать для отладки:
            # print(f"Debug: {e}")
            pass
# --- КЛАСС ДЛЯ ТРЕЯ ---
class TrayApp:
    def __init__(self, widget_window):
        self.widget = widget_window
        self.tray = QSystemTrayIcon(QIcon("icon.png"), parent=app)
        self.tray.setToolTip("Spotify Lyrics Widget")

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
        subprocess.Popen([sys.executable, "settings.py"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = SpotifyWidget()
    window.show()
    tray = TrayApp(window)
    sys.exit(app.exec())
