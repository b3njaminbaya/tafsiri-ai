"""Stage 4 of the training pipeline: evaluate a fine-tuned adapter on a held-
out test set. This is the quality gate — see promote_language.py, which
refuses to suggest promoting a language to production translation support
without an evaluation report backing it up.

Usage:
    python -m training.evaluate \\
        --base-model facebook/m2m100_418M \\
        --adapter-dir ./pipeline-data/en-ki/adapter \\
        --new-lang ki --init-from sw \\
        --direction en-ki \\
        --test-file ./pipeline-data/en-ki/prepared/test.jsonl \\
        --out ./pipeline-data/en-ki/eval_report.json
"""
import argparse
import json
from pathlib import Path
from typing import List

import sacrebleu
import torch
from peft import PeftModel
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from .finetune import parse_direction
from .vocab_extension import register_language

MAX_SAMPLE_PREDICTIONS = 10


def _read_jsonl(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_adapter_for_eval(
    base_model: str, adapter_dir: Path, new_lang: str, init_from: str
) -> tuple:
    tokenizer = M2M100Tokenizer.from_pretrained(str(adapter_dir))
    base = M2M100ForConditionalGeneration.from_pretrained(base_model)
    # Re-registering is required on every load — see vocab_extension.py.
    # init_from must be the same language used at training time, since the
    # frozen embedding row is reconstructed fresh here rather than loaded
    # from the adapter checkpoint (see finetune.py's save_embedding_layers=False).
    register_language(tokenizer, base, new_lang, init_from_code=init_from)
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    model.eval()
    return model, tokenizer


def translate_batch(
    model, tokenizer: M2M100Tokenizer, texts: List[str], source_lang: str, target_lang: str
) -> List[str]:
    tokenizer.src_lang = source_lang
    encoded = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            forced_bos_token_id=tokenizer.get_lang_id(target_lang),
            max_new_tokens=256,
        )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)


def evaluate(
    base_model: str,
    adapter_dir: Path,
    new_lang: str,
    init_from: str,
    direction: str,
    test_file: Path,
    batch_size: int = 8,
) -> dict:
    source_lang, target_lang = parse_direction(direction, new_lang)
    records = _read_jsonl(test_file)
    if not records:
        raise ValueError(f"{test_file} has no test examples — evaluation needs a held-out set")

    model, tokenizer = load_adapter_for_eval(base_model, adapter_dir, new_lang, init_from)

    sources = [r["source"] for r in records]
    references = [r["target"] for r in records]
    predictions: List[str] = []
    for i in range(0, len(sources), batch_size):
        batch = sources[i : i + batch_size]
        predictions.extend(translate_batch(model, tokenizer, batch, source_lang, target_lang))

    bleu = sacrebleu.corpus_bleu(predictions, [references])
    chrf = sacrebleu.corpus_chrf(predictions, [references])

    samples = [
        {"source": s, "reference": r, "prediction": p}
        for s, r, p in list(zip(sources, references, predictions))[:MAX_SAMPLE_PREDICTIONS]
    ]

    return {
        "direction": direction,
        "test_examples": len(records),
        "bleu": bleu.score,
        "chrf": chrf.score,
        # Sample predictions exist so a human can sanity-check quality
        # directly — BLEU/chrF on a handful of low-resource test sentences
        # is noisy enough that a number alone isn't trustworthy. This
        # mirrors the project's existing active-learning review queue: a
        # metric flags what needs attention, a person makes the actual call.
        "sample_predictions": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", default="facebook/m2m100_418M")
    parser.add_argument("--adapter-dir", type=Path, required=True)
    parser.add_argument("--new-lang", required=True)
    parser.add_argument("--init-from", required=True)
    parser.add_argument("--direction", required=True)
    parser.add_argument("--test-file", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    report = evaluate(
        args.base_model,
        args.adapter_dir,
        args.new_lang,
        args.init_from,
        args.direction,
        args.test_file,
        args.batch_size,
    )
    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)
    if args.out:
        args.out.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
