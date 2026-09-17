# Training pipeline: adding a Kenyan language

This is the real, working, end-to-end pipeline for taking a Kenyan language
from `KENYAN_LANGUAGES_ROADMAP` (app/main.py — no model support at all) to
an actually-serving translation adapter. It is **not** a trained model for
any language — running it today produces nothing, because there is no real
parallel-text data yet. What it gives you is the machinery that will turn
data, once it exists, into a working adapter without further engineering.

Every mechanic described below (vocabulary extension surviving/not
surviving a save-reload cycle, PEFT's embedding auto-save behavior, MPS
compatibility) was verified empirically against a real M2M100
tokenizer/model before being written into code — not assumed from
documentation. See `tests/test_training_*.py` for the proof; they run
against `valhalla/m2m100_tiny_random`, the same tiny public checkpoint the
rest of ml-service's test suite uses, so the whole pipeline is covered by
CI without downloading the real 1.6GB model.

## The five stages

```
export_dataset.py  ->  prepare_data.py  ->  finetune.py  ->  evaluate.py  ->  promote_language.py
   (pull uploads)      (clean & split)      (LoRA train)      (BLEU/chrF)      (human decides)
```

### 1. Export — pull contributed data from the app

```bash
python -m training.export_dataset \
    --api-base http://localhost:8000/api/v1 \
    --token "$API_KEY_OR_BEARER_TOKEN" \
    --source-lang en --target-lang ki \
    --out-dir ./pipeline-data/en-ki/raw
```

Pulls every dataset uploaded via the Datasets page for that language pair
(uses the language-pair filter added to `GET /datasets/` for this). Fails
loudly if nothing has been uploaded yet — check the Datasets page's "Kenyan
— data collection only" language group.

### 2. Prepare — clean, dedupe, split

```bash
python -m training.prepare_data \
    --raw-dir ./pipeline-data/en-ki/raw \
    --out-dir ./pipeline-data/en-ki/prepared \
    --source-lang en --target-lang ki
```

Parses every format the app accepts (TSV, CSV, TXT, JSON, JSONL, TMX,
XLIFF), drops empty/implausibly-long/duplicate pairs, and writes
`train.jsonl` / `val.jsonl` / `test.jsonl` plus a `summary.json` — check
`summary.json`'s `train` count before spending time on stage 3. A handful of
sentence pairs is not enough to learn anything; low hundreds is a bare
minimum to prove the mechanics produce a non-degenerate model, low thousands
before the BLEU/chrF numbers in stage 4 mean much.

### 3. Fine-tune — LoRA adapter, not a new model

```bash
python -m training.finetune \
    --base-model facebook/m2m100_418M \
    --new-lang ki --init-from sw \
    --direction en-ki \
    --train-file ./pipeline-data/en-ki/prepared/train.jsonl \
    --val-file ./pipeline-data/en-ki/prepared/val.jsonl \
    --output-dir ./pipeline-data/en-ki/adapter \
    --epochs 10 --gpu
```

What this actually does, and the two design decisions worth understanding
before touching it:

- **The new language's embedding is frozen**, copied from `--init-from` (the
  closest available M2M100 language — another Bantu language for a Bantu
  target, `en` as a defensible fallback where nothing closer exists). It is
  never trained. With genuinely low-resource data, training a 1024-dim
  embedding vector from scratch is unlikely to converge to anything useful
  anyway; the LoRA adapter (applied to attention/FFN projections) does the
  real adapting. See `vocab_extension.py`'s module docstring.
- **`facebook/m2m100_418M`'s tokenizer has no token for a language outside
  its original 100** — there's no public API for adding one.
  `vocab_extension.register_language()` reaches into the tokenizer's own
  internal bookkeeping to add it. Two non-obvious things this had to get
  right, verified empirically (`tests/test_training_vocab_extension.py`):
  - The base checkpoint ships with a few unused "made-up word" embedding
    rows beyond what `len(tokenizer)` reports. A naive `if new_id >=
    current_embedding_rows` check to decide whether to copy the init
    embedding is **wrong** — it can be false for a token that was genuinely
    just added, silently skipping initialization and leaving that language's
    embedding at meaningless random noise. Fixed by tracking "was this
    token actually new" explicitly instead of inferring it from row counts.
  - `register_language()` must be called **every time the tokenizer is
    loaded from disk**, not just once at training time — M2M100Tokenizer
    rebuilds its language bookkeeping from a fixed list on every
    construction. The special token itself survives
    `save_pretrained()`/`from_pretrained()` (it's a normal added special
    token); the "this code is a registered language" bookkeeping does not.
    `evaluate.py` and the serving integration both re-call it on load.
