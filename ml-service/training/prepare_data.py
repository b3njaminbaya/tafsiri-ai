"""Stage 2 of the training pipeline: turn raw dataset files (as downloaded by
export_dataset.py, or dropped in manually) into cleaned, deduplicated,
train/val/test-split JSONL ready for finetune.py.

Usage:
    python -m training.prepare_data \\
        --raw-dir ./pipeline-data/en-ki/raw \\
        --out-dir ./pipeline-data/en-ki/prepared \\
        --source-lang en --target-lang ki
"""
import argparse
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import List

from .formats import SentencePair, UnsupportedFormatError, parse_parallel_file

MAX_CHARS = 1000
MIN_CHARS = 1


def clean_and_dedupe(pairs: List[SentencePair]) -> List[SentencePair]:
    """Real, if simple, cleaning: strip whitespace, drop empty or
    implausibly long lines (a >1000-char "sentence" is almost always a
    parsing artifact, not real training signal), and drop exact-duplicate
    pairs — repeated pairs from overlapping contributions would otherwise
    let the model overfit to a handful of sentences that happen to appear
    many times.
    """
    seen = set()
    cleaned = []
    for pair in pairs:
        source = pair.source.strip()
        target = pair.target.strip()
        if not (MIN_CHARS <= len(source) <= MAX_CHARS):
            continue
        if not (MIN_CHARS <= len(target) <= MAX_CHARS):
            continue
        key = (source, target)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(SentencePair(source=source, target=target))
    return cleaned


def split(
    pairs: List[SentencePair], val_fraction: float, test_fraction: float, seed: int
) -> tuple[List[SentencePair], List[SentencePair], List[SentencePair]]:
    """Deterministic shuffle-then-split. With very small low-resource
    datasets (the norm here, not the exception), val/test each get at least
    one example rather than rounding down to zero and silently training
    with no evaluation signal at all.
    """
    shuffled = list(pairs)
    random.Random(seed).shuffle(shuffled)

    n = len(shuffled)
    n_val = max(1, round(n * val_fraction)) if n >= 3 else 0
    n_test = max(1, round(n * test_fraction)) if n >= 3 else 0
    # Never let val+test consume the entire (tiny) dataset — train needs at
    # least one example too, or there's nothing to actually fine-tune on.
    while n_val + n_test >= n and (n_val > 0 or n_test > 0):
        if n_val >= n_test:
            n_val -= 1
        else:
            n_test -= 1

    val = shuffled[:n_val]
    test = shuffled[n_val : n_val + n_test]
    train = shuffled[n_val + n_test :]
    return train, val, test


def _write_jsonl(pairs: List[SentencePair], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(asdict(pair), ensure_ascii=False) + "\n")


def prepare(
    raw_dir: Path,
    out_dir: Path,
    source_lang: str,
    target_lang: str,
    val_fraction: float = 0.1,
    test_fraction: float = 0.1,
    seed: int = 13,
) -> dict:
    all_pairs: List[SentencePair] = []
    skipped_files = []
    for file_path in sorted(raw_dir.iterdir()):
        if not file_path.is_file():
            continue
        try:
            content = file_path.read_bytes()
            pairs = parse_parallel_file(content, file_path.name, source_lang, target_lang)
            all_pairs.extend(pairs)
        except (UnsupportedFormatError, ValueError, UnicodeDecodeError) as exc:
            # A single malformed/unsupported contribution shouldn't abort
            # the whole pipeline run — record it and keep going; the
            # summary below makes it visible rather than silently dropped.
            skipped_files.append({"file": file_path.name, "reason": str(exc)})

    cleaned = clean_and_dedupe(all_pairs)
    train, val, test = split(cleaned, val_fraction, test_fraction, seed)

    out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(train, out_dir / "train.jsonl")
    _write_jsonl(val, out_dir / "val.jsonl")
    _write_jsonl(test, out_dir / "test.jsonl")

    summary = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "raw_pairs_parsed": len(all_pairs),
        "after_cleaning": len(cleaned),
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "skipped_files": skipped_files,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--source-lang", required=True)
    parser.add_argument("--target-lang", required=True)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--test-fraction", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    summary = prepare(
        args.raw_dir,
        args.out_dir,
        args.source_lang,
        args.target_lang,
        args.val_fraction,
        args.test_fraction,
        args.seed,
    )
    print(json.dumps(summary, indent=2))
    if summary["train"] == 0:
        raise SystemExit(
            "No usable training pairs after cleaning — check --raw-dir has real "
            f"parallel files for {args.source_lang}->{args.target_lang}."
        )


if __name__ == "__main__":
    main()
