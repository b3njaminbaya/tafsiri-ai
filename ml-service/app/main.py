import logging
import os
import threading
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("ml-service")
logging.basicConfig(level=logging.INFO)

# facebook/m2m100_418M is the real production default: a genuinely multilingual
# (100-language) open translation model whose tokenizer speaks plain ISO codes
# (sw, am, ha, yo, zu, ...) that already match what the rest of this app uses,
# unlike NLLB-200's FLORES-200 codes (swh_Latn, ...) which would need a mapping
# table. Override via MODEL_NAME for local dev with a smaller/tiny checkpoint.
MODEL_NAME = os.getenv("MODEL_NAME", "facebook/m2m100_418M")

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


def _sequence_confidence(generated) -> float:
    """Geometric-mean token probability of the generated sequence, as a proxy
    confidence score — replaces the previous hardcoded 0.42 placeholder with a
    real (if rough) model-derived signal.
    """
    import torch

    if not getattr(generated, "scores", None):
        return 0.5
    transition_scores = _model.compute_transition_scores(
        generated.sequences, generated.scores, normalize_logits=True
    )
    valid = transition_scores[transition_scores > -1e8]
    if valid.numel() == 0:
        return 0.5
    avg_log_prob = valid.mean()
    return float(torch.clamp(torch.exp(avg_log_prob), 0.0, 1.0).item())


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: Optional[str] = None
    target_lang: str
    domain: Optional[str] = None


class TranslateResponse(BaseModel):
    translation: str
    source_lang: str
    target_lang: str
    confidence: float


@app.get("/health")
def health():
    return {"status": "ok", "model_name": MODEL_NAME, "model_loaded": _model is not None}


@app.get("/languages")
def languages():
    return {"languages": [{"code": c, "name": n} for c, n in SUPPORTED_LANGUAGES.items()]}


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    source_lang = req.source_lang if req.source_lang and req.source_lang != "auto" else None
    source_lang = source_lang or _detect_language(req.text)

    if source_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported source language: {source_lang}")
    if req.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {req.target_lang}")

    _load_model()
    _tokenizer.src_lang = source_lang
    encoded = _tokenizer(req.text, return_tensors="pt")

    import torch

    with torch.no_grad():
        generated = _model.generate(
            **encoded,
            forced_bos_token_id=_tokenizer.get_lang_id(req.target_lang),
            max_new_tokens=512,
            output_scores=True,
            return_dict_in_generate=True,
        )

    output_text = _tokenizer.batch_decode(generated.sequences, skip_special_tokens=True)[0]
    confidence = _sequence_confidence(generated)

    return TranslateResponse(
        translation=output_text,
        source_lang=source_lang,
        target_lang=req.target_lang,
        confidence=confidence,
    )
