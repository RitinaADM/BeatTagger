# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости для PyQt5, tkinter и других библиотек
RUN apt-get update && apt-get install -y \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libqt5widgets5 \
    libqt5gui5 \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir PyQt5 mutagen Pillow

# Указываем команду для запуска приложения
CMD ["python", "main.py"]