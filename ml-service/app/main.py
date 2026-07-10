import logging
import os
import threading
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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

# A curated subset of the ~100 languages M2M100 supports, deliberately
# emphasizing low-resource languages underserved by mainstream translation
# APIs — this list is this product's actual value proposition, not just a
# demo dropdown.
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "sw": "Swahili",
    "am": "Amharic",
    "ha": "Hausa",
    "ig": "Igbo",
    "yo": "Yoruba",
    "zu": "Zulu",
    "xh": "Xhosa",
    "so": "Somali",
    "ln": "Lingala",
    "wo": "Wolof",
    "ff": "Fulah",
    "lg": "Ganda",
}

app = FastAPI(title="NMT Agent ML Service", version="0.1.0")

_model = None
_tokenizer = None
_load_lock = threading.Lock()


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


def _detect_language(text: str) -> str:
    try:
        from langdetect import detect

        code = detect(text)
        return code if code in SUPPORTED_LANGUAGES else "en"
    except Exception:
        return "en"


def _resolve_source_lang(source_lang: Optional[str], text: str) -> str:
    explicit = source_lang if source_lang and source_lang != "auto" else None
    return explicit or _detect_language(text)


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
    """
    _load_model()
    _tokenizer.src_lang = source_lang
    encoded = _tokenizer(texts, return_tensors="pt", padding=True)

    generate_kwargs = dict(
        forced_bos_token_id=_tokenizer.get_lang_id(target_lang),
        max_new_tokens=512,
        output_scores=True,
        return_dict_in_generate=True,
    )
    if force_words_ids:
        generate_kwargs["force_words_ids"] = force_words_ids
        generate_kwargs["num_beams"] = 4

    import torch

    with torch.no_grad():
        generated = _model.generate(**encoded, **generate_kwargs)

    outputs = _tokenizer.batch_decode(generated.sequences, skip_special_tokens=True)
    confidences = _sequence_confidences(generated)
    return list(zip(outputs, confidences))


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
    return {"status": "ok", "model_name": MODEL_NAME, "model_loaded": _model is not None}


@app.get("/languages")
def languages():
    return {"languages": [{"code": c, "name": n} for c, n in SUPPORTED_LANGUAGES.items()]}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    source_lang = _resolve_source_lang(req.source_lang, req.text)
    _validate_languages(source_lang, req.target_lang)
    _load_model()

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
