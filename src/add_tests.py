"""Add posts to the test set, prefilled with a model's answers, to check by hand.

Usage: python src/add_tests.py claude-haiku-5-5 50347217 50342430 ...

Each new post gets "checked": false. Read the post, fix "expected" where the
model was wrong, write why in "notes", then set "checked" to true.
Posts already in the test set are skipped.
"""

import html
import json
import re
import sys
from pathlib import Path

THREAD_ID = 50338728
TESTS = Path("tests/expected.json")


def paragraphs(post_html: str) -> list[str]:
    parts = re.split(r"<p>", post_html)
    return [html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in parts if p.strip()]


def main() -> None:
    model, ids = sys.argv[1], [int(i) for i in sys.argv[2:]]
    tests = json.loads(TESTS.read_text())
    thread = json.loads(Path(f"data/raw/whoishiring_{THREAD_ID}.json").read_text())
    posts = {c["id"]: c for c in thread["children"] if c.get("text")}
    lines = Path(f"data/raw/whoishiring_{THREAD_ID}_{model}.jsonl").read_text().splitlines()
    got = {row["post_id"]: row for row in map(json.loads, filter(None, lines))}

    known = {t["post_id"] for t in tests}
    for post_id in ids:
        if post_id in known or post_id not in posts or post_id not in got:
            print(f"skipped {post_id}: already in the test set, or not in the thread or the extraction")
            continue
        fields = got[post_id]
        tests.append({
            "post_id": post_id,
            "link": f"https://news.ycombinator.com/item?id={post_id}",
            "post": paragraphs(posts[post_id]["text"]),
            "checked": False,
            "notes": f"prefilled from {model}",
            "expected": {key: fields[key] for key in ("company", "roles", "remote", "uruguay_allowed")},
        })
        print(f"added {post_id}: {fields['company']}")

    TESTS.write_text(json.dumps(tests, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{len(tests)} posts in the test set")


if __name__ == "__main__":
    main()
