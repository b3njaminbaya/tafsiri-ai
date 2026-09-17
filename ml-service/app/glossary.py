import re
from typing import Dict, List, Optional, Tuple

# A small, deliberately illustrative domain glossary: real per-domain fine-tuned
# adapters (LoRA or otherwise) need labeled training data and a training loop
# this project doesn't have yet. Terminology-constrained decoding is the honest
# version of "domain customization" achievable without one — it forces the
# model's beam search to include the correct domain term in its output rather
# than leaving translation quality to chance for terms that matter (a
# medical/legal document translated with the wrong term for "prescription" or
# "plaintiff" is a real, meaningful failure mode this addresses).
#
# Only (en, sw) entries below: this product is Kenya-only (see
# app/main.py:SUPPORTED_LANGUAGES), so es/fr entries that existed here before
# that scope change are unreachable — _validate_languages rejects es/fr
# before a request ever reaches glossary lookup.
GLOSSARY: Dict[str, Dict[Tuple[str, str], Dict[str, str]]] = {
    "medical": {
        ("en", "sw"): {
            "prescription": "dawa iliyoagizwa",
            "diagnosis": "utambuzi",
            "dosage": "kipimo",
        },
    },
    "legal": {
        ("en", "sw"): {
            "plaintiff": "mlalamikaji",
            "defendant": "mshtakiwa",
            "affidavit": "kiapo",
        },
    },
    "technical": {
        ("en", "sw"): {
            "firmware": "programu tegemezi",
            "bandwidth": "upana wa mawimbi",
            "encryption": "usimbaji",
        },
    },
}


def find_glossary_terms(
    domain: Optional[str], source_lang: str, target_lang: str, text: str
) -> List[str]:
    """Target-language terms to force into the output, based on which
    glossary source terms appear (as whole words) in the input text.
    """
    if not domain:
        return []
    entries = GLOSSARY.get(domain, {}).get((source_lang, target_lang), {})
    if not entries:
        return []
    lowered = text.lower()
    return [
        target_term
        for source_term, target_term in entries.items()
        if re.search(rf"\b{re.escape(source_term.lower())}\b", lowered)
    ]
