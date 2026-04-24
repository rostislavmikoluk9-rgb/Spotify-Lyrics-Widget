import os
import platform
import subprocess
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk

# Прямые ссылки на твои файлы (замени ТВОЙ_АКК на свой ник)
GITHUB_RAW = "https://raw.githubusercontent.com/rostislavmikoluk9-rgb/Spotify-Lyrics-Widget/main/"
FILES_TO_DOWNLOAD = ["main.py", "settings.py", "icon.png"]

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Widget Installer")
        self.root.geometry("400x250")

        self.label = tk.Label(root, text="Установщик Spotify Lyrics Widget", font=("Arial", 12, "bold"))
        self.label.pack(pady=10)

        self.info = tk.Label(root, text=f"Система: {platform.system()}")
        self.info.pack()

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.btn_start = tk.Button(root, text="Начать установку", command=self.start_install, bg="green", fg="white")
        self.btn_start.pack(pady=10)

        self.status = tk.Label(root, text="Ожидание...")
        self.status.pack()

    def update_status(self, text, value):
        self.status.config(text=text)
        self.progress['value'] = value
        self.root.update()

    def start_install(self):
        self.btn_start.config(state="disabled")
        try:
            # 1. Скачивание файлов
            for i, file in enumerate(FILES_TO_DOWNLOAD):
                self.update_status(f"Скачивание {file}...", (i + 1) * 20)
                urllib.request.urlretrieve(GITHUB_RAW + file, file)

            # 2. Установка зависимостей
            self.update_status("Установка зависимостей...", 80)
            libs = ["PyQt6", "syncedlyrics"]
            if platform.system() == "Windows":
                libs.append("SwSpotify")
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + libs)
                with open("START.bat", "w") as f: f.write("pythonw main.py")
            else:
                # Для Linux (CachyOS) создаем venv
                subprocess.check_call([sys.executable, "-m", "venv", "venv"])
                pip_path = os.path.join("venv", "bin", "pip")
                subprocess.check_call([pip_path, "install"] + libs)
                with open("run.sh", "w") as f:
                    f.write("#!/bin/bash\ncd \"$(dirname \"$0\")\"\n./venv/bin/python main.py")
                os.chmod("run.sh", 0o755)

            self.update_status("Установка завершена!", 100)
            messagebox.showinfo("Готово", "Программа успешно установлена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Что-то пошло не так: {e}")
            self.btn_start.config(state="normal")

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
