#!/usr/bin/env sh
set -e

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Launch gunicorn
exec gunicorn config.wsgi:application --config /app/gunicorn.conf.py

