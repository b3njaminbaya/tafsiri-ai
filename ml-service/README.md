# ML Service

Model-serving microservice for the NMT Agent. Wraps a Hugging Face
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

- `GET /health` — `{"status": "ok", "model_name": ..., "model_loaded": bool}`. The
  model is lazy-loaded on first `/translate` call, not at startup, so health
  checks don't block on a multi-GB download.
- `GET /languages` — the curated set of supported language codes/names. This
  list deliberately includes low-resource languages (Swahili, Amharic, Hausa,
  Igbo, Yoruba, Zulu, Xhosa, Somali, Lingala, Wolof, Fulah, Ganda) alongside
  the common ones — that coverage is this product's actual differentiator.
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
