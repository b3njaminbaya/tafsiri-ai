"""Adds a new language to an M2M100 tokenizer/model pair that was never
pretrained on it — the actual blocker behind ml-service's KENYAN_LANGUAGES_ROADMAP
(see app/main.py). M2M100's 100 languages are baked into the tokenizer as a
fixed list (FAIRSEQ_LANGUAGE_CODES); a language outside that list has no
`__xx__` token and no embedding row at all, and the tokenizer doesn't expose
a public API for adding one — this reaches into the same internal
bookkeeping M2M100Tokenizer itself uses.

Design choice, stated plainly: the new language's embedding is a frozen copy
of a linguistically related existing language's embedding (e.g. Swahili's
for another Bantu language), not a trained parameter. With the small amount
of data a genuinely low-resource language realistically has, training a
1024-dim embedding vector from scratch is unlikely to converge to anything
meaningful anyway — freezing it and letting the LoRA adapter (applied to the
attention/FFN projections, see finetune.py) do the actual adapting is more
sample-efficient and keeps the mechanics simple enough to verify. This is a
real simplification, not a hidden one; revisit it if a language accumulates
enough data that a trained embedding becomes worth the added complexity.

IMPORTANT — this must be called every time the tokenizer is loaded from
disk, not just once at training time: M2M100Tokenizer.__init__ rebuilds
lang_code_to_token/lang_code_to_id/lang_token_to_id/id_to_lang_token from
the fixed FAIRSEQ_LANGUAGE_CODES list on every construction. The special
token itself (e.g. "__ki__") does persist correctly through
save_pretrained()/from_pretrained() — it's a normal added special token —
but the "this code is a registered language" bookkeeping does not. Verified
empirically; see training/README.md.
"""
from typing import Optional

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer


def register_language(
    tokenizer: M2M100Tokenizer,
    model: Optional[M2M100ForConditionalGeneration],
    new_code: str,
    init_from_code: Optional[str] = None,
) -> int:
    """Idempotent. Registers `new_code` as a valid language on `tokenizer`
    (growing `model`'s embeddings to match, if a new token was actually
    added) and returns its token id. Safe to call on every load — if
    `new_code` is already registered, this is a no-op that just returns the
    existing id.

    `init_from_code` (required the first time a given token is truly new)
    is the existing M2M100 language whose embedding is copied as the new
    language's frozen starting point — pick the closest available relative
    (e.g. "sw" for another Bantu language; there's no perfect choice for
    Nilotic/Cushitic languages M2M100 has no close relative for, so "en" is
    a defensible fallback anchor, not a linguistic claim).
    """
    if new_code in tokenizer.lang_code_to_token:
        return tokenizer.get_lang_id(new_code)

    new_token = f"__{new_code}__"
    unk_id = tokenizer.convert_tokens_to_ids(tokenizer.unk_token)
    existing_id = tokenizer.convert_tokens_to_ids(new_token)
    newly_added = existing_id == unk_id

    if newly_added:
        # Truly new token: not in the vocab under any name yet.
        if init_from_code is None:
            raise ValueError(
                f"{new_code!r} has no existing token in this tokenizer and "
                "init_from_code was not given — required the first time a "
                "language is registered."
            )
        tokenizer.add_special_tokens(
            {"additional_special_tokens": tokenizer.additional_special_tokens + [new_token]}
        )
        token_id = tokenizer.convert_tokens_to_ids(new_token)
    else:
        # The token string already exists in the vocab (e.g. re-registering
        # after a reload, where save_pretrained/from_pretrained already
        # preserved the added special token itself) — reuse its id rather
        # than adding a duplicate. The embedding row was already copied the
        # first time this ran, so there's nothing more to initialize here.
        token_id = existing_id

    tokenizer.lang_code_to_token[new_code] = new_token
    tokenizer.lang_token_to_id[new_token] = token_id
    tokenizer.lang_code_to_id[new_code] = token_id
    tokenizer.id_to_lang_token[token_id] = new_token

    if model is not None and newly_added:
        # Always resize (not gated on current row count): M2M100's base
        # checkpoint ships with a few unused "made-up word" embedding rows
        # beyond what the tokenizer currently reports via len() (verified
        # empirically — see training/README.md), so a naive
        # `token_id >= current_rows` check can be false even for a token
        # that was just added, which would skip the embedding-copy step
        # below and leave that row at its original, meaningless random
        # init. resize_token_embeddings(len(tokenizer)) is safe to call
        # unconditionally: it grows the matrix if needed, or trims unused
        # padding rows if there was already enough headroom — either way
        # the new token's row ends up at a defined index we then write into.
        model.resize_token_embeddings(len(tokenizer))
        if init_from_code:
            with torch.no_grad():
                init_id = tokenizer.get_lang_id(init_from_code)
                model.model.shared.weight[token_id] = model.model.shared.weight[init_id].clone()
        # Frozen by design (see module docstring) — every row, not just the
        # new one, since this whole matrix is tied to the output/lm_head
        # weights too and isn't LoRA's target in finetune.py.
        model.model.shared.weight.requires_grad_(False)

    return token_id


def reset_active_languages(tokenizer: M2M100Tokenizer, safe_lang: str = "en") -> None:
    """Point src_lang/tgt_lang at a language guaranteed to exist in every
    M2M100 tokenizer before save_pretrained(). M2M100Tokenizer.__init__
    resolves src_lang to a token id immediately on construction — saving
    with it still pointed at a newly-registered custom language would
    produce a checkpoint that raises KeyError on the very next load, before
    any caller gets the chance to call register_language() again. Verified
    empirically; see training/README.md.
    """
    tokenizer.src_lang = safe_lang
    tokenizer.tgt_lang = safe_lang
