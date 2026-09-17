FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# torch gets its own layer/pip invocation (it's the largest download by far) so
# a transient network stall doesn't force re-downloading everything else too,
# and so Docker's build cache can preserve it independently.
COPY requirements-torch.txt ./
RUN pip install --retries 10 --timeout 120 -r requirements-torch.txt

COPY requirements.txt ./
RUN pip install --retries 10 --timeout 120 -r requirements.txt

# Deliberately not `training/` or requirements-training.txt — the training
# pipeline (see training/README.md) is a separate, offline toolchain with
# its own (much heavier) dependencies; it has no reason to ship in the
# always-on serving image, and app/main.py's adapter loading only ever
# imports peft when LANGUAGE_ADAPTERS is non-empty, so its absence here
# doesn't affect serving at all until a language is actually promoted.
COPY app ./app

RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /app/.cache && chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
