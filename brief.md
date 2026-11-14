# Startup radar: project brief

## The client

**The first user: a data engineer in Latin America** who wants to move into FDE or applied AI work and is curious about startups. They don't follow the startup market: no time, no idea where to look, and no record.

**Later:** anyone who follows startups to find a job or a business idea, such as developers, job seekers and early founders.

## The problem

Startup news is spread across many places: funding news, job posts, company directories and trend reports. Following it by hand takes hours every week. They need one place that answers a few questions in minutes, with sources.

**How it's used:** every Monday, for 15 minutes: read the answers and pick 1–2 startups to apply to or to study.

## The 5 questions

Ordered by how much the user needs them.

### 1. Which startups are hiring for the user's profile?

Startups with open FDE, applied AI engineer or AI data engineer roles that are open from the user's country (Uruguay in this version) or remote.

**A good answer:** a list of openings from the last 30 days, each with the company, the role, where it can be done from, the date posted and a link. It says when a posting excludes Uruguay, or doesn't say.

> 3 openings this month match your profile:
> - Startup A, Forward Deployed Engineer, remote (Americas), posted 12/10. [link]
> - Startup B, Applied AI Engineer, remote (worldwide), posted 20/10. [link]
> - Startup C, AI Data Engineer, posted 25/10. It doesn't say whether it hires outside the US. [link]

### 2. Which startups stood out this week or month?

The top 3, ranked by a score. A startup gets points for the size of a funding round, a new product launch, an acquisition, and fitting the user's targets (AI, hiring FDEs). The answer shows the score, so the user can see why one ranks above another.

**A good answer:** for each startup, what it does in one line, the event (the amount, the round, the date), why it matters, and the source.

> Last month, 3 startups got the most attention:
> - **Startup A** (score 9): builds … Raised USD 100M in a Series B on 14/10. It follows the trend of …
> - **Startup B** (score 7): does … It launched product X, which helps … with …
> - **Startup C** (score 6): helps … Google bought it on 22/10. Google seems to be expanding into …

### 3. Where is the money going?

In the last month or quarter: how much was invested, and the share that went to each domain (finance, health, retail, games, developer tools…). Inside AI: which layer (models, infrastructure, data, applications, agents).

**A good answer:** the top 5 domains by money and by number of rounds, compared with the period before, with 2–3 example startups in each. Every number has its period and its source.

> In October, startups raised USD 3 billion in total. AI startups took 60 %, up from 45 % in September. The top domains were:
> 1. AI agents for finance: 35 % (Startups X and Y, which …)
> 2. AI for retail: 25 % (…)
> 3. Games: … Startups G1, G2 and G3 grew fast this year; what they have in common is …

### 4. Which new trends are starting?

Kinds of products or uses of AI that are new or growing fast, like agentic AI when it started.

**A good answer:** the trend in one line, when it started, 3 example startups, and how fast it's growing (new startups or rounds per month). When there are too few examples, it says "too early to tell".

> New this month: "AI that reads receipts for small shops". 4 startups raised a seed round since August (A, B, C, D), compared with none before July.

### 5. What do the reports say about how startups do?

Background that changes slowly: the stages of a startup (pre-seed, seed, Series A…), how many survive, and in which domains and business models (B2B, B2C) they do better.

**A good answer:** a figure with its source and year, never a figure without a source. If the reports disagree, it says so.

> According to report U1 (2025), about X % of startups with a seed round reach a Series A within 2 years. The rate is higher for B2B startups (…) than for B2C (…). Report U2 gives a lower figure, because it counts …

## What every answer must have

- **Sources:** a link and a date for every fact.
- **Freshness:** the period it covers, and when the data was last updated.
- **Honesty:** "I don't know" or "no data" instead of a guess. No made-up figures.
- **Length:** it can be read in 2 minutes.

## Out of scope, for now

- Investment advice.
- Startups outside tech.
- Real-time news: a weekly update is enough.
- Latin America: the US and global data first.

## Sources

### Q1. Hiring (reviewed 31/10)

| Source | Link | What it gives | Notes |
|---|---|---|---|
| Hacker News "Who is hiring?" (monthly) | https://news.ycombinator.com/submitted?id=whoishiring | Openings posted by the companies, many remote | Free text: an LLM turns it into structured data (phase 1) |
| HN Search API (Algolia) | https://hn.algolia.com/api | The same threads as JSON, a whole thread in one call | Free, no key, about 10,000 requests per hour |
| Greenhouse job boards | https://developers.greenhouse.io/job-board.html | All the openings of one company, structured | Public API, no key. Needs each company's board name |
| Lever job boards | https://github.com/lever/postings-api | Same, with a remote / hybrid / on-site field | Public API, no key |
| Ashby job boards | https://developers.ashbyhq.com/docs/public-job-posting-api | Same, often with the pay | Public API, no key. Popular with new AI startups |
| YC Work at a Startup | https://www.workatastartup.com/ | Openings at YC startups | Login, no API: not usable by the radar |

How they work together: HN (and later YC and the funding news) says which startups to look at; the ATS boards give everything each one is hiring for.

### Q2 to Q5 (to check)

Links checked on 31/10; access and terms still to check before building on them.

| Q | Source | Link | What it gives | Notes |
|---|---|---|---|---|
| 2, 3 | SEC EDGAR search (Form D) | https://www.sec.gov/edgar/search/ | US rounds: amount, date, a broad industry group | No description of the company; filed late. Scripts must send a User-Agent with a name and an email |
| 3 | SEC Form D data sets | https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets | Every Form D, in quarterly files | For my own totals (US only) |
| 2 | Product Hunt | https://www.producthunt.com/ | New product launches | API: https://api.producthunt.com/v2/docs |
| 2 | TechCrunch, Venture | https://techcrunch.com/category/venture/ | Rounds, launches, acquisitions | Articles: an LLM extracts the facts (RSS feeds) |
| 2, 3 | Crunchbase News | https://news.crunchbase.com/ | Same, plus monthly funding recaps by sector (https://news.crunchbase.com/venture/) | Free to read; the data behind it is paid |
| 4 | YC company directory | https://www.ycombinator.com/companies | What each batch builds, by tag | No official API; the unofficial `yc-oss/api` copies it to JSON daily (https://yc-oss.github.io/api/companies/all.json): check the terms |
| 4 | YC Requests for Startups | https://www.ycombinator.com/rfs | What investors want built | A few times a year |
| 4 | Show HN | https://news.ycombinator.com/show | What gets launched and discussed | Count per month for growth |
| 5 | Carta data | https://carta.com/data/ | Rounds by stage, time between rounds, shutdowns | Look for "State of Private Markets" |
| 5 | Stanford AI Index | https://hai.stanford.edu/ai-index | AI investment by country and area | Yearly, free PDF |
| 5 | State of AI Report | https://www.stateof.ai/ | AI research and industry | Yearly |
| 5 | McKinsey "The State of AI" | https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai | How companies use AI | Yearly |
| 5 | PitchBook-NVCA Venture Monitor | https://nvca.org/research/pitchbook-nvca-venture-monitor/ | US venture totals | Quarterly, free with a form |

Crunchbase would be the best single source for Q2 and Q3, but it's paid. The free route (Form D, the YC directory, the news) needs matching the same startup across sources: the entity resolution part of the project.
