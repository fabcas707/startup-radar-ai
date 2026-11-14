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

## Folders

| Folder | What |
|---|---|
| `src/` | The 4 steps of the HN job matcher, and `add_tests.py` |
| `tests/` | `expected.json`: the hand-checked test set |
| `data/raw/` | The downloaded thread and the model's answers (not committed) |
| `notes/` | Course notes: what each module taught and what I'd use here |
