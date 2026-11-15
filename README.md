# Startup Radar AI

A **startup radar**: an AI assistant that answers "Which AI startups raised money recently, what do they do, and are they hiring for a given profile?", from public sources (Hacker News "Who is hiring?", SEC Form D filings, the Y Combinator directory) and free trend reports. Built like a client case: a problem, the solution, and measured results. The first slice of a bigger idea: a market radar for investment, startup ideas and job openings.

It's my learning project for building LLM applications end to end: LLMs, RAG, agents, evaluation and deployment. The client, the problem and the 5 questions it must answer are in `brief.md`.

Status (12/11/2026): the first piece, the **HN job matcher**, works and is measured. It answers question 1 of the brief: "Which startups are hiring for the user's profile?"

## The HN job matcher

**The problem:** the monthly Hacker News "Who is hiring?" thread has about 175 job posts, written as free text. Reading all of them to find the few that fit takes hours.

**The solution:** a script downloads the thread, Claude Haiku reads each post and returns the same fields for every one (company, roles, remote policy, whether Uruguay is allowed, pay), and a simple rule keeps the posts that fit the user's profile: at least one forward-deployed or AI role, remote, and Uruguay allowed or not stated.

**The result:** on the November 2026 thread, 23 matches out of 175 posts, in a few minutes and for a few cents.

### How it works

Run each step from this folder, with the virtual environment: `.venv/bin/python src/<script>`. The Anthropic API key is read from `~/.config/anthropic_api_key`.

| Step | Script | What it does | Output |
|---|---|---|---|
| 1 | `fetch_thread.py 50338728` | Downloads the thread from the HN Algolia API | `data/raw/whoishiring_50338728.json` |
| 2 | `extract_posts.py 50338728 5 claude-haiku-5-5` | A trial on a few posts: Claude extracts the fields with structured outputs (a JSON schema), so every answer has the same shape | printed only |
| 3 | `find_matches.py 50338728 claude-haiku-5-5` | Extracts all the posts (skipping the ones already done) and prints the matches | `data/raw/whoishiring_50338728_claude-haiku-5-5.jsonl` |
| 4 | `score.py claude-haiku-5-5` | Compares step 3 with the hand-checked test set | field accuracy, precision, recall |

`add_tests.py` adds posts to the test set, prefilled with the model's answers and marked `"checked": false`, to check by hand.

`data/raw/` isn't committed: steps 1 and 3 recreate it.

### Evaluation

**The test set:** 29 posts in `tests/expected.json`, each one read and corrected by hand, with a note on why. 15 were checked on 3/11 and 14 on 12/11 (a 15th was deleted from HN before it could be checked). The new ones include 3 "Remote (US)" posts, the known weak spot, 6 that Haiku marked as matches, and 6 random non-matches.

**Results with Claude Haiku 5.5** (12/11/2026):

| Measure | Result |
|---|---|
| Company | 29/29 |
| Remote policy | 29/29 |
| Uruguay allowed | 27/29 |
| Has an FDE or AI role | 28/29 |
| Match precision | 90 % (9 of 10 matches right) |
| Match recall | 90 % (9 of 10 real matches found) |

The errors: Estuary says US only, and Haiku read it as "not stated", so it's a false match. MixRank has an AI role that Haiku didn't see, so it's a missed match. Blockrotate prefers US or EU time zones, which I count as Uruguay allowed, and Haiku said "not stated"; the match result is the same.

On 3/11, with the first 15 posts, precision and recall were both 80 %. A first version of the rule also kept onsite and hybrid posts, which gave 40 % precision; dropping them gave the 80 %.

**On the full thread, precision is lower: about 60 %.** On 3/11 I read the 23 matches and judged about 9 of them wrong, so about 14 of 23 are right. That's a quick estimate, not a hand-checked score. The test set scores higher because it holds only 10 of the 23 matches, and the wrong ones are mostly outside it: posts like "Remote (US)" that Haiku reads as "Uruguay not stated". Recall on the full thread isn't measured.

## Known limits

- **The test set leans toward Haiku.** Its answers were prefilled from Haiku and then corrected, and 6 of the new posts were chosen because Haiku had marked them as matches. Both push the scores up.
- **"Remote (US)" is the weak spot.** Haiku often reads it as "Uruguay not stated", which lets US-only posts through as matches.
- **No seniority filter.** The rule checks the role, remote and Uruguay, but not years of experience. eventfirst (10+ years) counts as a right match but doesn't fit the profile; counted that way, precision on the test set is 80 %.
- **Role titles aren't scored**, because they're free text. Only "has an FDE or AI role" is checked.
- **One post can list several roles, but remote, location and pay are stored once per post.** FusionAuth is remote for one role and onsite for the others, so it's stored as "hybrid".
- **One thread, one model.** All the numbers are for the November 2026 thread and Claude Haiku 5.5.

