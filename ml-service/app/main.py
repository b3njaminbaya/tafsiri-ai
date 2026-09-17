import logging
import os
import threading
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from .glossary import find_glossary_terms

logger = logging.getLogger("ml-service")
logging.basicConfig(level=logging.INFO)

# facebook/m2m100_418M is the real production default: a genuinely multilingual
# (100-language) open translation model whose tokenizer speaks plain ISO codes
# (sw, am, ha, yo, zu, ...) that already match what the rest of this app uses,
# unlike NLLB-200's FLORES-200 codes (swh_Latn, ...) which would need a mapping
# table. Override via MODEL_NAME for local dev with a smaller/tiny checkpoint.
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/m2m100_418M")

MAX_BATCH_SIZE = 50

# Kenya-only, by design: this product's scope is Kenyan languages, not a
# general-purpose translator. Of Kenya's ~68 living languages, Swahili and
# Somali are the only two M2M100 was actually pretrained on — Swahili is
# Kenya's national/official language and the East African lingua franca;
# Somali is spoken by ethnic-Somali communities in northeastern Kenya.
# English is kept as the one deliberate exception: it's Kenya's other
# constitutional official language (Constitution of Kenya, 2010, Art. 7), and
# without it the only working pair would be Swahili<->Somali directly — a
# pairing almost nobody actually needs. Real demand is Kenyan-language<->
# English, and English also serves as the practical bridge for future
# Kenyan-language<->Kenyan-language routes once more are trained. Every other
# previously-supported language (Spanish, French, German, Amharic, Hausa,
# Yoruba, Zulu, ...) has been deliberately removed — this product does not
# translate non-Kenyan languages. See KENYAN_LANGUAGES_ROADMAP below for the
# Kenyan languages not supported yet, and why that's a data problem, not a
# config change.
SUPPORTED_LANGUAGES = {
    "sw": "Swahili",
    "so": "Somali",
    "en": "English",
}

# Codes above that are actual Kenyan-origin languages (deliberately excludes
# "en" — kept for practicality, not because English is Kenyan) — exposed via
# GET /languages so the frontend can prioritize them without hardcoding a
# separate list that could drift out of sync with this one.
KENYAN_LANGUAGE_CODES = {"sw", "so"}

# Real Kenyan languages with no pretrained coverage in M2M100 (or any other
# public multilingual model at this scale) — not selectable for translation,
# because accepting one would silently mistranslate it as whichever language
# the model actually recognizes rather than fail loudly. Exposed via
# GET /languages/roadmap so the frontend can (a) show an honest "not yet"
# list instead of pretending these aren't real gaps, and (b) use `code` to
# tag dataset uploads for these languages, so data collection for a language
# can start well before translation support exists — see
# datasets.py:ALLOWED_DATASET_LANGUAGE_CODES.
#
# `code` is ISO 639-1 where one exists, else ISO 639-3, to the best of this
# codebase's knowledge — verify against SIL/Ethinologue before treating as
# authoritative for anything beyond this app's own dataset tagging. `code:
# None` marks languages that are dialect clusters without one standard code
# (e.g. Mijikenda) or where the exact code wasn't confidently known when this
# list was written — a real gap in this list, not a claim there's no code.
# This is not exhaustive: Kenya has ~68 living languages (Ethnologue); this
# covers the larger/better-documented ones. Extending it is welcome.
KENYAN_LANGUAGES_ROADMAP = [
    {"code": "ki", "name": "Kikuyu (Gĩkũyũ)", "family": "Bantu"},
    {"code": "luo", "name": "Luo (Dholuo)", "family": "Nilotic"},
    {"code": "kln", "name": "Kalenjin", "family": "Nilotic"},
    {"code": "kam", "name": "Kamba (Kikamba)", "family": "Bantu"},
    {"code": "guz", "name": "Kisii (Ekegusii)", "family": "Bantu"},
    {"code": "mas", "name": "Maasai (Maa)", "family": "Nilotic"},
    {"code": "luy", "name": "Luhya", "family": "Bantu"},
    {"code": "mer", "name": "Meru (Kimeru)", "family": "Bantu"},
    {"code": None, "name": "Mijikenda", "family": "Bantu"},
    {"code": "tuv", "name": "Turkana", "family": "Nilotic"},
    {"code": "ebu", "name": "Embu (Kiembu)", "family": "Bantu"},
    {"code": "teo", "name": "Teso (Iteso)", "family": "Nilotic"},
    {"code": "dav", "name": "Taita (Dawida)", "family": "Bantu"},
    {"code": "kuj", "name": "Kuria", "family": "Bantu"},
    {"code": "saq", "name": "Samburu", "family": "Nilotic"},
    {"code": "pkb", "name": "Pokomo", "family": "Bantu"},
    {"code": "rel", "name": "Rendille", "family": "Cushitic"},
]

