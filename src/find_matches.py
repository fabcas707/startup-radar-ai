"""Step 3: extract every post of a thread, save the results, and print the matches.

Usage: python src/find_matches.py 50338728 [model]

Results are saved one post per line in data/raw/whoishiring_<id>_<model>.jsonl,
one file per model, so the results of two models can be compared.
Posts already in that file are skipped, so a second run (or a run stopped with
Ctrl+C) never pays twice for the same post.
"""

import json
import sys
from pathlib import Path

import anthropic

from extract_posts import KEY_FILE, MODEL, extract


def load_done(path: Path) -> dict[int, dict]:
    if not path.exists():
        return {}
    rows = [json.loads(line) for line in path.read_text().splitlines() if line]
    return {row["post_id"]: row for row in rows}


def is_match(fields: dict) -> bool:
    has_role = any(role["is_fde_or_ai"] for role in fields["roles"])
    # Onsite or hybrid means moving there, so Uruguay only matters for remote posts.
    can_be_remote = fields["remote"] in ("yes", "not stated")
    return has_role and can_be_remote and fields["uruguay_allowed"] in ("yes", "not stated")


def main() -> None:
    item_id = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else MODEL
    thread = json.loads(Path(f"data/raw/whoishiring_{item_id}.json").read_text())
    posts = [c for c in thread["children"] if c.get("text")]

    out = Path(f"data/raw/whoishiring_{item_id}_{model}.jsonl")
    done = load_done(out)
    todo = [p for p in posts if p["id"] not in done]
    print(f"Model: {model}. {len(posts)} posts: {len(done)} already extracted, {len(todo)} to go")

    client = anthropic.Anthropic(api_key=KEY_FILE.read_text().strip())
    with out.open("a") as f:
        for i, post in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] post {post['id']}")
            try:
                fields = extract(client, post["text"], model)
            except anthropic.APIError as e:
                print(f"  error, skipped (a new run retries it): {e}")
                continue
            if fields is None:
                continue
            row = {"post_id": post["id"], **fields}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            done[post["id"]] = row

    matches = [row for row in done.values() if is_match(row)]
    print(f"\n{len(matches)} of {len(done)} posts match (an FDE or AI role, Uruguay allowed or not stated):\n")
    for row in matches:
        roles = ", ".join(r["title"] for r in row["roles"] if r["is_fde_or_ai"])
        print(f"- {row['company']}: {roles}")
        print(f"  {row['remote']} · {row['location_policy']} · Uruguay: {row['uruguay_allowed']} · pay: {row['pay']}")
        print(f"  https://news.ycombinator.com/item?id={row['post_id']}")


if __name__ == "__main__":
    main()
