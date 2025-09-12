#!/usr/bin/env sh
set -e
set -o pipefail

# Ensure static/media directories exist and are writable
mkdir -p /app/static /app/media
chown -R django:django /app/static /app/media || true

# Apply database migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Launch gunicorn as non-root user for safety
exec gunicorn config.wsgi:application --config /app/gunicorn.conf.py --user django --group django