# Populated by a maintainer after training/promote_language.py confirms a
# fine-tuned language adapter clears the quality floor — see that script's
# printed instructions for exactly how an entry gets added here. Empty by
# default: with nothing configured, _load_model()/_generate() below take the
# exact same code path they always have — no PEFT import, no adapter
# lookup, _model stays a plain M2M100ForConditionalGeneration. Verified in
# tests/test_language_adapters.py's "no adapters configured" cases.
# {lang_code: (init_from_code, adapter_directory_path)}
LANGUAGE_ADAPTERS: Dict[str, Tuple[str, str]] = {}

# Which of LANGUAGE_ADAPTERS' keys actually loaded successfully at startup —
# a language whose adapter file is missing/corrupt is logged and skipped
# rather than crashing ml-service, since a bad config for one new language
# must not take down the working sw/so/en path.
_adapter_languages: set = set()

_model = None
_tokenizer = None
_load_lock = threading.Lock()
# Guards the tokenizer's mutable src_lang state + the encode/generate call
# together as one critical section. FastAPI runs sync `def` endpoints in a
# thread pool, so two concurrent requests really do run in parallel threads;
# without this, `_tokenizer.src_lang = X` from one request can be overwritten
# by another before the first request's own `_tokenizer(texts, ...)` call
# reads it back, silently encoding that request's text with the wrong source
# language. _load_lock only ever guarded model *loading*, never this.
_inference_lock = threading.Lock()


def _load_model() -> None:
    global _model, _tokenizer
    if _model is not None:
        return
    with _load_lock:
        if _model is not None:
            return
        from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

        logger.info("Loading translation model %r ...", MODEL_NAME)
        _tokenizer = M2M100Tokenizer.from_pretrained(MODEL_NAME)
        _model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME)
        _model.eval()
        logger.info("Model %r loaded.", MODEL_NAME)

        if LANGUAGE_ADAPTERS:
            _load_language_adapters()


def _load_language_adapters() -> None:
    """Wraps the base model with PEFT multi-adapter support for every
    language configured in LANGUAGE_ADAPTERS. Only called when that dict is
    non-empty (see _load_model above) — no PEFT import or model wrapping
    happens otherwise.
    """
    global _model
    from peft import PeftModel

    from training.vocab_extension import register_language

    for lang_code, (init_from_code, adapter_dir) in LANGUAGE_ADAPTERS.items():
        try:
            register_language(_tokenizer, _model, lang_code, init_from_code=init_from_code)
            if isinstance(_model, PeftModel):
                _model.load_adapter(adapter_dir, adapter_name=lang_code)
            else:
                _model = PeftModel.from_pretrained(_model, adapter_dir, adapter_name=lang_code)
            _adapter_languages.add(lang_code)
            logger.info("Loaded language adapter for %r from %r", lang_code, adapter_dir)
        except Exception:
            logger.exception(
                "Failed to load language adapter for %r from %r — %r stays unsupported this run",
                lang_code,
                adapter_dir,
                lang_code,
            )
    if isinstance(_model, PeftModel):
        _model.eval()


@asynccontextmanager
async def _lifespan(app: FastAPI):
    # Preload at startup instead of lazily on the first request: without
    # this, whichever user's request happens to arrive first after a deploy
    # or restart pays the full ~1.6GB model-load latency (tens of seconds),
    # which is a plausible way to trip a load balancer's request timeout
    # rather than just a slow readiness check.
    _load_model()
    yield


