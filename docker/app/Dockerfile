FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential gcc \
       default-libmysqlclient-dev pkg-config \
       libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# App user
RUN adduser --disabled-password --gecos '' django \
    && chown -R django:django /app \
    && chmod +x docker/app/entrypoint.sh
# Keep running as root for volume ownership fixes in entrypoint; gunicorn runs as django

# Reasonable defaults for container
ENV DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS=* \
    DB_ENGINE=sqlite

EXPOSE 8000

ENTRYPOINT ["/app/docker/app/entrypoint.sh"]
