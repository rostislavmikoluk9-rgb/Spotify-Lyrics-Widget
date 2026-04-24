import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QPushButton, QFontDialog, QColorDialog)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки виджета")
        self.setFixedSize(400, 350)

        # Используем абсолютный путь, чтобы на Linux не было проблем с запуском из разных папок
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "config.json")

        self.load_config()
        self.init_ui()

    def load_config(self):
        try:
            with open(self.config_path, "r", encoding='utf-8') as f:
                self.conf = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
            # Дефолтные настройки на случай ошибки
            self.conf = {"font_name": "Arial", "font_size": 24, "x": 100, "y": 100, "text_color": "white"}

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding='utf-8') as f:
                json.dump(self.conf, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def init_ui(self):
        layout = QVBoxLayout()

        # Выбор шрифта
        self.btn_font = QPushButton(f"Шрифт: {self.conf['font_name']}")
        self.btn_font.clicked.connect(self.choose_font)
        layout.addWidget(self.btn_font)

        # Размер шрифта
        layout.addWidget(QLabel("Размер текста:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 80)
        self.size_slider.setValue(self.conf['font_size'])
        self.size_slider.valueChanged.connect(self.update_size)
        layout.addWidget(self.size_slider)

        # Позиция X
        layout.addWidget(QLabel("Позиция X (влево-вправо):"))
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(0, 1920)
        self.x_slider.setValue(self.conf['x'])
        self.x_slider.valueChanged.connect(self.update_x)
        layout.addWidget(self.x_slider)

        # --- ВОТ ЭТОТ БЛОК НУЖНО ВЕРНУТЬ ---
        # Позиция Y
        layout.addWidget(QLabel("Позиция Y (выше-ниже):"))
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(0, 1080)
        self.y_slider.setValue(self.conf.get('y', 100)) # Используем .get на всякий случай
        self.y_slider.valueChanged.connect(self.update_y)
        layout.addWidget(self.y_slider)
        # ------------------------------------

        # Синхронизация (задержка)
        layout.addWidget(QLabel("Синхронизация (задержка):"))
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setRange(-50, 50)
        self.offset_slider.setValue(int(self.conf.get('offset', 0.0) * 10))
        self.offset_slider.valueChanged.connect(self.update_offset)
        layout.addWidget(self.offset_slider)

        # Цвет
        self.btn_color = QPushButton("Выбрать цвет текста")
        self.btn_color.clicked.connect(self.choose_color)
        layout.addWidget(self.btn_color)

        self.setLayout(layout)

    def update_offset(self, val):
        self.conf['offset'] = val / 10.0
        self.save_config()

    def choose_font(self):
        try:
            font, ok = QFontDialog.getFont(self)
            if ok and font:
                font_family = font.family()
                if font_family:
                    self.conf['font_name'] = font_family
                    # Теперь self.btn_font существует!
                    self.btn_font.setText(f"Шрифт: {font_family}")
                    self.save_config()
                    print(f"Шрифт изменен на: {font_family}")
        except Exception as e:
            print(f"Ошибка при выборе шрифта: {e}")

    def update_size(self, val):
        self.conf['font_size'] = val
        self.save_config()

    def update_x(self, val):
        self.conf['x'] = val
        self.save_config()

    def update_y(self, val):
        self.conf['y'] = val
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
