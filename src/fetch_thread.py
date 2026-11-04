"""Step 1: download one "Who is hiring?" thread from the HN Algolia API and save it.

Usage: python3 src/fetch_thread.py 50338728
"""

import json
import sys
import urllib.request
from pathlib import Path

API = "https://hn.algolia.com/api/v1/items/{id}"


def fetch(item_id: str) -> dict:
    with urllib.request.urlopen(API.format(id=item_id), timeout=30) as resp:
        return json.load(resp)


def main() -> None:
    item_id = sys.argv[1]
    thread = fetch(item_id)

    out = Path("data/raw") / f"whoishiring_{item_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(thread, indent=2))

    # Each top-level comment is one job post; replies are discussion.
    posts = [c for c in thread["children"] if c.get("text")]
    print(f"{thread['title']}: {len(posts)} posts, saved to {out}")
    print("\nFirst post, raw:\n")
    print(posts[0]["text"][:800])


if __name__ == "__main__":
    main()
