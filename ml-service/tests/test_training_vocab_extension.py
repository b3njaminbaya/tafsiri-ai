import pytest
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from training.vocab_extension import register_language, reset_active_languages

MODEL_NAME = "valhalla/m2m100_tiny_random"


@pytest.fixture(scope="module")
def base_tokenizer_and_model():
    tok = M2M100Tokenizer.from_pretrained(MODEL_NAME)
    model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME)
    return tok, model


def test_register_new_language_grows_vocab_and_embeddings(base_tokenizer_and_model):
    tok, model = base_tokenizer_and_model
    len_before = len(tok)
    rows_before = model.get_input_embeddings().weight.shape[0]

    new_id = register_language(tok, model, "ki", init_from_code="sw")

    assert len(tok) == len_before + 1
    assert tok.get_lang_id("ki") == new_id
    assert model.get_input_embeddings().weight.shape[0] >= new_id + 1


def test_new_language_embedding_copies_init_from_language(base_tokenizer_and_model):
    tok, model = base_tokenizer_and_model
    register_language(tok, model, "luo", init_from_code="sw")
    sw_row = model.model.shared.weight[tok.get_lang_id("sw")]
    luo_row = model.model.shared.weight[tok.get_lang_id("luo")]
    assert torch.equal(sw_row, luo_row)


def test_shared_embedding_is_frozen_after_registration(base_tokenizer_and_model):
    tok, model = base_tokenizer_and_model
    register_language(tok, model, "kam", init_from_code="sw")
    assert model.model.shared.weight.requires_grad is False


def test_register_language_is_idempotent(base_tokenizer_and_model):
    tok, model = base_tokenizer_and_model
    first_id = register_language(tok, model, "guz", init_from_code="sw")
    len_after_first = len(tok)
    second_id = register_language(tok, model, "guz", init_from_code="sw")
    assert first_id == second_id
    assert len(tok) == len_after_first  # no duplicate token added


def test_register_language_without_init_code_raises_for_truly_new_token():
    tok = M2M100Tokenizer.from_pretrained(MODEL_NAME)
    with pytest.raises(ValueError):
        register_language(tok, None, "mas", init_from_code=None)


def test_reset_active_languages_sets_safe_default():
    tok = M2M100Tokenizer.from_pretrained(MODEL_NAME)
    register_language(tok, None, "teo", init_from_code="sw")
    tok.src_lang = "teo"
    tok.tgt_lang = "teo"
    reset_active_languages(tok, safe_lang="en")
    assert tok.src_lang == "en"
    assert tok.tgt_lang == "en"


def test_full_save_and_reload_cycle_survives_without_crashing(tmp_path):
    """The specific failure mode this guards against: saving a tokenizer
    while src_lang/tgt_lang still point at the newly-registered language
    makes the checkpoint permanently unloadable, because M2M100Tokenizer
    resolves src_lang to an id at __init__ time, before any caller can
    re-register the language. See vocab_extension.py's module docstring.
    """
    tok = M2M100Tokenizer.from_pretrained(MODEL_NAME)
    model = M2M100ForConditionalGeneration.from_pretrained(MODEL_NAME)
    register_language(tok, model, "ebu", init_from_code="sw")
    tok.src_lang = "ebu"
    tok.tgt_lang = "en"

    reset_active_languages(tok, safe_lang="en")
    tok.save_pretrained(tmp_path)

    # Must not raise.
    reloaded = M2M100Tokenizer.from_pretrained(tmp_path)
    # The special token itself persisted...
    assert reloaded.convert_tokens_to_ids("__ebu__") != reloaded.convert_tokens_to_ids(
        reloaded.unk_token
    )
    # ...but the language bookkeeping did not, exactly as documented.
    assert "ebu" not in reloaded.lang_code_to_token
    # Re-registering (as evaluate.py / serving must do on every load) fixes it.
    register_language(reloaded, None, "ebu", init_from_code="sw")
    assert "ebu" in reloaded.lang_code_to_token
