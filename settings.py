import os
import sys
import json
import platform
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QLabel, QSlider, QPushButton, QFontDialog, QColorDialog)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки виджета")

        # Определяем систему
        self.system = platform.system()
        self.setFixedSize(400, 500)

        # Путь к конфигу всегда рядом со скриптом
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")

        self.load_config()
        self.init_ui()

    def load_config(self):
        if not os.path.exists(self.config_path):
            # Дефолтные настройки зависят от ОС
            is_win = self.system == "Windows"
            self.conf = {
                "font_name": "Segoe UI" if is_win else "Arial",
                "font_size": 28 if is_win else 24,
                "text_color": "#ffffff",
                "x": 460 if is_win else 550,
                "y": 800 if is_win else 200,
                "shadow_blur": 10,
                "offset": 0.8 if is_win else 0.0
            }
            self.save_config()
        else:
            try:
                with open(self.config_path, "r", encoding='utf-8') as f:
                    self.conf = json.load(f)
            except:
                self.conf = {} # На случай битого JSON

    def save_config(self):
        with open(self.config_path, "w", encoding='utf-8') as f:
            json.dump(self.conf, f, indent=4, ensure_ascii=False)

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопка выбора шрифта
        self.btn_font = QPushButton(f"Шрифт: {self.conf.get('font_name', 'Default')}")
        self.btn_font.clicked.connect(self.choose_font)
        layout.addWidget(self.btn_font)

        # Размер текста
        layout.addWidget(QLabel("Размер текста:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 150)
        self.size_slider.setValue(self.conf.get('font_size', 24))
        self.size_slider.valueChanged.connect(self.update_size)
        layout.addWidget(self.size_slider)

        # Позиция X (расширенный диапазон для широких экранов)
        layout.addWidget(QLabel("Позиция X (горизонталь):"))
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(-500, 3000)
        self.x_slider.setValue(self.conf.get('x', 100))
        self.x_slider.valueChanged.connect(self.update_x)
        layout.addWidget(self.x_slider)

        # Позиция Y
        layout.addWidget(QLabel("Позиция Y (вертикаль):"))
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(-200, 1500)
        self.y_slider.setValue(self.conf.get('y', 100))
        self.y_slider.valueChanged.connect(self.update_y)
        layout.addWidget(self.y_slider)

        # Синхронизация (Offset)
        layout.addWidget(QLabel("Синхронизация (задержка):"))
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setRange(-50, 50) # от -5.0 до +5.0 сек
        self.offset_slider.setValue(int(self.conf.get('offset', 0.0) * 10))
        self.offset_slider.valueChanged.connect(self.update_offset)
        layout.addWidget(self.offset_slider)

        # Размытие тени
        layout.addWidget(QLabel("Размытие тени:"))
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(0, 30)
        self.blur_slider.setValue(self.conf.get('shadow_blur', 7))
        self.blur_slider.valueChanged.connect(self.update_blur)
        layout.addWidget(self.blur_slider)

        # Кнопка цвета
        self.btn_color = QPushButton("Выбрать цвет текста")
        self.btn_color.clicked.connect(self.choose_color)
        layout.addWidget(self.btn_color)

        # Кнопка выхода
        btn_close = QPushButton("Закрыть настройки")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    # --- Функции обновления ---
    def update_offset(self, val):
        self.conf['offset'] = val / 10.0
        self.save_config()

    def update_size(self, val):
        self.conf['font_size'] = val
        self.save_config()

    def update_x(self, val):
        self.conf['x'] = val
        self.save_config()

    def update_y(self, val):
        self.conf['y'] = val
        self.save_config()

    def update_blur(self, val):
        self.conf['shadow_blur'] = val
        self.save_config()

    def choose_font(self):
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.conf['font_name'] = font.family()
            self.btn_font.setText(f"Шрифт: {font.family()}")
            self.save_config()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.conf['text_color'] = color.name()
            self.save_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())
