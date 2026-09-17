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

# Bakes the model weights into the image at build time rather than
# downloading them from the Hub on every container start. Serverless hosts
# with ephemeral/no-persistent-disk containers (Cloud Run, HF Spaces) throw
# away everything on disk — including HF_HOME's cache — whenever an idle
# instance scales to zero, so without this every cold start re-downloads
# the ~1.6GB model from the Hub. Verified live on Cloud Run: that made cold
# starts take ~55-58s, most of it network download, not actual model init
# (which the app's own logs show completing in ~1-2s once weights are
# local). ARG (not the MODEL_NAME env var) on purpose: this only pre-warms
# the default production model; overriding MODEL_NAME at runtime for local
# dev with a smaller checkpoint still works, it just falls back to a normal
# Hub download for that different model, same as before this change.
ARG MODEL_NAME=facebook/m2m100_418M
RUN python -c "from transformers import M2M100Tokenizer, M2M100ForConditionalGeneration; M2M100Tokenizer.from_pretrained('$MODEL_NAME'); M2M100ForConditionalGeneration.from_pretrained('$MODEL_NAME')"

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
