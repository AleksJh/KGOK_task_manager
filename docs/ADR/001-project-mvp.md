**Общий Обзор**

- Проект: `KMPC_task_manager` (Kapantask) — Django 5 + Celery + Bootstrap 5.
- Инфраструктура: Poetry для зависимостей, Ruff и Coverage для качества, Docker Compose (PostgreSQL, RabbitMQ, web, celery, nginx).
- Цели: роли админ/сервис, управление задачами и комментариями, асинхронные email-уведомления, удобный веб-интерфейс.

**Структура Проекта**

- `kapantask/`:
    - `settings.py`: конфиг Django, чтение окружения через `environs`, поддержка Celery, подключение приложений.
    - `urls.py`: админка, `tasks.urls`, аутентификация (`django.contrib.auth.urls`), отдача статики/медиа в `DEBUG`.
    - `wsgi.py` и `asgi.py`: WSGI/ASGI точки входа.
    - `celery.py`: настройка Celery, `DJANGO_SETTINGS_MODULE`, автообнаружение `tasks`.
- `tasks/`:
    - `models.py`:
    
        - `Department`.
        - `User` (наследует `AbstractUser`) с `is_admin`, `department`.
        - `Task` со статусами (New/In Progress/On Hold/Done/Cancelled), `assigned_to` (Department), `assigned_by` (User), `is_overdue` (свойство).
        - `Comment` привязан к `Task`.
        - `EmailConfiguration` для SMTP (активная конфигурация, хост, порт, SSL/TLS, креды).
    - `forms.py`:
        - `CustomAuthenticationForm`, `UserForm`, `DepartmentForm`.
        - `TaskForm` (поле `due_date` с `datetime-local`), `TaskStatusForm`.
        - `CommentForm`, `EmailConfigurationForm`.
    - `views.py`:
        - `dashboard`: метрики для админа, обзор задач для пользователя; график распределения задач по департаментам.
        - `task_list`: список задач с фильтрами по статусу, отделу (для админа), просроченности.
        - `task_detail`: детали задачи, комментарии, изменение статуса.
        - `task_create`, `task_edit`: создание/редактирование (create — только админ).
        - `department_list`, `department_create`, `department_edit`: управление отделами (только админ).
        - `email_config`: настройка SMTP (только админ).
    - `urls.py`: маршруты для login, dashboard, задач, отделов, email-конфига.
    - `signals.py`: `post_save` для `Task` и `Comment` — запуск Celery-уведомлений.
    - `tasks.py`: Celery-задачи:
        - `get_email_config`: получение активной email-конфигурации.
        - `send_task_notification`: письмо при создании новой задачи отделу/пользователям.
        - `send_comment_notification`: письмо при добавлении комментария.
    - `admin.py`: регистрация моделей, `CustomUserAdmin`, настройки отображения/поиска/фильтров.
    - `management/commands/setup_demo_data.py`: команда для демо-инициализации (отделы, админ, сервис-пользователи, набор задач с разными статусами/сроками, email-конфигурация).
    - `tests/`:
        - `test_models.py`: фабрики и тесты моделей, включая `is_overdue`.
        - `test_views.py`: аутентификация, дашборды, списки/фильтры задач, детальная страница (комментарии/статусы), отделы (доступ админов), создание задач.
- `templates/`:
    - `base.html`: общий шаблон с Bootstrap 5, навигацией и ролями.
    - `registration/login.html`: логин-форма.
    - `tasks/dashboard.html`: дашборд (админский и пользовательский).
    - `tasks/task_list.html`: список задач с фильтрами и индикаторами статусов.
    - `tasks/task_detail.html`: детали, комментарии, изменение статуса, история.
    - `tasks/task_form.html`: форма создания/редактирования задач.
    - `tasks/department_list.html` и `tasks/department_form.html`: список/форма отделов.
    - `tasks/email_config.html`: форма настройки SMTP.

**Зависимости и Poetry**

