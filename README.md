# 🖥️ Spotify Desktop Lyrics Widget

A sleek, transparent, and customizable lyrics widget that stays on your desktop. It automatically fetches synced lyrics for your currently playing song on Spotify (or other media players).

**Created by:** Rostyslav Mykoliuk (Idea) & Google Gemini (Realization).

---

## ✨ Features
* **Cross-Platform:** Full support for **Linux** (tested on CachyOS/Arch) and **Windows 10/11**.
* **Real-time Customization:** Built-in settings menu to change fonts, colors, and position without restarting.
* **Transparent UI:** No background, no borders—just the lyrics floating on your wallpaper.
* **Smart Sync:** Compensates for system delays to keep lyrics in time with the music.

---

## 🛠️ Requirements

### Python Dependencies
Install the required libraries using pip:
```bash
pip install PyQt6 syncedlyrics
```

### System-Specific Requirements
* **Windows:**
  ```bash
  pip install winsdk
  ```
* **Linux:**
  Requires `playerctl` to be installed on your system:
  ```bash
  # Arch Linux / CachyOS
  sudo pacman -S playerctl
  ```

---

## 🚀 How to Use

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/rostislavmikoluk9-rgb/spotify-lyrics-widget.git](https://github.com/rostislavmikoluk9-rgb/spotify-lyrics-widget.git)
   cd spotify-lyrics-widget
   ```
2. **Run the application:**
   ```bash
   python main.py
   ```
3. **Customize:**
   * **Right-click** the tray icon (cherry/app icon) and select **"Настройки" (Settings)**.
   * Or manually edit the `config.json` file.
   * You can adjust: **X/Y position, Font Family, Font Size, and Text Color**.

---

## 💡 Technical Notes & Fixes

### Windows 11 Transparency
If you see a grey background/border on Windows:
1. Go to **Windows Settings > Personalization > Colors**.
2. Toggle **Transparency Effects** OFF and then ON again.

### Performance
Minimal CPU usage thanks to efficient system-level media polling (`winsdk` for Windows and `dbus/playerctl` for Linux).

---

## 🧪 Tested On
* **OS:** Arch Linux (CachyOS), Windows 11