- **`--gpu` matters.** CPU works (and is what the test suite uses, for a
  tiny model). MPS (Apple Silicon) does not — verified directly: a plain
  embedding lookup on this model raises `RuntimeError: Placeholder storage
  has not been allocated on MPS device` partway through a real forward
  pass. `finetune.py` defaults to CPU rather than silently picking up a
  broken MPS device. For anything beyond small-scale experimentation, use a
  real CUDA GPU (a cloud instance, Colab, etc.) — LoRA keeps compute
  requirements modest, but full-precision fine-tuning of a 418M model on
  CPU is impractically slow for a real dataset.
- **Adapter checkpoints stay small on purpose.** PEFT auto-detects that the
  embedding matrix was resized and defaults to saving the *entire*
  embedding table alongside the adapter (`save_embedding_layers="auto"`) —
  for the real model that's ~500MB of a frozen, deterministically-
  reproducible tensor, saved uselessly on every single language's adapter.
  `finetune.py` passes `save_embedding_layers=False` explicitly, since
  `register_language()` reconstructs the identical frozen row on every load
  anyway. Verified this doesn't break anything: reload + generate still
  works with the flag off (`tests/test_training_finetune.py`).

### 4. Evaluate — BLEU/chrF plus samples a human should actually read

```bash
python -m training.evaluate \
    --base-model facebook/m2m100_418M \
    --adapter-dir ./pipeline-data/en-ki/adapter \
    --new-lang ki --init-from sw \
    --direction en-ki \
    --test-file ./pipeline-data/en-ki/prepared/test.jsonl \
    --out ./pipeline-data/en-ki/eval_report.json
```

Loads the adapter fresh (a genuinely separate process from training, the
same as evaluate.py or ml-service's serving process would do — proves the
save/reload cycle works, not just training in isolation), scores it with
`sacrebleu`, and includes up to 10 sample predictions verbatim in the
report. **Read the samples.** BLEU/chrF on a handful of low-resource test
sentences is noisy; a score clearing a threshold and a translation that's
actually coherent are different claims.

### 5. Promote — a human decision, not a script

```bash
python -m training.promote_language \
    --report ./pipeline-data/en-ki/eval_report.json \
    --new-lang ki --adapter-dir ./pipeline-data/en-ki/adapter
```

Checks the report against a conservative, unvalidated floor (BLEU ≥ 10,
chrF ≥ 25, ≥ 20 test examples — round numbers, not calibrated against this
product's actual quality bar, because there isn't one yet). If it clears
the floor, **prints** the exact `app/main.py` changes needed — it does not
edit the file. Moving a language from "roadmap" to "supported" is a claim
to real users that translation works; that's exactly the kind of call this
project already keeps human-reviewed everywhere else (the active-learning
review queue exists for the same reason). See `promote_language.py`'s
module docstring.

## Serving a promoted language

Once promoted, `ml-service/app/main.py`'s `LANGUAGE_ADAPTERS` dict maps the
new language to its adapter directory. This is the one part of the pipeline
that touches the always-on serving path, so it was built and tested to be
provably zero-risk when empty (the shipped default):

- `_load_model()` only imports `peft` / wraps the model in a `PeftModel` if
  `LANGUAGE_ADAPTERS` is non-empty. `requirements.txt` (the serving
  container's dependencies) deliberately doesn't include `peft` at all —
  see `test_no_adapters_configured_never_imports_peft` in
  `tests/test_language_adapters.py`, which asserts the import is never
  reached in the default configuration.
- Adapter selection (`PeftModel.set_adapter()` / `disable_adapter()`) is
  shared, mutable model state, exactly like the tokenizer's `src_lang` —
  it's guarded by the same `_inference_lock` that already protects against
  concurrent requests corrupting each other's source language (see
  `app/main.py`'s `_inference_lock` docstring). Getting this wrong would
  reintroduce the exact class of race condition that lock was built to fix.
- `tests/test_language_adapters.py` proves, over the real HTTP `/translate`
  endpoint, both that a configured adapter serves its language correctly
  and that Swahili/Somali/English keep working, unaffected, in the same
  running process with that adapter loaded alongside.

## What this doesn't do

- **No real Kenyan-language model exists yet.** Nothing here has been run
  against real data — there wasn't any when this was built. The pipeline is
  proven correct on a tiny random-weight test checkpoint, the same standard
  the rest of this service's test suite already holds itself to.
- **No automatic retraining.** Corrections submitted through the
  active-learning review queue aren't fed back into this pipeline
  automatically — that's a real next step, not attempted here.
- **No new-language-to-new-language translation** (e.g. Kikuyu directly to
  Luo, neither pretrained). Each adapter bridges one new language to an
  existing M2M100 language (English, in practice) — a harder problem this
  doesn't attempt.
- **Quality expectations should be modest for a first pass.** A LoRA
  adapter trained on a few hundred or thousand sentence pairs for a
  language the base model has never seen will not match Swahili/Somali
  quality. It's a real, measurable starting point that gets better as more
  data comes in through the Datasets page — not a finished product on the
  first run.
