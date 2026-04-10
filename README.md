# OpenFootprint 🔍

> **Open-source OSINT intelligence platform.** Aggregate digital identities from publicly available data sources — emails, usernames, developer profiles, news mentions — with AI-powered orchestration and graph-based identity resolution.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![Next.js 14](https://img.shields.io/badge/Next.js-14-black)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---
<img width="1540" height="1104" alt="Screenshot 2026-03-31 003720" src="https://github.com/user-attachments/assets/6d205fc8-a010-429a-9149-61ef8ff6c14f" />


## What is OpenFootprint?

OpenFootprint is a modular OSINT (Open Source Intelligence) platform that lets you search for a person's digital presence across the public web by providing a name, email address, or username.

It runs multiple **data connectors** in parallel, uses a **LangChain AI agent** to orchestrate findings intelligently, performs **identity resolution** with confidence scoring, stores results in a **Neo4j identity graph**, and surfaces everything in a **Next.js dashboard** with force-directed graph visualization.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Next.js Frontend                            │
│   Search Bar → Job Polling → Profile View → Identity Graph Viz     │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼────────────────────────────────────────┐
│                      FastAPI Backend                                │
│  POST /search  →  Create Job  →  Dispatch Celery Task              │
│  GET  /result/{id}  →  Poll status / Return results                │
└────────┬───────────────────────────────────┬────────────────────────┘
         │                                   │
┌────────▼──────────┐             ┌──────────▼────────────────────────┐
│  Redis (broker)   │             │     PostgreSQL                    │
│  Celery queues    │             │     Search jobs + results         │
└────────┬──────────┘             └───────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────────────┐
│                   Celery Worker                                    │
│                                                                    │
│   ┌─────────────────────────────────────────────────────────┐     │
│   │              LangChain Orchestrator Agent               │     │
│   │  Reads query → decides which connectors to call → runs  │     │
│   └──────────┬──────────────────────────────────────────────┘     │
│              │ calls                                               │
│   ┌──────────▼──────────────────────────────────────────────┐     │
│   │                    Connectors                           │     │
│   │  HIBP │ Hunter.io │ GitHub │ Sherlock │ SerpAPI │ News  │     │
│   └──────────┬──────────────────────────────────────────────┘     │
│              │ raw results                                         │
│   ┌──────────▼──────────────────────────────────────────────┐     │
│   │              Identity Resolution Engine                 │     │
│   │  Username similarity · Bio embeddings · Graph clustering │     │
│   │  → ResolvedProfile with confidence score               │     │
│   └──────────┬──────────────────────────────────────────────┘     │
│              │ write                                               │
│   ┌──────────▼──────────────────────────────────────────────┐     │
│   │                Neo4j Identity Graph                     │     │
│   │  Person → Email / Username / Profile nodes + SAME_AS    │     │
│   └─────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Details |
|---|---|
| **Email Intelligence** | Have I Been Pwned breach check + Hunter.io verification |
| **Developer Footprint** | GitHub profile, repos, commit emails, language breakdown |
| **Username Search** | Sherlock across 300+ platforms |
| **Web Mentions** | NewsAPI, HackerNews (Algolia), DEV.to, SerpAPI/Google |
| **AI Orchestrator** | LangChain ReAct agent selects connectors intelligently |
| **Identity Resolution** | Levenshtein + Jaro-Winkler + sentence-transformer embeddings |
| **Confidence Scoring** | Multi-signal 0–100% score per resolved profile |
| **Identity Graph** | Neo4j graph with Person → Email/Username/Profile edges |
| **Async Pipeline** | Celery + Redis worker queue with Flower monitoring |
| **Graph Visualization** | Force-directed D3 graph in Next.js dashboard |
| **REST API** | FastAPI with OpenAPI docs, rate limiting, structured JSON |

---

## Data Sources

All sources are **publicly available** and used within free tier limits:

| Connector | Data | Free Tier | Key Required |
|---|---|---|---|
| **Have I Been Pwned** | Email breach history | 1 req/1.5s | Optional (faster with key) |
| **Hunter.io** | Email verification + sources | 25/month | Yes |
| **GitHub API** | Profile, repos, commit emails | 60/hr (5000 with token) | Optional |
| **Sherlock** | Username across 300+ sites | Unlimited | No |
| **SerpAPI** | Google search results | 100/month | Yes |
| **NewsAPI** | News article mentions | 100/day | Yes |
| **HackerNews** | HN story/comment search | Unlimited | No |
| **DEV.to** | Developer articles | Unlimited | No |

> **Note:** OpenFootprint respects `robots.txt`, API rate limits, and platform Terms of Service. It does not scrape platforms that prohibit crawling.

---

## Quickstart

> **Three commands to run the full stack.** Docker handles everything — databases, workers, frontend, backend.

### Step 1 — Install Docker

If you don't have Docker, install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (free, works on Mac/Windows/Linux). That's the only prerequisite.

### Step 2 — Clone the repo

```bash
git clone https://github.com/your-org/digitalfootprint.git
cd digitalfootprint
```

When you clone this repo, you get this folder structure:

```
digitalfootprint/
├── backend/          ← Python API + all connectors
├── frontend/         ← Next.js dashboard
├── docker-compose.yml
├── .env.example      ← copy this to .env
└── README.md
```

### Step 3 — Add your API keys

```bash
cp .env.example .env
```

Then open `.env` in any text editor and fill in your keys. The app works with **zero keys** (using GitHub anonymous + HackerNews + DEV.to which need nothing), but the more keys you add the more data you get:

| Key | Where to get it | Free tier | What it unlocks |
|---|---|---|---|
| `GITHUB_TOKEN` | [github.com/settings/tokens](https://github.com/settings/tokens) — click "Generate new token (classic)", check nothing, just generate | Free, unlimited | 5000 req/hr instead of 60 |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | ~$0.01/search with gpt-4o-mini | AI picks the best connectors for your query |
| `HIBP_API_KEY` | [haveibeenpwned.com/API/Key](https://haveibeenpwned.com/API/Key) | $3.50/mo | Paste exposure + faster breach checks |
| `HUNTER_API_KEY` | [hunter.io/users/sign_up](https://hunter.io/users/sign_up) | 25 searches/mo | Email verification + source list |
| `SERPAPI_KEY` | [serpapi.com/users/sign_up](https://serpapi.com/users/sign_up) | 100 searches/mo | Google search results |
| `NEWS_API_KEY` | [newsapi.org/register](https://newsapi.org/register) | 100 req/day | News article mentions |

**Minimum useful setup** — just set `GITHUB_TOKEN`. It's free, takes 30 seconds, and makes a big difference.

### Step 4 — Start everything

```bash
docker compose up -d
```

This single command builds and starts 7 services:

| Service | URL | What it does |
|---|---|---|
| **Next.js frontend** | http://localhost:3000 | The search dashboard — start here |
| **FastAPI backend** | http://localhost:8000/docs | REST API with interactive Swagger UI |
| **Celery worker** | — | Runs search jobs in the background |
| **Flower monitor** | http://localhost:5555 | Watch background tasks in real time |
| **Neo4j graph DB** | http://localhost:7474 | Identity graph browser (user: `neo4j`, pass: `df_neo4j_pass`) |
| **PostgreSQL** | localhost:5432 | Stores jobs and results |
| **Redis** | localhost:6379 | Job queue broker |

First run takes 3–5 minutes while Docker pulls images and builds the containers. Subsequent starts take ~10 seconds.

### Step 5 — Run a search

Open **http://localhost:3000**, type a username or email, hit Search.

Or call the API directly:

```bash
# Submit a search job
curl -s -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "torvalds", "search_type": "username"}' | jq

# → {"job_id": "abc-123", "status": "pending", ...}

# Poll every few seconds until status = "completed"
curl -s http://localhost:8000/api/v1/result/abc-123 | jq .status
```

### Stopping / resetting

```bash
# Stop services (keeps data)
docker compose down

# Stop and wipe all data (start fresh)
docker compose down -v
```

---

## API Reference

### `POST /api/v1/search`

Submit a new OSINT search job.

**Request body:**
```json
{
  "query": "johndoe",
  "search_type": "username",
  "include_connectors": ["github", "sherlock"],
  "max_depth": 1
}
```

| Field | Type | Description |
|---|---|---|
| `query` | string | Email, username, or full name |
| `search_type` | `email\|username\|name\|combined` | Query type hint |
| `include_connectors` | string[] | Allowlist connectors (null = all) |
| `max_depth` | int 1–3 | Graph traversal depth |

**Response** `202 Accepted`:
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "pending",
  "message": "Poll GET /api/v1/result/{job_id} for results.",
  "created_at": "2024-06-01T12:00:00Z"
}
```

---

### `GET /api/v1/result/{job_id}`

Poll for results. Returns status-only while running, full result when complete.

**Response** `200 OK` (completed):
```json
{
  "job_id": "...",
  "query": "johndoe",
  "status": "completed",
  "duration_seconds": 18.4,
  "overall_confidence": 0.87,
  "total_emails": 2,
  "total_profiles": 1,
  "total_mentions": 14,

  "profiles": [{
    "profile_id": "...",
    "confidence_score": 0.87,
    "primary_identity": "John Doe",
    "emails": ["john@example.com"],
    "usernames": ["johndoe"],
    "names": ["John Doe"],
    "locations": ["San Francisco, CA"],
    "avatar_url": "https://avatars.githubusercontent.com/...",
    "bio": "Software engineer...",

    "github": { ... },
    "email_intel": [{ "email": "...", "breach_count": 2, "breaches": [...] }],
    "social_profiles": [{ "platform": "Twitter", "url": "...", "exists": true }],
    "mentions": { "news_articles": [...], "web_results": [...] }
  }],

  "connector_results": [
    { "connector": "github", "status": "success", "duration_ms": 842 },
    { "connector": "haveibeenpwned", "status": "success", "duration_ms": 1240 },
    { "connector": "sherlock", "status": "success", "duration_ms": 12500 }
  ],

  "graph_nodes": [...],
  "graph_edges": [...]
}
```

---

### `GET /api/v1/jobs`

List recent search jobs.

### `DELETE /api/v1/jobs/{job_id}`

Delete a job and its results.

### `GET /api/v1/connectors`

List all connectors and their availability status.

### `GET /health`

Service health check including Postgres, Redis, and Neo4j status.

---

## Configuration

All settings are in `.env` (copy from `.env.example`):

```env
# LLM — pick one (enables AI-guided connector selection)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Connectors
HIBP_API_KEY=...          # haveibeenpwned.com — optional
HUNTER_API_KEY=...        # hunter.io — free tier: 25/month
GITHUB_TOKEN=ghp_...      # github.com/settings/tokens — free
SERPAPI_KEY=...           # serpapi.com — free tier: 100/month
NEWS_API_KEY=...          # newsapi.org — free tier: 100/day

# Rate limiting
API_RATE_LIMIT=30         # requests per minute per IP

# Sherlock
SHERLOCK_TIMEOUT=10       # seconds per site check
```

---

## Adding a Connector

Connectors are self-contained modules in `backend/app/connectors/`. Adding one takes ~50 lines:

```python
# backend/app/connectors/myservice.py
from app.connectors.base import BaseConnector

class MyServiceConnector(BaseConnector):
    name = "myservice"
    description = "Fetch data from MyService API"
    required_keys = ["MY_SERVICE_API_KEY"]  # Settings attributes

    async def _execute(self, query: str, **kwargs) -> dict:
        resp = await self._get(
            "https://api.myservice.com/search",
            params={"q": query, "key": settings.MY_SERVICE_API_KEY},
        )
        return resp.json()
```

Then register it in `backend/app/connectors/__init__.py`:

```python
from app.connectors.myservice import MyServiceConnector
ALL_CONNECTORS = [..., MyServiceConnector]
```

The connector is automatically:
- Available if `MY_SERVICE_API_KEY` is set
- Exposed in `GET /api/v1/connectors`
- Offered as a LangChain tool to the AI agent
- Run in the direct (no-LLM) fallback mode

---

## Development

### Run without Docker

```bash
# Start dependencies only
docker compose up postgres neo4j redis -d

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Frontend
cd frontend
npm install
npm run dev
```

### Run tests

```bash
cd backend
pytest tests/ -v
```

### Database migrations

```bash
cd backend
# Generate a migration
alembic revision --autogenerate -m "add_column_x"
# Apply
alembic upgrade head
```

---

## Project Structure

```
digitalfootprint/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app factory
│   │   ├── config.py             # Pydantic settings
│   │   ├── api/
│   │   │   └── routes.py         # POST /search, GET /result/{id}
│   │   ├── agent/
│   │   │   ├── orchestrator.py   # LangChain ReAct agent
│   │   │   └── tools.py          # LangChain tool wrappers
│   │   ├── connectors/
│   │   │   ├── base.py           # BaseConnector (abstract)
│   │   │   ├── __init__.py       # Connector registry
│   │   │   ├── haveibeenpwned.py
│   │   │   ├── hunter.py
│   │   │   ├── github.py
│   │   │   ├── sherlock.py
│   │   │   ├── serpapi.py
│   │   │   └── news.py
│   │   ├── database/
│   │   │   ├── postgres.py       # SQLAlchemy async ORM
│   │   │   └── neo4j_db.py       # Neo4j identity graph
│   │   ├── identity/
│   │   │   └── resolver.py       # Identity resolution + scoring
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic request/response models
│   │   └── tasks/
│   │       ├── celery_app.py     # Celery configuration
│   │       └── search_tasks.py   # Async search pipeline task
│   ├── tests/
│   │   └── test_all.py
│   ├── alembic/                  # Database migrations
│   ├── sql/init.sql
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Home / search page
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── result/[id]/page.tsx  # Results dashboard
│   ├── components/
│   │   ├── ProfileCard.tsx       # Identity summary card
│   │   ├── GitHubPanel.tsx       # Developer footprint
│   │   ├── EmailIntelPanel.tsx   # Breach details
│   │   ├── IdentityGraph.tsx     # Force-directed graph
│   │   ├── ConnectorStatusPanel.tsx
│   │   ├── MentionsFeed.tsx
│   │   └── ConfidenceBadge.tsx
│   ├── lib/
│   │   ├── api.ts                # Typed API client
│   │   └── utils.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Confidence Scoring

Each resolved profile receives a confidence score (0–100%) based on multiple signals:

| Signal | Weight | Condition |
|---|---|---|
| GitHub username match | up to 25% | Username similarity to query |
| Email breach found | 20% | HIBP confirms email is real |
| Email clean (not breached) | 10% | HIBP confirms email exists |
| Sherlock: 2+ platforms | 20% | Username found on multiple sites |
| Sherlock: 1 platform | 10% | Username found on one site |
| Mentions found (5+) | 15% | News/web presence |
| Cross-source email | 10% | Same email in 2+ connectors |
| Bio similarity | up to 10% | Embedding cosine similarity |

---

## Ethics & Legal

DigitalFootprint is designed for **defensive security research**, **due diligence**, and **self-investigation** only.

- Only accesses **publicly available** data
- Respects `robots.txt` on all crawled domains
- Honors API rate limits and Terms of Service
- Does **not** access private profiles, authenticated content, or data behind login walls
- Does **not** store or share results beyond the local database

**Use responsibly.** Depending on your jurisdiction, OSINT activities may be subject to legal restrictions. The authors assume no liability for misuse.

---

## Lens Agent (Bonus Module)

A standalone **Google Lens visual analysis agent** lives in `lens_agent/` — completely independent from the OSINT pipeline, no Docker required.

### What it does

Give it any public image URL and it returns a structured breakdown: what the object is, its category, key attributes, 3–5 visually similar matches, and a confidence level — all powered by Google Lens + Gemini 2.5 Flash.

### Setup

```bash
cd lens_agent
pip install -r requirements.txt
# installs: google-adk, GoogleLens
```

You also need a free **Gemini API key** from [aistudio.google.com](https://aistudio.google.com):

```bash
export GOOGLE_API_KEY=your-key-here
```

### Run it

```bash
# One-shot
python agent.py --url "https://example.com/image.jpg"

# Interactive mode
python agent.py
```

### Use in your own code

```python
from lens_agent.agent import lens_agent

response = lens_agent.run("Analyze this image: https://example.com/photo.jpg")
print(response)
```

---

## Contributing

Contributions are welcome! Priority areas:

- New connectors (LinkedIn public profiles, Twitter/X, Reddit)
- Identity resolution improvements (better clustering for common names)
- Neo4j graph query optimizations
- Frontend UX improvements

Please open an issue before submitting large PRs.

---

## License

MIT License — see [LICENSE](./LICENSE).

---

## Acknowledgements

- [Sherlock Project](https://github.com/sherlock-project/sherlock) — username search engine
- [Have I Been Pwned](https://haveibeenpwned.com) — breach intelligence
- [LangChain](https://langchain.com) — AI agent orchestration
- [Neo4j](https://neo4j.com) — graph database
- [sentence-transformers](https://sbert.net) — semantic text embeddings
