"""Step 2: extract structured fields from a few job posts with Claude.

Usage: python src/extract_posts.py 50338728 5 [model]
(reads data/raw/whoishiring_<id>.json from step 1; the second number is how many posts;
the model is optional, for example claude-haiku-5-5)
"""

import json
import sys
from pathlib import Path

import anthropic

MODEL = "claude-opus-5-5"
KEY_FILE = Path.home() / ".config" / "anthropic_api_key"

# The shape every answer must have. Structured outputs make Claude return
# exactly this JSON, so the code never has to guess how to read the reply.
SCHEMA = {
    "type": "object",
    "properties": {
        "company": {"type": "string"},
        "roles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "is_fde_or_ai": {"type": "boolean"},
                },
                "required": ["title", "is_fde_or_ai"],
                "additionalProperties": False,
            },
        },
        "remote": {"type": "string", "enum": ["yes", "no", "hybrid", "not stated"]},
        "location_policy": {"type": "string"},
        "uruguay_allowed": {"type": "string", "enum": ["yes", "no", "not stated"]},
        "pay": {"type": "string"},
    },
    "required": ["company", "roles", "remote", "location_policy", "uruguay_allowed", "pay"],
    "additionalProperties": False,
}

INSTRUCTIONS = """Extract the facts from this Hacker News "Who is hiring?" post.
- roles: every open role in the post. is_fde_or_ai is true for forward-deployed,
  solutions or customer-facing engineering roles, and for roles that build with
  LLMs or AI; false otherwise.
- location_policy: what the post says about where people can work from, in a few words.
- uruguay_allowed: "yes" only if Uruguay, Latin America, the Americas or anywhere
  is allowed; "no" if the post limits it to places that exclude Uruguay.
- pay: as written in the post, or "not stated".
Use only what the post says; never guess.

Post:
"""


def extract(client: anthropic.Anthropic, post_text: str, model: str = MODEL) -> dict | None:
    # If a safety check declines a post, the API retries it on another model.
    # Haiku has no such fallback, and the parameter would make the request fail.
    fallback = {} if model.startswith("claude-haiku") else {
        "betas": ["server-side-fallback-2026-07-01"],
        "fallbacks": "default",
    }
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        # Extraction is a simple task: low effort is cheaper and fast enough.
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        **fallback,
        messages=[{"role": "user", "content": INSTRUCTIONS + post_text}],
    )
    if response.stop_reason == "refusal":
        print("  (declined, skipped)")
        return None
    usage = response.usage
    print(f"  tokens: {usage.input_tokens} in, {usage.output_tokens} out")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def main() -> None:
    item_id, how_many = sys.argv[1], int(sys.argv[2])
    model = sys.argv[3] if len(sys.argv) > 3 else MODEL
    print(f"Model: {model}")
    thread = json.loads(Path(f"data/raw/whoishiring_{item_id}.json").read_text())
    posts = [c for c in thread["children"] if c.get("text")][:how_many]

    client = anthropic.Anthropic(api_key=KEY_FILE.read_text().strip())

    for post in posts:
        print(f"\nPost {post['id']} by {post['author']}")
        fields = extract(client, post["text"], model)
        if fields:
            print(json.dumps(fields, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
