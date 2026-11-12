"""Step 4: score a model's extraction against the test set.

Usage: python src/score.py claude-haiku-5-5

Compares data/raw/whoishiring_50338728_<model>.jsonl with tests/expected.json
and prints the accuracy of each field and the precision and recall of the matches.
"""

import json
import sys
from pathlib import Path

from find_matches import is_match

THREAD_ID = 50338728


def has_fde_or_ai(fields: dict) -> bool:
    return any(role["is_fde_or_ai"] for role in fields["roles"])


# Each check compares one thing; role titles are free text, so they aren't compared.
CHECKS = {
    "company": lambda f: f["company"].strip().lower(),
    "remote": lambda f: f["remote"],
    "uruguay_allowed": lambda f: f["uruguay_allowed"],
    "has FDE or AI role": has_fde_or_ai,
}


def main() -> None:
    model = sys.argv[1]
    tests = json.loads(Path("tests/expected.json").read_text())
    lines = Path(f"data/raw/whoishiring_{THREAD_ID}_{model}.jsonl").read_text().splitlines()
    got = {row["post_id"]: row for row in map(json.loads, filter(None, lines))}

    missing = [t["post_id"] for t in tests if t["post_id"] not in got]
    if missing:
        print(f"Not extracted by {model}, skipped: {missing}")
    tests = [t for t in tests if t["post_id"] in got]
    print(f"Model: {model}. {len(tests)} test posts\n")

    print("Field accuracy:")
    for name, value in CHECKS.items():
        wrong = [t for t in tests if value(got[t["post_id"]]) != value(t["expected"])]
        print(f"  {name}: {len(tests) - len(wrong)}/{len(tests)}")
        for t in wrong:
            print(f"    wrong: {t['expected']['company']} "
                  f"(expected {value(t['expected'])!r}, got {value(got[t['post_id']])!r})")

    tp = fp = fn = 0
    for t in tests:
        expected, predicted = is_match(t["expected"]), is_match(got[t["post_id"]])
        tp += expected and predicted
        fp += predicted and not expected
        fn += expected and not predicted
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    print(f"\nMatches: {tp} right, {fp} false positives, {fn} missed")
    print(f"  precision {precision:.0%} · recall {recall:.0%}")


if __name__ == "__main__":
    main()
