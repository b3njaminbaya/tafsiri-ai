import json

from training.formats import SentencePair
from training.prepare_data import clean_and_dedupe, prepare, split


def test_clean_and_dedupe_strips_and_drops_empty():
    pairs = [
        SentencePair("  hello  ", "  niatia  "),
        SentencePair("", "empty source"),
        SentencePair("empty target", ""),
    ]
    cleaned = clean_and_dedupe(pairs)
    assert cleaned == [SentencePair("hello", "niatia")]


def test_clean_and_dedupe_drops_duplicates():
    pairs = [SentencePair("hello", "niatia"), SentencePair("hello", "niatia")]
    assert clean_and_dedupe(pairs) == [SentencePair("hello", "niatia")]


def test_clean_and_dedupe_drops_implausibly_long_lines():
    pairs = [SentencePair("x" * 2000, "niatia")]
    assert clean_and_dedupe(pairs) == []


def test_split_is_deterministic_for_a_given_seed():
    pairs = [SentencePair(f"s{i}", f"t{i}") for i in range(20)]
    train1, val1, test1 = split(pairs, 0.1, 0.1, seed=42)
    train2, val2, test2 = split(pairs, 0.1, 0.1, seed=42)
    assert train1 == train2 and val1 == val2 and test1 == test2
    # Every pair ends up in exactly one split.
    all_out = set(train1) | set(val1) | set(test1)
    assert all_out == set(pairs)
    assert len(train1) + len(val1) + len(test1) == 20


def test_split_gives_tiny_datasets_at_least_one_val_and_test_example():
    pairs = [SentencePair(f"s{i}", f"t{i}") for i in range(5)]
    train, val, test = split(pairs, 0.1, 0.1, seed=1)
    assert len(val) >= 1
    assert len(test) >= 1
    assert len(train) >= 1


def test_split_single_pair_goes_entirely_to_train():
    pairs = [SentencePair("s", "t")]
    train, val, test = split(pairs, 0.1, 0.1, seed=1)
    assert train == pairs
    assert val == [] and test == []


def test_prepare_end_to_end(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "corpus1.tsv").write_bytes(
        "\n".join(f"hello {i}\tniatia {i}" for i in range(20)).encode("utf-8")
    )
    (raw_dir / "corpus2.json").write_bytes(
        json.dumps([{"source": "world", "target": "thi"}]).encode("utf-8")
    )
    (raw_dir / "not_a_dataset.pdf").write_bytes(b"%PDF-1.4 not really a dataset")

    out_dir = tmp_path / "prepared"
    summary = prepare(raw_dir, out_dir, "en", "ki")

    assert summary["raw_pairs_parsed"] == 21
    assert summary["train"] + summary["val"] + summary["test"] == 21
    assert summary["skipped_files"] == [
        {"file": "not_a_dataset.pdf", "reason": "No parser for .pdf files"}
    ]
    assert (out_dir / "train.jsonl").exists()
    assert (out_dir / "val.jsonl").exists()
    assert (out_dir / "test.jsonl").exists()

    train_lines = (out_dir / "train.jsonl").read_text().splitlines()
    first = json.loads(train_lines[0])
    assert "source" in first and "target" in first
