"""Ask the small RAG a question (task 1.3).

Step 4: retrieval. It embeds the question, compares it with every chunk saved
by rag_index.py, and keeps the TOP_K closest ones.
Step 5: the answer. Claude gets the question and those chunks as numbered
sources, answers only from them, cites them, and says so when they don't
contain the answer (grounding).

Run from the repo folder:
    .venv/bin/python src/rag_ask.py "Can a model avoid its harness?"
    .venv/bin/python src/rag_ask.py --model claude-haiku-5-5 "Can a model avoid its harness?"
"""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")  # the model is already downloaded: don't call the Hub

import anthropic
import numpy as np
from sentence_transformers import SentenceTransformer

from rag_index import MODEL as EMBEDDING_MODEL
from rag_index import OUT

TOP_K = 5
MODEL = "claude-opus-5-5"
KEY_FILE = Path.home() / ".config" / "anthropic_api_key"

# The grounding rules. Retrieval always returns TOP_K chunks, even when none
# is relevant, so only the model can tell "not in the report".
INSTRUCTIONS = """You answer questions about the State of AI Report 2026, using only the numbered sources you are given, which are excerpts of the report.

Rules:
- Use only the sources. Don't add facts from your own knowledge, even if you know them.
- After each sentence that uses a source, cite it by its number in brackets, like [2]. Cite several when needed, like [1][3].
- If the sources don't contain the answer, say: "The report excerpts I have don't answer this." Then say in one sentence what they cover that comes closest, if anything.
- If the sources answer only part of the question, answer that part and say which part they don't cover.
- Keep the answer under 150 words."""


def retrieve(question: str, model, chunks: list[dict], vectors: np.ndarray, k: int = TOP_K):
    """Return the k chunks closest in meaning to the question, with their scores."""
    q = model.encode(question, normalize_embeddings=True)  # 384 numbers, length 1
    # Every vector has length 1, so a dot product is the cosine similarity:
    # one multiplication of the chunks x 384 matrix by the question's vector.
    scores = vectors @ q
    best = np.argsort(scores)[::-1][:k]  # the positions of the k highest scores
    return [(chunks[i], float(scores[i])) for i in best]


def answer(client: anthropic.Anthropic, question: str, retrieved: list, model: str = MODEL) -> str:
    """Stuff the retrieved chunks into one prompt as numbered sources, and ask Claude."""
    sources = "\n\n".join(
        f'<source id="{n}" page="{chunk["page"]}" section="{chunk["section"]}">\n{chunk["text"]}\n</source>'
        for n, (chunk, _score) in enumerate(retrieved, start=1)
    )
    # If a safety check declines, the API retries on another model.
    # Haiku has no such fallback, and the parameter would make the request fail.
    fallback = {} if model.startswith("claude-haiku") else {
        "betas": ["server-side-fallback-2026-07-01"],
        "fallbacks": "default",
    }
    response = client.beta.messages.create(
        model=model,
        max_tokens=16000,
        output_config={"effort": "medium"},
        **fallback,
        system=INSTRUCTIONS,
        messages=[{"role": "user", "content": f"{sources}\n\nQuestion: {question}"}],
    )
    if response.stop_reason == "refusal":
        return "(declined by a safety check)"
    usage = response.usage
    print(f"(tokens: {usage.input_tokens} in, {usage.output_tokens} out)\n")
    return "".join(block.text for block in response.content if block.type == "text")


def main() -> None:
    args = sys.argv[1:]
    model = MODEL
    if args[:1] == ["--model"]:
        model, args = args[1], args[2:]
    question = " ".join(args)
    if not question:
        raise SystemExit('Usage: .venv/bin/python src/rag_ask.py [--model claude-haiku-5-5] "your question"')

    chunks = json.loads((OUT / "chunks.json").read_text())
    vectors = np.load(OUT / "embeddings.npy")
    embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    retrieved = retrieve(question, embedder, chunks, vectors)

    print(f"Question: {question}\n\nSources (retrieval):")
    for n, (chunk, score) in enumerate(retrieved, start=1):
        print(f"[{n}] {score:.2f}  page {chunk['page']}  {chunk['text'][:90]}...")

    client = anthropic.Anthropic(api_key=KEY_FILE.read_text().strip())
    print(f"\nAnswer ({model}):")
    print(answer(client, question, retrieved, model))


if __name__ == "__main__":
    main()
