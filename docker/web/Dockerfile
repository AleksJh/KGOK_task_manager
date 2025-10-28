FROM python:3.11-slim

WORKDIR /app

# Установка Poetry
RUN pip install poetry==1.7.1

# Копирование файлов проекта
COPY pyproject.toml poetry.lock /app/

# Настройка Poetry для не создания виртуального окружения внутри контейнера
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-dev --no-interaction --no-ansi

# Копирование остальных файлов проекта
COPY . /app/

# Создание директорий для статических и медиа файлов
RUN mkdir -p /app/static /app/media

# Сбор статических файлов
RUN python manage.py collectstatic --noinput

# Запуск миграций
RUN python manage.py migrate

# Порт для Gunicorn
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "kapantask.wsgi:application", "--bind", "0.0.0.0:8000"]