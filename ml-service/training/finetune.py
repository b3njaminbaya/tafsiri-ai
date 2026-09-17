"""Stage 3 of the training pipeline: LoRA fine-tune M2M100 to add a Kenyan
language, using the train/val JSONL prepare_data.py produced.

What this does and doesn't do, stated plainly:
- Trains a small LoRA adapter (attention + FFN projections) on top of a
  FROZEN base model — the existing sw/so/en (and any other language's)
  behavior is untouched, both because the base weights don't move and
  because the adapter only activates for requests involving the new
  language (see ml-service/app/main.py's adapter routing).
- The new language's embedding is a frozen copy of a related language's
  embedding (see vocab_extension.py) — not trained. What the LoRA adapter
  actually learns is how to process/attend to sequences carrying that
  language tag.
- Realistic expectations: with genuinely low-resource data (hundreds to a
  few thousand sentence pairs, the likely starting point for any of these
  languages), this will not produce translation quality comparable to
  sw/so. It produces something real and measurable (see evaluate.py) — not
  nothing, but not production-grade on a small first dataset either. This
  gets better as more data comes in through the Datasets page.

Usage:
    python -m training.finetune \\
        --base-model facebook/m2m100_418M \\
        --new-lang ki --init-from sw \\
        --direction en-ki \\
        --train-file ./pipeline-data/en-ki/prepared/train.jsonl \\
        --val-file ./pipeline-data/en-ki/prepared/val.jsonl \\
        --output-dir ./pipeline-data/en-ki/adapter \\
        --epochs 10
"""
import argparse
import json
from pathlib import Path
from typing import List, Tuple

import torch
from peft import LoraConfig, get_peft_model
from transformers import (
    DataCollatorForSeq2Seq,
    M2M100ForConditionalGeneration,
    M2M100Tokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from .vocab_extension import register_language, reset_active_languages

DEFAULT_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "out_proj"]


def _read_jsonl(path: Path) -> List[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def parse_direction(direction: str, new_lang: str) -> Tuple[str, str]:
    """'en-ki' -> ('en', 'ki'). Exactly one side must be the new language —
    this pipeline is deliberately scoped to new-language<->existing-language
    pairs; new<->new (e.g. ki<->luo, neither pretrained) is a real but much
    harder problem this doesn't attempt.
    """
    parts = direction.split("-")
    if len(parts) != 2:
        raise ValueError(f"--direction must look like 'en-ki', got {direction!r}")
    source_lang, target_lang = parts
    if new_lang not in (source_lang, target_lang):
        raise ValueError(f"--direction {direction!r} doesn't include --new-lang {new_lang!r}")
    return source_lang, target_lang


def build_model_and_tokenizer(
    base_model: str, new_lang: str, init_from: str
) -> Tuple[M2M100ForConditionalGeneration, M2M100Tokenizer]:
    tokenizer = M2M100Tokenizer.from_pretrained(base_model)
    model = M2M100ForConditionalGeneration.from_pretrained(base_model)
    register_language(tokenizer, model, new_lang, init_from_code=init_from)

    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=DEFAULT_TARGET_MODULES,
        task_type="SEQ_2_SEQ_LM",
    )
    peft_model = get_peft_model(model, lora_config)
    return peft_model, tokenizer


def build_dataset(records: List[dict], tokenizer: M2M100Tokenizer, source_lang: str, target_lang: str):
    from datasets import Dataset

    tokenizer.src_lang = source_lang
    tokenizer.tgt_lang = target_lang

    def _tokenize(batch):
        return tokenizer(
            batch["source"], text_target=batch["target"], truncation=True, max_length=256
        )

    ds = Dataset.from_list(records)
    return ds.map(_tokenize, batched=True, remove_columns=ds.column_names)


def finetune(
    base_model: str,
    new_lang: str,
    init_from: str,
    direction: str,
    train_file: Path,
    val_file: Path,
    output_dir: Path,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    use_cpu: bool = True,
) -> dict:
    source_lang, target_lang = parse_direction(direction, new_lang)
    train_records = _read_jsonl(train_file)
    val_records = _read_jsonl(val_file) if val_file and val_file.exists() else []
    if not train_records:
        raise ValueError(f"{train_file} has no training examples")

    model, tokenizer = build_model_and_tokenizer(base_model, new_lang, init_from)
    train_ds = build_dataset(train_records, tokenizer, source_lang, target_lang)
    val_ds = build_dataset(val_records, tokenizer, source_lang, target_lang) if val_records else None

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        eval_strategy="epoch" if val_ds is not None else "no",
        save_strategy="no",
        logging_steps=max(1, len(train_ds) // batch_size // 4 or 1),
        report_to=[],
        # CPU by default, deliberately: Trainer will happily pick up MPS
        # (Apple Silicon/Metal) automatically, but MPS's operator coverage
        # for this model hits real gaps (verified: a plain embedding lookup
        # raises "Placeholder storage has not been allocated on MPS device"
        # partway through a forward pass on this exact model). CUDA (a real
        # GPU) is reliable and should be used for anything beyond small-
        # scale experimentation — pass use_cpu=False there. See
        # training/README.md.
        use_cpu=use_cpu,
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
    )
    train_result = trainer.train()

    output_dir.mkdir(parents=True, exist_ok=True)
    reset_active_languages(tokenizer)  # see vocab_extension.py — must happen before saving
    model.save_pretrained(str(output_dir), save_embedding_layers=False)
    tokenizer.save_pretrained(str(output_dir))

    metadata = {
        "base_model": base_model,
        "new_lang": new_lang,
        "init_from": init_from,
        "direction": direction,
        "train_examples": len(train_records),
        "val_examples": len(val_records),
        "epochs": epochs,
        "final_train_loss": train_result.training_loss,
    }
    (output_dir / "training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", default="facebook/m2m100_418M")
    parser.add_argument("--new-lang", required=True, help="Language code being added, e.g. ki")
    parser.add_argument(
        "--init-from",
        required=True,
        help="Existing M2M100 language to copy the new language's starting embedding from "
        "(closest available relative — e.g. sw for another Bantu language)",
    )
    parser.add_argument("--direction", required=True, help="e.g. en-ki or ki-en")
    parser.add_argument("--train-file", type=Path, required=True)
    parser.add_argument("--val-file", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use CUDA instead of CPU. Do not pass this for MPS (Apple Silicon) — see finetune.py.",
    )
    args = parser.parse_args()

    metadata = finetune(
        args.base_model,
        args.new_lang,
        args.init_from,
        args.direction,
        args.train_file,
        args.val_file,
        args.output_dir,
        args.epochs,
        args.batch_size,
        args.learning_rate,
        use_cpu=not args.gpu,
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