app = FastAPI(title="Tafsiri AI ML Service", version="0.1.0", lifespan=_lifespan)


# langdetect is non-deterministic run-to-run for ambiguous/short text unless
# seeded (a documented langdetect gotcha) — fixed once at import time so
# repeated calls with the same input give the same answer.
def _seed_langdetect() -> None:
    try:
        from langdetect import DetectorFactory

        DetectorFactory.seed = 0
    except Exception:
        pass


_seed_langdetect()


def _detect_language(text: str) -> Optional[str]:
    """Returns a supported language code, or None if detection failed or
    landed on a language this service doesn't support — callers must treat
    None as "could not auto-detect", not silently translate as English
    (the previous behavior: any failure, or any real detection outside the
    curated SUPPORTED_LANGUAGES list, was coerced to "en" with no signal,
    so e.g. a Swahili sentence too short for langdetect's n-gram model could
    come back mistranslated and labeled source_lang: "en" as if authoritative).
    """
    try:
        from langdetect import detect

        code = detect(text)
    except Exception:
        return None
    return code if code in SUPPORTED_LANGUAGES else None


def _resolve_source_lang(source_lang: Optional[str], text: str) -> str:
    explicit = source_lang if source_lang and source_lang != "auto" else None
    if explicit:
        return explicit
    detected = _detect_language(text)
    if detected is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not reliably auto-detect the source language (the text may be "
                "too short/ambiguous, or in a language this service doesn't support). "
                "Please specify source_lang explicitly."
            ),
        )
    return detected


def _validate_languages(source_lang: str, target_lang: str) -> None:
    if source_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported source language: {source_lang}")
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {target_lang}")


def _sequence_confidences(generated) -> List[float]:
    """Per-row geometric-mean token probability, as a proxy confidence score —
    replaces the previous hardcoded 0.42 placeholder with a real (if rough)
    model-derived signal. Works for both a single sequence and a batch.
    """
    import torch

    if not getattr(generated, "scores", None):
        return [0.5] * generated.sequences.shape[0]
    transition_scores = _model.compute_transition_scores(
        generated.sequences,
        generated.scores,
        beam_indices=getattr(generated, "beam_indices", None),
        normalize_logits=True,
    )
    results = []
    for row in transition_scores:
        valid = row[row > -1e8]
        if valid.numel() == 0:
            results.append(0.5)
        else:
            results.append(float(torch.clamp(torch.exp(valid.mean()), 0.0, 1.0).item()))
    return results


def _generate(
    texts: List[str],
    source_lang: str,
    target_lang: str,
    force_words_ids: Optional[List[List[int]]] = None,
) -> List[Tuple[str, float]]:
    """Runs one real batched generate() call over `texts` (a batch of 1 for a
    single translation, or many for /translate/batch). force_words_ids, when
    given, applies uniformly across the whole batch — see translate_batch()
    for why that means items needing different forced terms can't share a call.

    source_lang == target_lang is short-circuited before this is even called
    (see _maybe_noop_translation) — every call here is a real translation.
    """
    _load_model()
    generate_kwargs = dict(
        max_new_tokens=512,
        output_scores=True,
        return_dict_in_generate=True,
    )
    if force_words_ids:
        generate_kwargs["force_words_ids"] = force_words_ids
        generate_kwargs["num_beams"] = 4

    import torch

    # Setting _tokenizer.src_lang and then reading it back via _tokenizer(...)
    # is two steps on shared, mutable module state — held together under one
    # lock so a concurrent request for a different source_lang can't
    # interleave between them (see _inference_lock's docstring above).
    with _inference_lock:
        _tokenizer.src_lang = source_lang
        encoded = _tokenizer(texts, return_tensors="pt", padding=True)
        generate_kwargs["forced_bos_token_id"] = _tokenizer.get_lang_id(target_lang)

        # Which adapter (if any) applies to this request is also shared,
        # mutable model state (PeftModel.set_adapter/disable_adapter), so it
        # belongs in the same critical section as the tokenizer's src_lang —
        # same hazard _inference_lock's docstring describes, just a second
        # piece of state that can leak between concurrent requests otherwise.
        #
        # Guarded on _adapter_languages, not just isinstance(_model,
        # PeftModel): peft is a training-only dependency (see
        # requirements-training.txt), deliberately absent from the serving
        # container's requirements.txt. `_adapter_languages` is empty
        # whenever LANGUAGE_ADAPTERS is (the shipped default), so this
        # import is never reached in a normal serving deployment — import
        # peft here unconditionally and every translation call would crash
        # with ModuleNotFoundError the moment it's not installed.
        if _adapter_languages:
            from peft import PeftModel

            adapter = _select_adapter_for(source_lang, target_lang) if isinstance(_model, PeftModel) else None
            if adapter:
                _model.set_adapter(adapter)
                with torch.no_grad():
                    generated = _model.generate(**encoded, **generate_kwargs)
            elif isinstance(_model, PeftModel):
                with _model.disable_adapter(), torch.no_grad():
                    generated = _model.generate(**encoded, **generate_kwargs)
            else:
                with torch.no_grad():
                    generated = _model.generate(**encoded, **generate_kwargs)
        else:
            with torch.no_grad():
                generated = _model.generate(**encoded, **generate_kwargs)
        outputs = _tokenizer.batch_decode(generated.sequences, skip_special_tokens=True)

    confidences = _sequence_confidences(generated)
    return list(zip(outputs, confidences))


