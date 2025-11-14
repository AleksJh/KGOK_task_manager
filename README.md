# Kapantask - Система Управления Задачами Капанского ГОК

Полноценная система управления задачами для Капанского ГОК, разработанная на Django с использованием Docker для простого развертывания.

## Функциональность

- **Администратор (Отдел горного планирования)**:
  - Аналитика и статистика по всем службам
  - Управление задачами (создание, редактирование, назначение)
  - Управление службами
  - Настройка Email-уведомлений

- **Службы (Обычные пользователи)**:
  - Просмотр и управление назначенными задачами
  - Фильтрация задач по статусам
  - Добавление комментариев к задачам

## Технический стек

- **Бэкенд**: Django 5.0+
- **База данных**: PostgreSQL
- **Асинхронные задачи**: Celery + RabbitMQ
- **Фронтенд**: Bootstrap 5
- **Контейнеризация**: Docker Compose
- **Управление зависимостями**: Poetry
- **Линтинг и форматирование**: Ruff

## Установка и запуск

### Предварительные требования

- Docker и Docker Compose
- Poetry (для локальной разработки)

### Установка с использованием Poetry

```bash
# Клонирование репозитория
git clone https://github.com/AleksJh/KGOK_task_manager
cd kapantask

# Установка зависимостей с помощью Poetry
poetry install

# Активация виртуального окружения
poetry shell
```

### Быстрый старт (Dev)

```bash
# Создание .env файла (или использование примера)
cp .env.example .env

# Запуск всех сервисов в Dev-режиме
# Используется docker-compose.override.yml: монтируется код и включён авто‑перезапуск
docker compose up -d

# Инициализация демо-данных
docker compose exec web python manage.py setup_demo_data
```

### Доступ к приложению

После запуска, приложение будет доступно по адресу: http://localhost:8000

**Вход в систему**:
- Можно входить как по имени пользователя, так и по email.
- Примеры:
  - Администратор: `admin` или `admin@kgok.ru` / `adminpass`
  - Службы: `geology` или `geology@kgok.ru` / `servicepass` (аналогично: `geomech`, `survey`, `drilling`)

**Демо-аккаунты** (инициализируются командой из раздела «Быстрый старт»):
- Администратор: `admin@kgok.ru` / `adminpass`
- Службы: `geology@kgok.ru`, `geomech@kgok.ru`, `survey@kgok.ru`, `drilling@kgok.ru` — пароль `servicepass`

## Инструкция для Production

### Генерация самоподписанного SSL-сертификата

```bash
# Создание директории для сертификатов
mkdir -p ./ssl

# Генерация приватного ключа и сертификата
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./ssl/kapantask.key -out ./ssl/kapantask.crt \
  -subj "/C=RU/ST=State/L=City/O=Kapansky GOK/CN=kapantask.local"
```

### Настройка Nginx для использования SSL

1. Убедитесь, что файлы сертификатов доступны для контейнера Nginx:

```yaml
# В docker-compose.yml
services:
  nginx:
    volumes:
      - ./ssl:/etc/nginx/ssl
```

2. Обновите конфигурацию Nginx для использования SSL:

```nginx
# В nginx/default.conf
server {
    listen 80;
    server_name kapantask.local;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name kapantask.local;
    
    ssl_certificate /etc/nginx/ssl/kapantask.crt;
    ssl_certificate_key /etc/nginx/ssl/kapantask.key;
    
    # Остальная конфигурация...
}
```

3. Перезапустите контейнеры:

```bash
docker-compose down
docker-compose up -d
```

## Разработка и тестирование

### Запуск тестов

```bash
# Запуск всех тестов
python manage.py test

# Запуск тестов с проверкой покрытия
coverage run --source='.' manage.py test
coverage report
```

### Линтинг и форматирование кода

```bash
# Проверка кода с помощью Ruff
ruff check .

# Автоматическое форматирование кода
ruff format .
```
### Разделение сред: Dev vs Prod

**Как это реализовано в проекте:**
- В продакшене исходный код копируется в образ (см. `docker/web/Dockerfile:18-33`).

- В разработке используется `docker-compose.override.yml`, который:
  - монтирует код: `./:/app`;
  - запускает Gunicorn с авто‑перезагрузкой: `--reload` (`docker-compose.override.yml:7`).

**Команды запуска:**
- Dev (с монтированием кода и авто‑перезагрузкой):
  - `docker compose up -d`
- Prod (без монтирования кода, как в образе):
  - `docker compose -f docker-compose.yml up -d`

**Переключение между режимами:**
- Остановить текущий стек: `docker compose down`
- Запустить нужный режим:
  - Dev: `docker compose up -d`
  - Prod: `docker compose -f docker-compose.yml up -d`

**Примечания:**
- На Windows важно корректное окончание строк в `entrypoint.sh`. В Dockerfile предусмотрена нормализация (`sed -i 's/\r$//' ...`).
- Если менялись зависимости, выполните пересборку: `docker compose build --no-cache && docker compose up -d`.
