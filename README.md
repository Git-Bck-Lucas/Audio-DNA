# Audio DNA

**AI-powered Big Five personality analysis from Spotify listening data, grounded in music-psychology research via RAG.**

## 🎯 Problem & Solution

Self-reported personality questionnaires are tedious and easy to game. Audio DNA derives Big Five (OCEAN) personality signals from authentic Spotify listening behavior, and grounds every score in peer-reviewed music-psychology literature so the output is calibrated and honest rather than a black-box guess.

**Use cases:**
- Playful, shareable "musical personality" profiles
- Team building and compatibility exploration
- A worked example of production-grade, research-grounded LLM engineering

## 🔬 Scientific Foundation

The RAG corpus is built from six peer-reviewed sources:

- **Rentfrow & Gosling (2003)** – STOMP: genre preferences correlate with personality
- **Rentfrow, Goldberg & Levitin (2011)** – the MUSIC five-factor model (Mellow, Unpretentious, Sophisticated, Intense, Contemporary)
- **Langmeyer et al. (2012)** – personality × music-preference correlations (German sample)
- **Schäfer & Mehlhorn (2017)** – meta-analysis; average correlation is near-zero (r ≈ 0.058), which anchors the calibration
- **Anderson et al. (2021)** – Big Five predicted from real Spotify streaming behavior (5,808 users, 17.6M songs)
- **Sust et al. (2023)** – ML prediction of personality from naturalistic listening (audio + lyrics)

Key honest finding baked into the product: **only Openness is reliably predictable from music**; Conscientiousness, Agreeableness and Neuroticism are near-zero at the meta-analytic level. The app reflects this instead of faking confident scores.

## ✨ Features

- **Spotify OAuth** integration
- **Feature extraction**: genre clustering (Agglomerative), diversity/entropy metrics, content features (song length, explicit ratio, age) and listening-behavior metrics (frequency, repeat ratio)
- **RAG grounding** over the six papers using **PostgreSQL + pgvector**; trait-oriented retrieval evaluated with **recall@k** (`backend/rag/eval_retrieval.py`)
- **Calibrated Big Five** output: per-trait `score`, `confidence` (high / medium / low) and `reasoning` that cites the retrieved literature
- **Two analysis modes**:
  - `science` – strictly literature-grounded; weakly-predictable traits stay near the neutral midpoint with low confidence
  - `lucas` – a playful "armchair psychologist" mode that applies bolder, clearly-flagged heuristics
- **Claude Opus 4.8** (`claude-opus-4-8`) via structured outputs (`messages.parse`)
- **API cost tracking** (~$0.05 / analysis)

**Planned:**
- Frontend (Big Five visualization, RAG-grounding shown to the user, science/fun toggle)
- Observability (Langfuse tracing, LLM-as-a-judge evals)
- Security hardening (see Privacy) and rate limiting
- Prompt caching of the (user-independent) grounding context

## 🏗️ Tech Stack

- **Backend**: FastAPI, Pydantic, Python 3.10
- **Data / RAG**: PostgreSQL + pgvector, SQLAlchemy, Alembic, Sentence Transformers (all-MiniLM-L6-v2), scikit-learn
- **AI**: Anthropic Claude Opus 4.8 (structured outputs)
- **Infra**: Docker Compose, Caddy (automatic HTTPS), GitHub Actions CI/CD — deployed at `api.lucas-beck.de`
- **APIs**: Spotify Web API

## 🚀 Quick Start

```bash
# Setup
git clone https://github.com/Git-Bck-Lucas/Audio-DNA.git
cd audio-dna
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your Spotify + Anthropic API keys and Postgres credentials

# Database (Postgres + pgvector via Docker), migrations, and RAG ingestion
docker compose up -d db
alembic -c backend/alembic.ini upgrade head
python -m backend.rag.ingest

# Run the API
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Or run the full stack (API + db) with `docker compose up`.

**Access:**
- API Docs: http://127.0.0.1:8000/docs
- Spotify Login: http://127.0.0.1:8000/api/v1/spotify/login

## 📡 API Endpoints

```
GET  /api/v1/spotify/login                          # Initiate OAuth
GET  /callback                                      # OAuth callback
GET  /api/v1/analysis/get_personality?mode=science  # Analyze personality (mode: science | lucas)
```

## 🧪 RAG & Evaluation

The retrieval pipeline and its evaluation are documented in [`backend/rag/README.md`](backend/rag/README.md):
- Document loading, chunking, boilerplate filtering, embedding and pgvector storage
- Trait-oriented retrieval (one query per Big Five trait) that grounds each score
- `recall@k` evaluation against a verified, labeled set (`backend/rag/eval_retrieval.py`)

## 🗺️ Roadmap

Following the [AI Engineer Roadmap 2026](https://roadmap.sh/ai-engineer):

- [x] FastAPI + Pydantic
- [x] LLM integration (Claude API, structured outputs)
- [x] ML feature engineering (clustering, diversity metrics)
- [x] PostgreSQL + Alembic
- [x] Docker containerization
- [x] RAG over psychology papers (pgvector) + retrieval evaluation
- [x] Production deployment (Caddy HTTPS, GitHub Actions)
- [~] Testing & logging
- [ ] Observability (Langfuse, traces, LLM-as-a-judge)
- [ ] Frontend
- [ ] Team analysis features

## 🔒 Privacy & Security

- Spotify access/refresh tokens and analysis results are **stored in PostgreSQL** (not anonymous, not ephemeral).
- Personality data is sensitive and treated as such.
- Security hardening is in progress: OAuth `state`/CSRF, removing the access token from query parameters, token encryption at rest, CORS restriction, and rate limiting against LLM-cost abuse.

## 📝 License

TBD.
