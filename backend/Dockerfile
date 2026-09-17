FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --retries 10 --timeout 120 -r requirements.txt

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Runs migrations before serving: this Dockerfile's CMD is what a plain
# `docker run` (and Render, which builds from this Dockerfile directly, not
# docker-compose) actually executes. infra/docker-compose.yml separately
# overrides this same command for local dev, but without this default a
# standalone deploy of this image would start serving traffic against an
# unmigrated database.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