def _select_adapter_for(source_lang: str, target_lang: str) -> Optional[str]:
    """Which loaded language adapter (if any) applies to this request — the
    adapter for whichever side of the pair is the newly-added language (see
    training/finetune.py: adapters exist for new-language<->existing-language
    pairs, never new<->new). None means "use the base model with no adapter
    active", the correct behavior for an all-base-language pair like sw<->en
    even when some other language's adapter happens to be loaded alongside.
    """
    if source_lang in _adapter_languages:
        return source_lang
    if target_lang in _adapter_languages:
        return target_lang
    return None


def _maybe_noop_translation(text: str, source_lang: str, target_lang: str) -> Optional[Tuple[str, float]]:
    """Same-language requests need no model call at all — previously they
    still ran a full generate() for a "translation" that was really just a
    lossy round-trip through the model.
    """
    if source_lang == target_lang:
        return text, 1.0
    return None


def _force_words_ids_for(terms: List[str]) -> List[List[int]]:
    return [_tokenizer(term, add_special_tokens=False).input_ids for term in terms]


def _resolve_forced_terms(item: "TranslateRequest", source_lang: str) -> List[str]:
    if item.forced_terms is not None:
        return item.forced_terms
    return find_glossary_terms(item.domain, source_lang, item.target_lang, item.text)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = None
    target_lang: str
    domain: Optional[str] = None
    # None (default): fall back to this service's own small internal glossary
    # (app/glossary.py). A list (even empty): use exactly these terms instead
    # — this is what lets the backend own a real, DB-backed, admin-manageable
    # glossary while ml-service still does the actual constrained decoding.
    forced_terms: Optional[List[str]] = None

    @field_validator("text")
    @classmethod
    def _text_must_have_content(cls, value: str) -> str:
        # min_length=1 alone blocks "" but not "   " — whitespace-only text
        # was reaching langdetect (which either throws, now handled, or
        # returns a meaningless code) and then a full generate() call.
        if not value.strip():
            raise ValueError("text must not be empty or whitespace-only")
        return value


class TranslateResponse(BaseModel):
    translation: str
    source_lang: str
    target_lang: str
    confidence: float
    applied_glossary_terms: List[str] = []


class BatchTranslateRequest(BaseModel):
    items: List[TranslateRequest] = Field(..., min_length=1, max_length=MAX_BATCH_SIZE)


class BatchTranslateResponse(BaseModel):
    results: List[TranslateResponse]


@app.get("/health")
def health():
    """Liveness only — the process is up and answering HTTP. Always 200, even
    before the model has loaded. Use /ready for a real readiness check.
    """
    return {"status": "ok", "model_name": MODEL_NAME, "model_loaded": _model is not None}


