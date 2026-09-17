"""Stage 5 (manual, by design): checks an evaluate.py report against a
minimum quality bar and, if it passes, prints exactly what to change in
app/main.py to make the language real — it does not edit app/main.py
itself.

Why this doesn't auto-promote: moving a language from "roadmap" to
"supported" is a claim this app makes to real users that their translation
will work. That's exactly the kind of quality decision this project already
keeps human-reviewed everywhere else (the active-learning review queue
exists because model output needs a person to check it; the correction flow
requires a translator/admin role). A BLEU/chrF number clearing a threshold
on a small low-resource test set is a useful signal, not a substitute for
that judgment — see evaluate.py's sample_predictions for what a human
should actually look at before deciding.

Usage:
    python -m training.promote_language --report ./pipeline-data/en-ki/eval_report.json \\
        --new-lang ki --adapter-dir ./pipeline-data/en-ki/adapter
"""
import argparse
import json
from pathlib import Path

# Deliberately conservative and low-confidence-worthy: these are round
# numbers, not validated against this project's actual translation quality
# bar (there isn't one yet — no Kenyan language has shipped). Treat a report
# that clears this as "worth a human looking at the sample predictions
# closely", not "ready to ship".
MIN_BLEU = 10.0
MIN_CHRF = 25.0


def check_report(report: dict) -> tuple[bool, list[str]]:
    reasons = []
    if report["bleu"] < MIN_BLEU:
        reasons.append(f"BLEU {report['bleu']:.1f} is below the {MIN_BLEU} floor")
    if report["chrf"] < MIN_CHRF:
        reasons.append(f"chrF {report['chrf']:.1f} is below the {MIN_CHRF} floor")
    if report["test_examples"] < 20:
        reasons.append(
            f"only {report['test_examples']} test examples — too few for these scores "
            "to mean much either way, gather more data before trusting this report"
        )
    return len(reasons) == 0, reasons


def print_promotion_instructions(new_lang: str, adapter_dir: Path) -> None:
    print(
        f"""
{new_lang!r} cleared the automated floor. This does NOT mean it's ready —
read evaluate.py's sample_predictions in the report yourself first; BLEU/chrF
on a handful of low-resource sentences is noisy. If the samples genuinely
look right, promoting {new_lang!r} to real translation support means:

1. Copy the adapter checkpoint somewhere ml-service can read it, e.g.:
       cp -r {adapter_dir} ml-service/language_adapters/{new_lang}

2. In ml-service/app/main.py:
   - Move the {new_lang!r} entry from KENYAN_LANGUAGES_ROADMAP to
     SUPPORTED_LANGUAGES (with its real display name).
   - Add {new_lang!r} to KENYAN_LANGUAGE_CODES.
   - Set LANGUAGE_ADAPTERS[{new_lang!r}] = ("<init_from_code>", "language_adapters/{new_lang}")
     (see LANGUAGE_ADAPTERS' docstring for what init_from_code does and why
     it must match what finetune.py used).

3. Restart ml-service and verify live — translate a few real sentences in
   {new_lang!r} yourself, the same "verify it actually works" standard the
   rest of this project holds itself to (see docs/AUDIT.md).

This script intentionally stops here rather than editing app/main.py for
you — see this file's module docstring for why.
"""
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--new-lang", required=True)
    parser.add_argument("--adapter-dir", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.report.read_text())
    passed, reasons = check_report(report)

    if not passed:
        print(f"{args.new_lang!r} does not clear the automated floor yet:")
        for reason in reasons:
            print(f"  - {reason}")
        print("\nThis means more/better data, not a code change — see training/README.md.")
        raise SystemExit(1)

    print_promotion_instructions(args.new_lang, args.adapter_dir)


if __name__ == "__main__":
    main()
