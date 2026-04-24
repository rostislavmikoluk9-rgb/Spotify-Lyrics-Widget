# Spotify Lyrics Widget

Легковесный виджет для отображения синхронизированных текстов песен Spotify поверх всех окон.

A lightweight widget for displaying synchronized Spotify lyrics on top of all windows.

## Описание / Description
Программа автоматически подхватывает играющий трек в Spotify, ищет текст в онлайн-базах и выводит его на рабочий стол с эффектом анимации. Поддерживает кэширование текстов для работы в оффлайне и экономии трафика.

The program automatically detects the playing track in Spotify, searches for lyrics in online databases, and displays them on the desktop with an animation effect. It supports lyrics caching for offline use and bandwidth saving.

**Авторы / Authors:** Ростислав Мыколюк (RoStoCheK) & Gemini (Google AI).

## Основные фишки / Key Features
* **Hot Reload:** Настройки из `config.json` применяются мгновенно без перезапуска. / Settings from `config.json` are applied instantly without restart.
* **Трей-меню / Tray Menu:** Удобное управление через системный лоток. / Convenient control via the system tray.
* **Smart Caching:** Локальное хранение текстов в `lyrics_cache`. / Local storage of lyrics in the `lyrics_cache` folder.
* **Animation:** Динамическое появление текста (эффект печатной машинки). / Dynamic text appearance (typewriter effect).

---

## Инструкция по установке / Installation Guide

### 🐧 Linux (Arch / CachyOS / Ubuntu)
Для работы требуется / Requires: `playerctl`.

1. `git clone https://github.com/rostislavmikoluk9-rgb/Spotify-Lyrics-Widget.git`
2. `cd Spotify-Lyrics-Widget`
3. `sh install.sh` — автоматическая установка / automatic setup.
4. `./run.sh` — запуск / run.

### 🪟 Windows 10 / 11
Требуется / Requires: [Python 3.12](https://www.python.org/downloads/)(or lower).

1. Распакуйте архив в любое удобное место / Extract the archive to any convenient location.
2. В терминале от имени адмнистратора. / In the terminal, as an administrator. `pip install PyQt6 syncedlyrics`
3. Запустите / Start `main.pyw`

---

## Возможные проблемы / Troubleshooting

* **Windows 11 (Transparency):** Возможна серая подложка. Решается отключением "Эффектов прозрачности" в Windows. 

A gray background may appear. Solved by disabling "Transparency effects" in Windows settings.
* **Linux (KDE/Wayland):** Принудительно включен `QT_QPA_PLATFORM=xcb` для корректного позиционирования. 

`QT_QPA_PLATFORM=xcb` is forced for correct window positioning.
* **No Lyrics:** Если текст не найден, выводится название трека. 

If lyrics are not found, the track title is displayed.

---

## Настройки / Configuration (config.json)
* `font_name` / `font_size`: Шрифт и размер. / Font family and size.
* `text_color`: Цвет текста (HEX). / Text color (HEX).
* `x`, `y`: Позиция на экране. / Screen position.
* `offset`: Корректировка тайминга. / Timing offset.

---

## Благодарности / Credits
* **Gemini (Google AI)** — logic & architecture.
* **syncedlyrics** — lyrics search engine.
* **PyQt6** — GUI framework.

## ⚠️ Дисклеймер / Disclaimer
Данное приложение является **некоммерческим проектом**. Создано исключительно в образовательных целях.

This application is a **non-commercial project**. Created for educational purposes only.