@app.get("/ready")
def ready():
    """A real readiness probe, unlike /health: 503 until the model has
    actually finished loading. With the startup preload above this should
    only ever be momentarily false right after process start, not on every
    first request the way lazy-loading used to make it.
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model is still loading")
    return {"status": "ready", "model_name": MODEL_NAME}


@app.get("/languages")
def languages():
    return {
        "languages": [
            {"code": c, "name": n, "kenyan": c in KENYAN_LANGUAGE_CODES}
            for c, n in SUPPORTED_LANGUAGES.items()
        ]
    }


@app.get("/languages/roadmap")
def languages_roadmap():
    """Real Kenyan languages not yet supported — see KENYAN_LANGUAGES_ROADMAP."""
    return {"languages": KENYAN_LANGUAGES_ROADMAP}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    source_lang = _resolve_source_lang(req.source_lang, req.text)
    _validate_languages(source_lang, req.target_lang)
    _load_model()

    noop = _maybe_noop_translation(req.text, source_lang, req.target_lang)
    if noop is not None:
        output_text, confidence = noop
        return TranslateResponse(
            translation=output_text,
            source_lang=source_lang,
            target_lang=req.target_lang,
            confidence=confidence,
            applied_glossary_terms=[],
        )

    # Domain "customization" without a training loop: force the correct
    # domain-specific term into the output via constrained beam search rather
    # than leaving it to chance. This is what makes the `domain` field on
    # TranslateRequest actually change the output, instead of being stored and
    # ignored.
    forced_terms = _resolve_forced_terms(req, source_lang)
    force_words_ids = _force_words_ids_for(forced_terms) if forced_terms else None

    [(output_text, confidence)] = _generate([req.text], source_lang, req.target_lang, force_words_ids)

    return TranslateResponse(
        translation=output_text,
        source_lang=source_lang,
        target_lang=req.target_lang,
        confidence=confidence,
        applied_glossary_terms=forced_terms,
    )


@app.post("/translate/batch", response_model=BatchTranslateResponse)
def translate_batch(req: BatchTranslateRequest):
    _load_model()

    resolved: List[Tuple[TranslateRequest, str]] = []
    for item in req.items:
        source_lang = _resolve_source_lang(item.source_lang, item.text)
        _validate_languages(source_lang, item.target_lang)
        resolved.append((item, source_lang))

    results: List[Optional[TranslateResponse]] = [None] * len(req.items)

    # Items needing glossary term-forcing are translated individually:
    # force_words_ids applies uniformly across an entire generate() call, so
    # items requiring different forced terms can't share one batched call.
    # Everything else is grouped by (source_lang, target_lang) and translated
    # in a single real batched generate() call per group — genuine batching,
    # not a loop dressed up as one.
    groups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for idx, (item, source_lang) in enumerate(resolved):
        noop = _maybe_noop_translation(item.text, source_lang, item.target_lang)
        if noop is not None:
            output_text, confidence = noop
            results[idx] = TranslateResponse(
                translation=output_text,
                source_lang=source_lang,
                target_lang=item.target_lang,
                confidence=confidence,
                applied_glossary_terms=[],
            )
            continue

        forced_terms = _resolve_forced_terms(item, source_lang)
        if forced_terms:
            force_words_ids = _force_words_ids_for(forced_terms)
            [(output_text, confidence)] = _generate(
                [item.text], source_lang, item.target_lang, force_words_ids
            )
            results[idx] = TranslateResponse(
                translation=output_text,
                source_lang=source_lang,
                target_lang=item.target_lang,
                confidence=confidence,
                applied_glossary_terms=forced_terms,
            )
        else:
            groups[(source_lang, item.target_lang)].append(idx)

    for (source_lang, target_lang), indices in groups.items():
        texts = [resolved[i][0].text for i in indices]
        outputs = _generate(texts, source_lang, target_lang, None)
        for i, (output_text, confidence) in zip(indices, outputs):
            results[i] = TranslateResponse(
                translation=output_text,
                source_lang=source_lang,
                target_lang=target_lang,
                confidence=confidence,
                applied_glossary_terms=[],
            )

    return BatchTranslateResponse(results=results)