## The small RAG (first version, 15/11/2026)

The first piece for question 5 of the brief ("What do the reports say…?"): questions about one report, the State of AI Report 2026 (244 pages), answered only from the report, with the page of every source.

**How it works:**

1. `src/rag_index.py` reads the PDF page by page, removes the text printed on every slide (the navigation bar, the footer, the slide number), and cuts each page into chunks of at most 200 tokens, counted with the embedding model's own tokenizer, with 30 tokens of overlap. The section name ("Section 1: Research") goes in front of each chunk. The embedding model (`all-MiniLM-L6-v2`, run locally) reads at most 256 tokens, so the script stops if any chunk is longer: nothing is cut. Result: 331 chunks.
2. `src/rag_ask.py` embeds the question, takes the 5 closest chunks by cosine similarity (a dot product in numpy, no vector database yet), and gives them to Claude as numbered sources, with three rules: use only the sources, cite one after each sentence, and say "the excerpts don't answer this" when they don't.

**Results on 7 questions** (`tests/rag_questions.json`). Each answer scored by hand from 1 to 10, then reviewed: a good answer has to be both supported by its sources and useful.

| # | Question | Expected page in the top 5? | Answer |
|---|---|---|---|
| 1 | What's in the report? (asked as "What's in the report?") | No (page 4); the welcome slide (page 3) came 5th | Haiku 6/10: every claim is supported, but it describes 4 unrelated chunks as if they were the report's sections |
| 2 | The most intelligent model, open-weight and closed | Yes, 2nd | Opus 10/10: the closed leader with its score, and it says the excerpts only name China's best open-weight model |
| 3 | Can a model avoid its harness? | Yes, 1st | Haiku 8/10, Opus 7/10: both said the excerpts don't answer it, though page 15 does ("stronger models can outgrow their harnesses"). Haiku then answered well, one citation per sentence; Opus put everything in one sentence with the citations at the end |
| 4 | How are robots trained? | Yes, 2nd | Opus 10/10: four methods, each cited |
| 5 | A model that runs an online store and earns money | Yes (page 46), 2nd | Haiku 10/10: "partly, in a simulation", with the numbers and the limits |
| 6 | What does harness mean? | Yes (page 203), 2nd | Haiku 10/10: the report's own definition |
| 7 | AI companies in Uruguay (not in the report) | Not applicable | Haiku 10/10: it said the excerpts don't answer it, and what they cover instead |

Retrieval found the expected page for 5 of 6 questions. I checked the cited facts against their chunks (17 numbers and names): all were there, so no answer made anything up.

**What it showed:**

- **Similarity scores can't detect "not in the report".** The retriever always returns 5 chunks, and question 7 got a higher top score (0.55) than question 3's right chunk (0.49). The grounding rule in the prompt is what caught it.
- **Overview questions don't fit top-5 retrieval.** "What's in the report?" needs the summary page, not the 5 chunks closest to the words of the question. The wording matters too: the longer "What information is contained in the State of AI Report 2026?" put the welcome slide 1st (0.74); "What's in the report?" put it 5th.
- **The abstention rule can be too strict.** On question 3 both models said "the excerpts don't answer this" when the answer was there in other words. A vague question needs a partial answer, not a refusal.

**Known limits:** 7 questions, written and scored by me; one report; each answer run once per model; no vector database, which is fine for hundreds of chunks, not millions. Next, by 29/11: 3–4 reports, a bigger test set, Chroma or pgvector, and hybrid search.

## Folders

| Folder | What |
|---|---|
| `src/` | The 4 steps of the HN job matcher, `add_tests.py`, and the small RAG (`rag_index.py`, `rag_ask.py`) |
| `tests/` | `expected.json`: the hand-checked test set of the job matcher; `rag_questions.json`: the RAG's 7 questions |
| `data/raw/` | The downloaded thread, the model's answers and the report PDF (not committed) |
| `data/rag/` | The RAG's chunks and vectors (not committed: the text is the report's) |
| `notes/` | Course notes: what each module taught and what I'd use here |
