#!/bin/sh
set -e

# Управляет выполнением миграций при старте контейнера
MIGRATE_ON_START=${MIGRATE_ON_START:-true}
COLLECTSTATIC_ON_START=${COLLECTSTATIC_ON_START:-true}

wait_for_db() {
  host=${POSTGRES_HOST:-localhost}
  port=${POSTGRES_PORT:-5432}
  echo "Ожидание БД ${host}:${port}..."
  # До 30 попыток подключения
  max_retries=30
  counter=0
  while ! python - <<'PY'
import os, sys
import psycopg2
host=os.environ.get('POSTGRES_HOST','localhost')
port=int(os.environ.get('POSTGRES_PORT','5432'))
user=os.environ.get('POSTGRES_USER','postgres')
password=os.environ.get('POSTGRES_PASSWORD','postgres')
dbname=os.environ.get('POSTGRES_DB','postgres')
try:
    psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
except Exception:
    sys.exit(1)
PY
  do
    counter=$((counter+1))
    if [ $counter -ge $max_retries ]; then
      echo "БД не готова после ${max_retries} попыток"
      exit 1
    fi
    echo "БД недоступна, повтор ${counter}/${max_retries}..."
    sleep 2
  done
  echo "БД доступна."
}

if [ "$MIGRATE_ON_START" = "true" ]; then
  wait_for_db
  echo "Выполняю миграции..."
  python manage.py migrate --noinput
fi

if [ "$COLLECTSTATIC_ON_START" = "true" ]; then
  echo "Собираю статику..."
  python manage.py collectstatic --noinput
fi

echo "Запуск приложения: $@"
exec "$@"