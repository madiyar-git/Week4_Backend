#!/usr/bin/env bash
set -e

echo "==> Running Database Migrations..."
python manage.py migrate --noinput

echo "==> Collecting Static Files..."
python manage.py collectstatic --noinput

echo "==> Starting Application Server..."
exec "$@"