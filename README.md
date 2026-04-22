# 🖥️ Spotify Desktop Lyrics Widget

A sleek, transparent, and customizable lyrics widget that stays on your desktop. It automatically fetches synced lyrics for your currently playing song on Spotify.

**Created by:** Rostyslav Mykoliuk (Idea) & Google Gemini (Realization).

---

## ✨ Features
* **Cross-Platform:** Full support for **Linux** (tested on CachyOS/Arch) and **Windows 10/11**.
* **Real-time Customization:** Built-in settings menu to change fonts, colors, and position without restarting.
* **Transparent UI:** No background, no borders—just the lyrics floating on your wallpaper.
* **Smart Sync:** Compensates for system delays to keep lyrics in time with the music.

---

## 🛠️ Requirements

### Python version 3.13(or lower) is required

## Python Dependencies

Install the required libraries using pip:
```bash
pip install PyQt6 syncedlyrics
```
Or
```
python -m pip install PyQt6 syncedlyrics
```
### System-Specific Requirements
* **Windows:**
  ```bash
  pip install winsdk
  ```
  Or
  ```
  python -m pip install winsdk
  ```
* **Linux:**
  Requires `playerctl` to be installed on your system:
  ```bash
  # Arch Linux / CachyOS
  sudo pacman -S playerctl
  ```

---

## 🚀 How to Use

1.1 **Run the application (For Linux):**
   
   In terminal from folder  
   ```bash
   python main.py
   ```
1.2 **Run the application (For Windows):**
   ```
   simply just run main.pyw
   ```
2. **Customize:**
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
