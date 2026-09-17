# ML Service

Model-serving microservice for Tafsiri AI. Wraps a Hugging Face
multilingual translation model (`facebook/m2m100_418M` by default) behind a
small FastAPI surface consumed by the backend's `/api/v1/translate` route.

## Why M2M100 (not NLLB-200)

Both are legitimate many-to-many multilingual models with strong low-resource
language coverage. M2M100's tokenizer uses plain ISO 639-1-ish codes (`sw`,
`am`, `ha`, `yo`, `zu`, ...) that already match what the rest of this app uses
everywhere else, whereas NLLB-200 uses FLORES-200 codes (`swh_Latn`, ...) that
would need a separate mapping table. Swapping to NLLB-200 later is possible by
changing `MODEL_NAME` and swapping the tokenizer/model classes in
`app/main.py` if its broader language coverage becomes worth the extra
mapping layer.

## Endpoints

- `GET /health` — `{"status": "ok", "model_name": ..., "model_loaded": bool}`.
  Liveness only, always 200 — the model is preloaded at startup via a FastAPI
  lifespan handler, so this doesn't reflect load state on its own.
- `GET /ready` — 503 until the model has actually finished loading; use this,
  not `/health`, for a real readiness probe.
- `GET /languages` — the supported language codes/names, each flagged
  `"kenyan": true/false`. **This product is Kenya-only**: Swahili and
  Somali (`kenyan: true`) plus English, kept as the one deliberate exception
  — it's Kenya's other constitutional official language, and without it the
  only working pair would be Swahili<->Somali directly, which almost no one
  needs. Every other M2M100 language (Spanish, French, Amharic, Hausa, ...)
  has been deliberately removed; this is not a general-purpose translator.
- `GET /languages/roadmap` — real Kenyan languages (Kikuyu, Luo, Kalenjin,
  Kamba, Kisii, Maasai, Luhya, Meru, Mijikenda, Turkana, and more) that are
  **not** supported yet, because M2M100 has no pretrained coverage for them —
  an honest "not yet" list rather than a silent gap. Supporting these for
  real needs parallel-text data and fine-tuning (or a different base model),
  not a code change.
- `POST /translate` — `{text, source_lang?, target_lang, domain?}` →
  `{translation, source_lang, target_lang, confidence}`. If `source_lang` is
  omitted or `"auto"`, language is detected with `langdetect`. `confidence` is
  a real (if rough) geometric-mean token probability from the model's own
  generation scores — not a hardcoded number.

## Local development

```bash
pip install -r requirements.txt
MODEL_NAME=facebook/m2m100_418M uvicorn app.main:app --reload --port 8001
```

The first `/translate` request downloads and caches the model (~1.6GB for the
418M checkpoint) under `~/.cache/huggingface`. For a fast smoke test of the
wiring itself (tokenization, generation loop, confidence scoring) without a
large download, override the model:

```bash
MODEL_NAME=valhalla/m2m100_tiny_random uvicorn app.main:app --reload --port 8001
```

That checkpoint shares the exact same architecture/tokenizer classes as the
production model — it exercises the identical code path, just with random
(untrained) weights, so its actual translations are meaningless but the
plumbing is fully verified.

In `docker-compose`, model weights persist across rebuilds in the
`ml-model-cache` volume so they aren't re-downloaded on every `--build`.

The production `Dockerfile` takes a different approach: it downloads and
bakes the model weights into the image itself at build time (see the `ARG
MODEL_NAME` / `RUN python -c "...from_pretrained..."` step), rather than
relying on a persistent volume. That's because the production host (Cloud
Run) has an ephemeral container filesystem with no persistent disk — every
scale-to-zero cold start would otherwise re-download the ~1.6GB model from
the Hub, which pushed cold-start latency to ~55-58 seconds in practice, most
of it network download rather than actual model init (which completes in
1-2 seconds once the weights are already local).

## Adding a Kenyan language

See [`training/README.md`](training/README.md) for the full pipeline —
pulling contributed parallel text from the Datasets page, cleaning it, LoRA
fine-tuning M2M100 on a language it was never pretrained on, evaluating the
result, and serving it. It's a separate offline toolchain
(`requirements-training.txt`, not installed in the serving image) with real,
tested mechanics — it just has no real Kenyan-language data to run on yet.
