"""Index the State of AI Report 2026 for the small RAG (task 1.3).

Reads the PDF page by page, cuts each page into chunks measured in tokens,
puts the section name in front of each chunk, embeds every chunk, and saves
the chunks and their vectors in data/rag/ (not committed: the text is the
report's).

Run from the repo folder: .venv/bin/python src/rag_index.py
"""

import json
import re
from pathlib import Path

import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

PDF = Path("data/raw/state_of_ai_2026.pdf")
OUT = Path("data/rag")
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_TOKENS = 200  # the model reads at most 256 tokens, 2 of them its own markers
OVERLAP_TOKENS = 30  # tokens repeated at the start of the next chunk
MAX_WORD_CHARS = 100  # the tokenizer turns a longer word into one [UNK] token

# Text printed on every slide that isn't content: the navigation bar, the
# footer and the slide number. Repeated in every chunk, it would make all the
# vectors look alike, so it's removed before chunking.
NAV = re.compile(r"Introduction\s*\|\s*Research\s*\|\s*Industry\s*\|\s*Politics\s*\|\s*Safety\s*\|\s*Predictions")
FOOTER = re.compile(r"stateof\.ai 2026")
# The slide number ("| 14") is usually last, but on a few slides it comes after
# the title. Checked on 15/11: every "| N" left in the text was the slide number.
SLIDE_NUMBER = re.compile(r"\|\s*\d{1,3}\b")
# A section's title slide, for example "Section 2: Industry".
SECTION_TITLE = re.compile(r"^Section \d+: \w+$")


def clean(text: str) -> str:
    """Remove the repeated non-content text and collapse the white space."""
    text = NAV.sub(" ", text)
    text = FOOTER.sub(" ", text)
    text = SLIDE_NUMBER.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def split(text: str, prefix: str, tokenizer) -> list[str]:
    """Cut one page's text into chunks of at most CHUNK_TOKENS tokens, prefix included.

    Words are packed whole, so no word is cut. The next chunk starts
    OVERLAP_TOKENS tokens back, so an idea that falls on a cut is in both.
    """
    budget = CHUNK_TOKENS - len(tokenizer(prefix, add_special_tokens=False)["input_ids"])

    def n_tokens(word: str) -> int:
        return len(tokenizer(word, add_special_tokens=False)["input_ids"])

    def fit(word: str) -> list[str]:
        """Split a word that's too long (a long URL, say) into halves until each fits.

        Two limits: the token budget, and the tokenizer's 100 characters per word.
        A longer word becomes a single [UNK] (unknown) token, so its content
        would be lost without any error.
        """
        if (len(word) <= MAX_WORD_CHARS and n_tokens(word) <= budget) or len(word) == 1:
            return [word]
        half = len(word) // 2
        return fit(word[:half]) + fit(word[half:])

    words = [piece for word in text.split(" ") for piece in fit(word)]
    # Tokens per word: the model's tokenizer splits on spaces first,
    # so the sum of the words' tokens is the chunk's token count.
    counts = [len(ids) for ids in tokenizer(words, add_special_tokens=False)["input_ids"]]

    chunks = []
    start = 0
    while start < len(words):
        end, used = start, 0
        while end < len(words) and used + counts[end] <= budget:
            used += counts[end]
            end += 1
        end = max(end, start + 1)  # always take at least one word (fit() keeps it under the budget)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        # Step back OVERLAP_TOKENS tokens, but always move forward.
        back, repeated = end, 0
        while back > start + 1 and repeated + counts[back - 1] <= OVERLAP_TOKENS:
            repeated += counts[back - 1]
            back -= 1
        start = back
    return chunks


def main() -> None:
    model = SentenceTransformer(MODEL, device="cpu")
    reader = PdfReader(PDF)

    chunks = []
    section = "Introduction"  # the pages before "Section 1"
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean(page.extract_text() or "")
        if SECTION_TITLE.match(text):
            section = text  # it goes in front of every chunk until the next section
            continue
        if not text:
            continue
        prefix = f"{section}. "
        for piece in split(text, prefix, model.tokenizer):
            chunks.append({"id": len(chunks), "page": page_number, "section": section, "text": piece})
    print(f"{len(reader.pages)} pages -> {len(chunks)} chunks")

    # What gets embedded: the section name, then the chunk.
    to_embed = [f"{c['section']}. {c['text']}" for c in chunks]
    # The guarantee: if any chunk is longer than the model can read, its end
    # would be ignored by the embedding, so stop here instead of indexing it.
    token_ids = [model.tokenizer(t)["input_ids"] for t in to_embed]
    lengths = [len(ids) for ids in token_ids]
    # [UNK] marks characters the model doesn't know (symbols like "●" or emoji):
    # print how many, to see whether any real words are being lost.
    unknown = sum(ids.count(model.tokenizer.unk_token_id) for ids in token_ids)
    print(f"Unknown tokens ([UNK]) in all chunks: {unknown}")
    too_long = [c["id"] for c, n in zip(chunks, lengths) if n > model.max_seq_length]
    if too_long:
        raise SystemExit(f"Stopped: chunks {too_long} are longer than {model.max_seq_length} tokens")
    print(f"Longest chunk: {max(lengths)} tokens (the model reads {model.max_seq_length}): nothing is cut")

    # normalize_embeddings=True gives every vector length 1,
    # so cosine similarity is a plain dot product in rag_ask.py.
    vectors = model.encode(to_embed, normalize_embeddings=True, show_progress_bar=True)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=1))
    np.save(OUT / "embeddings.npy", vectors)
    print(f"Saved {OUT}/chunks.json and {OUT}/embeddings.npy, shape {vectors.shape}")


if __name__ == "__main__":
    main()
