import json

import pytest

from training.finetune import finetune, parse_direction

MODEL_NAME = "valhalla/m2m100_tiny_random"


def test_parse_direction():
    assert parse_direction("en-ki", "ki") == ("en", "ki")
    assert parse_direction("ki-en", "ki") == ("ki", "en")


def test_parse_direction_rejects_direction_without_new_lang():
    with pytest.raises(ValueError):
        parse_direction("en-sw", "ki")


def test_parse_direction_rejects_malformed_direction():
    with pytest.raises(ValueError):
        parse_direction("en_ki", "ki")


def _write_jsonl(path, pairs):
    with path.open("w", encoding="utf-8") as f:
        for source, target in pairs:
            f.write(json.dumps({"source": source, "target": target}) + "\n")


def test_finetune_end_to_end_on_tiny_checkpoint(tmp_path):
    """Proves the full LoRA fine-tuning cycle actually runs against a real
    M2M100 tokenizer/model (the same tiny random-weight checkpoint the rest
    of ml-service's test suite uses) — not a mock. This does NOT prove
    translation quality (the checkpoint's weights are random, so its output
    is gibberish by construction); it proves the mechanics — vocabulary
    extension, LoRA training, checkpoint save — run correctly end to end on
    a language M2M100 was never pretrained on. See training/README.md for
    what would be needed to prove quality on a real language.
    """
    train_file = tmp_path / "train.jsonl"
    val_file = tmp_path / "val.jsonl"
    # Tiny, repeated on purpose — enough for a couple of real optimizer
    # steps without the test taking minutes.
    _write_jsonl(
        train_file,
        [("hello", "niatia"), ("world", "thi"), ("good morning", "wega ruciini")] * 3,
    )
    _write_jsonl(val_file, [("hello", "niatia")])

    output_dir = tmp_path / "adapter"
    metadata = finetune(
        base_model=MODEL_NAME,
        new_lang="ki",
        init_from="sw",
        direction="en-ki",
        train_file=train_file,
        val_file=val_file,
        output_dir=output_dir,
        epochs=1,
        batch_size=4,
        learning_rate=1e-3,
    )

    assert metadata["train_examples"] == 9
    assert metadata["new_lang"] == "ki"
    assert isinstance(metadata["final_train_loss"], float)

    # Real artifacts a later evaluate.py / serving load would need.
    assert (output_dir / "adapter_config.json").exists()
    assert (output_dir / "adapter_model.safetensors").exists()
    assert (output_dir / "tokenizer_config.json").exists()
    assert (output_dir / "training_metadata.json").exists()

    # The adapter checkpoint should stay small (see vocab_extension.py /
    # finetune.py: save_embedding_layers=False) rather than re-saving the
    # entire embedding matrix on every language's adapter.
    adapter_size = (output_dir / "adapter_model.safetensors").stat().st_size
    assert adapter_size < 5_000_000  # a few KB in practice for this tiny model
