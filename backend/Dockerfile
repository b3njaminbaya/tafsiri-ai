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
# --forwarded-allow-ips='*': both Render and Cloud Run terminate TLS at a
# proxy in front of this container and forward plain HTTP internally.
# Without this, uvicorn's default --forwarded-allow-ips=127.0.0.1 doesn't
# trust the proxy's X-Forwarded-Proto header (the proxy isn't 127.0.0.1),
# so Starlette's automatic trailing-slash redirect builds its Location URL
# from the scheme it actually saw — http — downgrading real HTTPS clients
# to plaintext. Verified live against a real Cloud Run deploy. Safe to
# trust unconditionally here since Cloud Run/Render's ingress is the only
# thing that can reach this container directly.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