- `pyproject.toml`:
    - `python = "^3.11"` (работает и на 3.13), `django`, `celery`, `psycopg2-binary`, `django-bootstrap5`, `gunicorn`, `environs`, `factory-boy`; dev: `ruff`, `coverage`.
- Проблема: `poetry lock` падал с сообщением `'files'`. Решение: удалить `poetry.lock` и пересобрать — после этого `poetry lock` прошел.
- `poetry install` — успешная установка зависимостей.
- Ошибка `manage.py check`:
    - `environs` ожидал `marshmallow.__version_info__`, которого нет в `marshmallow 4.0.1`.
    - Решение: зафиксировали совместимую версию `marshmallow@3.20.2` (`poetry add marshmallow@3.20.2`). Проверка `manage.py check` — без ошибок.

**Запуск и Окружение**

- `runserver` упал с `OperationalError` (хост `db` не найден) — локальный запуск вне Docker не видит контейнер БД.
- Для локальной разработки создали `.env.local` с:
    - `DATABASE_URL=sqlite:///db.sqlite3`
    - `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- Рекомендации:
    - Для локального запуска переименовать `.env.local` в `.env` или добавить в `settings.py` чтение `.env.local` при наличии.
    - Для прод/докера использовать `.env` с `POSTGRES_*` и `RABBITMQ_*`.

**Docker Compose**

- В проекте есть `docker-compose.yml` и Dockerfile’ы (`docker/nginx`, `docker/web`).
- Ожидаемый запуск полного стека: `docker-compose up -d` (поднимет `db` и `broker` для Celery).
- В контейнере web — миграции, сборка статики, запуск WSGI/ASGI + Celery worker/beat по конфигу.

**Git и Репозиторий**

- Ошибка `git push -u origin master`: «src refspec master does not match any» — не было коммитов.
- Действия:
    - Создали `.gitignore` с исключениями: `__pycache__/`, `.pyc`, `db.sqlite3`, `media`, `.env`, `.env.local`, `venv/`, `.idea/`, `.vscode/`, `.DS_Store`, `Thumbs.db`, `.venv/`, и др.
    - `git reset` и `git add .` — добавили только нужные файлы; `.env` исключен игнором.
    - Выполнили первый коммит: `git commit -m "Initial commit: Kapansky GOK Task Management System"`.
- Рекомендации по пушу:
    - Установить remote: `git remote add origin <repo-url>`.
    - Проверить имя ветки на GitHub (`main` vs `master`):
        - Если remote использует `main`: `git branch -M main` и `git push -u origin main`.
        - Иначе: `git push -u origin master`.
- Предупреждения CRLF/LF при `git add` на Windows — нормальные; при необходимости настроить `git config core.autocrlf true`.

**Практические Команды**

- Установка: `poetry lock` → `poetry install`.
- Проверка: `poetry run python manage.py check`.
- Миграции: `poetry run python manage.py migrate`.
- Демо-данные: `poetry run python manage.py setup_demo_data`.
- Запуск dev-сервера: `poetry run python manage.py runserver` (для локального — с SQLite в `.env`).
- Тесты: `poetry run pytest` или `poetry run python -m pytest` (если настроены), либо `poetry run coverage run -m pytest` и `poetry run coverage html` при необходимости покрытия.
- Линтер: `poetry run ruff check .`.

**Итоги и Важные Моменты**

- Реализована полноценная система задач с ролями, отделами, комментариями, статуса́ми и метриками.
- Настроены Celery-уведомления с использованием конфигурации email из БД.
- Интерфейс на Bootstrap 5, шаблоны покрывают все основные экраны.
- Тестами покрыты модели и ключевые сценарии представлений.
- Решены проблемы с Poetry/lock и несовместимостью `marshmallow`/`environs`.
- Для локальной разработки предусмотрена конфигурация с SQLite; для продакшена — PostgreSQL и RabbitMQ через Docker.
- Репозиторий подготовлен: `.gitignore` создан, первый коммит выполнен; осталось привязать удаленный репозиторий и выполнить push в нужную ветку.