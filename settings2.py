import sys
import json
import os  # НОВОЕ: нужно для работы с путями
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSlider, QPushButton, QFontDialog, QColorDialog)
from PyQt6.QtCore import Qt

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки виджета")
        self.setFixedSize(400, 350)

        # --- НОВОЕ: Умное определение пути к конфигу ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(current_dir, "config.json")
        # -----------------------------------------------

        self.load_config()
        self.init_ui()

    def load_config(self):
        # Теперь self.config_path содержит полный путь, например:
        # /home/ros/.local/share/spotify_widget/dist/config.json
        with open(self.config_path, "r") as f:
            self.conf = json.load(f)

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.conf, f, indent=4)

    # ... остальной код (init_ui, update_size и т.д.) без изменений ...

    def init_ui(self):
        layout = QVBoxLayout()

        # Выбор шрифта
        btn_font = QPushButton(f"Шрифт: {self.conf['font_name']}")
        btn_font.clicked.connect(self.choose_font)
        layout.addWidget(btn_font)

        # Размер шрифта
        layout.addWidget(QLabel("Размер текста:"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(10, 80)
        self.size_slider.setValue(self.conf['font_size'])
        self.size_slider.valueChanged.connect(self.update_size)
        layout.addWidget(self.size_slider)

        # Координаты X и Y
        layout.addWidget(QLabel("Позиция X (влево-вправо):"))
        self.x_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_slider.setRange(0, 1920)
        self.x_slider.setValue(self.conf['x'])
        self.x_slider.valueChanged.connect(self.update_x)
        layout.addWidget(self.x_slider)

        layout.addWidget(QLabel("Позиция Y (выше-ниже):"))
        self.y_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_slider.setRange(0, 1080)
        self.y_slider.setValue(self.conf['y'])
        self.y_slider.valueChanged.connect(self.update_y)
        layout.addWidget(self.y_slider)

        # Цвет
        btn_color = QPushButton("Выбрать цвет текста")
        btn_color.clicked.connect(self.choose_color)
        layout.addWidget(btn_color)

        self.setLayout(layout)

    def choose_font(self):
        ok, font = QFontDialog.getFont()
        if ok:
            self.conf['font_name'] = font.family()
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
