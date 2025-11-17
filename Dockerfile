# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY backend/ /app/backend/
COPY Procfile /app/

# Устанавливаем рабочую директорию в backend
WORKDIR /app/backend

# Создаем директорию для статических файлов
RUN mkdir -p /app/backend/staticfiles

# Собираем статические файлы
RUN python manage.py collectstatic --noinput || true

# Открываем порт
EXPOSE 8000

# Команда по умолчанию (переопределяется в docker-compose.yml)
CMD ["gunicorn", "core.wsgi", "--bind", "0.0.0.0:8000"]

