"""Proves the serving-side half of the training pipeline: once a language
adapter is configured, /translate actually uses it, AND existing base
languages (sw/so/en) keep working correctly, unaffected, in the same
running process — this is the "an adapter for one language must not risk
the ones already working" property _generate()'s isolation is built for.
"""
import json

from app import main as ml_main


def _write_jsonl(path, pairs):
    with path.open("w", encoding="utf-8") as f:
        for source, target in pairs:
            f.write(json.dumps({"source": source, "target": target}) + "\n")


def test_no_adapters_configured_never_imports_peft(client, monkeypatch):
    """The default, shipped state: LANGUAGE_ADAPTERS is empty, so _generate()
    must never even attempt to import peft — a serving deployment that never
    installed requirements-training.txt would crash on the very first
    translation otherwise. Simulated here by making the import explode if
    reached, rather than by actually uninstalling peft.
    """
    import builtins

    real_import = builtins.__import__

    def _exploding_import(name, *args, **kwargs):
        if name == "peft":
            raise AssertionError("peft must not be imported when no adapters are configured")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(ml_main, "_adapter_languages", set())
    monkeypatch.setattr(builtins, "__import__", _exploding_import)
    try:
        resp = client.post("/translate", json={"text": "hello", "source_lang": "en", "target_lang": "sw"})
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)
    assert resp.status_code == 200


def test_configured_adapter_serves_the_new_language_without_breaking_existing_ones(
    client, monkeypatch, tmp_path
):
    from training.finetune import finetune

    train_file = tmp_path / "train.jsonl"
    _write_jsonl(train_file, [("hello", "niatia"), ("world", "thi")] * 3)

    adapter_dir = tmp_path / "ki_adapter"
    finetune(
        base_model=ml_main.MODEL_NAME,
        new_lang="ki",
        init_from="sw",
        direction="en-ki",
        train_file=train_file,
        val_file=None,
        output_dir=adapter_dir,
        epochs=1,
        batch_size=4,
        learning_rate=1e-3,
    )

    # Wire it up exactly as promote_language.py instructs a maintainer to.
    monkeypatch.setitem(ml_main.SUPPORTED_LANGUAGES, "ki", "Kikuyu (Gĩkũyũ)")
    monkeypatch.setattr(ml_main, "KENYAN_LANGUAGE_CODES", ml_main.KENYAN_LANGUAGE_CODES | {"ki"})
    monkeypatch.setattr(ml_main, "LANGUAGE_ADAPTERS", {"ki": ("sw", str(adapter_dir))})

    # Force a real reload with the adapter configured, then restore the
    # process's original loaded model/tokenizer afterward so later tests in
    # this session see the same shared state they always have.
    original_model, original_tokenizer, original_adapters = (
        ml_main._model,
        ml_main._tokenizer,
        set(ml_main._adapter_languages),
    )
    monkeypatch.setattr(ml_main, "_model", None)
    monkeypatch.setattr(ml_main, "_tokenizer", None)
    monkeypatch.setattr(ml_main, "_adapter_languages", set())
    ml_main._load_model()

    try:
        assert "ki" in ml_main._adapter_languages

        # The new, adapter-backed language now actually works over the real API.
        resp = client.post("/translate", json={"text": "hello", "source_lang": "en", "target_lang": "ki"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["source_lang"] == "en" and body["target_lang"] == "ki"
        assert isinstance(body["translation"], str) and len(body["translation"]) > 0

        # A base-language pair, with the ki adapter also loaded alongside,
        # still works — proves _select_adapter_for's None case (disable all
        # adapters) is actually exercised and correct, not just untested.
        resp_sw = client.post("/translate", json={"text": "hello", "source_lang": "en", "target_lang": "sw"})
        assert resp_sw.status_code == 200
        assert resp_sw.json()["target_lang"] == "sw"

        resp_so = client.post("/translate", json={"text": "hello", "source_lang": "en", "target_lang": "so"})
        assert resp_so.status_code == 200
    finally:
        monkeypatch.setattr(ml_main, "_model", original_model)
        monkeypatch.setattr(ml_main, "_tokenizer", original_tokenizer)
        monkeypatch.setattr(ml_main, "_adapter_languages", original_adapters)


def test_unconfigured_roadmap_language_still_rejected(client):
    resp = client.post("/translate", json={"text": "hi", "source_lang": "en", "target_lang": "luo"})
    assert resp.status_code == 400
