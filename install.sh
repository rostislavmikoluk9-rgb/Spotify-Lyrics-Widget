#!/bin/bash

# Устанавливаем системные зависимости через pacman
echo "📦 Проверка системных зависимостей (playerctl)..."
sudo pacman -S --needed --noconfirm playerctl python

# Создаем виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
    echo "создание виртуального окружения (venv)..."
    python -m venv venv
fi

# Активируем venv и ставим библиотеки
echo "🚚 Установка библиотек внутри venv..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install PyQt6 syncedlyrics

echo "✅ Готово! Теперь используй ./run.sh для запуска."
chmod +x run.sh
