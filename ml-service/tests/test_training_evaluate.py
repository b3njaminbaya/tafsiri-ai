import json

from training.evaluate import evaluate
from training.finetune import finetune

MODEL_NAME = "valhalla/m2m100_tiny_random"


def _write_jsonl(path, pairs):
    with path.open("w", encoding="utf-8") as f:
        for source, target in pairs:
            f.write(json.dumps({"source": source, "target": target}) + "\n")


def test_evaluate_end_to_end_after_real_finetune(tmp_path):
    """Chains finetune.py -> evaluate.py exactly as a real pipeline run
    would: train an adapter, then load it back fresh (a separate model/
    tokenizer instantiation, the same as evaluate.py or ml-service's serving
    process would do) and score it. Proves the whole save -> reload ->
    generate -> score cycle works, not just training in isolation.
    """
    train_file = tmp_path / "train.jsonl"
    val_file = tmp_path / "val.jsonl"
    test_file = tmp_path / "test.jsonl"
    _write_jsonl(train_file, [("hello", "niatia"), ("world", "thi")] * 3)
    _write_jsonl(val_file, [("hello", "niatia")])
    _write_jsonl(test_file, [("hello", "niatia"), ("world", "thi")])

    adapter_dir = tmp_path / "adapter"
    finetune(
        base_model=MODEL_NAME,
        new_lang="ki",
        init_from="sw",
        direction="en-ki",
        train_file=train_file,
        val_file=val_file,
        output_dir=adapter_dir,
        epochs=1,
        batch_size=4,
        learning_rate=1e-3,
    )

    report = evaluate(
        base_model=MODEL_NAME,
        adapter_dir=adapter_dir,
        new_lang="ki",
        init_from="sw",
        direction="en-ki",
        test_file=test_file,
        batch_size=4,
    )

    assert report["test_examples"] == 2
    assert isinstance(report["bleu"], float)
    assert isinstance(report["chrf"], float)
    # A real score, not a placeholder — 0 is a legitimate BLEU score for a
    # random-weight checkpoint's gibberish output, which is exactly what's
    # expected here (this proves the scoring pipeline runs, not that this
    # particular checkpoint translates well — it can't, its weights are
    # random).
    assert 0.0 <= report["bleu"] <= 100.0
    assert 0.0 <= report["chrf"] <= 100.0
    assert len(report["sample_predictions"]) == 2
    for sample in report["sample_predictions"]:
        assert set(sample.keys()) == {"source", "reference", "prediction"}
        assert isinstance(sample["prediction"], str)


def test_evaluate_rejects_empty_test_file(tmp_path):
    (tmp_path / "empty.jsonl").write_text("", encoding="utf-8")
    import pytest

    with pytest.raises(ValueError):
        evaluate(
            base_model=MODEL_NAME,
            adapter_dir=tmp_path,
            new_lang="ki",
            init_from="sw",
            direction="en-ki",
            test_file=tmp_path / "empty.jsonl",
        )
