# Audio DNA

**AI-powered personality analysis through music listening behavior**

## 🎯 Problem & Solution

HR teams struggle with engaging personality assessments. Audio DNA analyzes Spotify listening data to generate scientifically-backed Big Five personality profiles - replacing self-reported surveys with authentic behavioral data.

**Use Cases:**
- Team compatibility analysis
- Cultural fit assessment for hiring
- Data-driven team building
- Personalized collaboration strategies

## 🔬 Scientific Foundation

Based on peer-reviewed research:
- [Nave et al. (2020)](https://www.researchgate.net/publication/342854806) - Validated Big Five prediction through Spotify data (5,808 users, 17.6M songs)
- Rentfrow & Gosling (2003) - Genre preferences correlate with personality traits
- [Predictive Index Study](https://www.predictiveindex.com/blog/personality-tests-for-team-building/) - Regular assessments increase engagement by 15%, reduce turnover by 25%

## ✨ Features

**Current (v0.1.0):**
- Spotify OAuth integration
- ML-based feature extraction (genre clustering, diversity metrics)
- AI personality analysis via Claude Opus 4.5
- Big Five scores with detailed reasoning
- API cost tracking (~€0.015/analysis)

**Planned:**
- Team compatibility reports
- Multi-user analysis
- Cultural fit scoring
- Collaborative playlist generation

## 🏗️ Tech Stack

- **Backend**: FastAPI, Python 3.10
- **ML**: Sentence Transformers, Scikit-learn (Agglomerative Clustering)
- **AI**: Anthropic Claude Opus 4.5
- **APIs**: Spotify Web API
- **Future**: PostgreSQL, Docker, Kubernetes, CI/CD

## 🚀 Quick Start
```bash
# Setup
git clone https://github.com/Git-Bck-Lucas/Audio-DNA.git
cd audio-dna
python3.10 -m venv venv
source venv/bin/activate  # or: . venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your Spotify + Anthropic API keys

# Run
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Access:**
- API Docs: http://127.0.0.1:8000/docs
- Spotify Login: http://127.0.0.1:8000/api/v1/spotify/login

## 📡 API Endpoints
```
GET  /api/v1/spotify/login              # Initiate OAuth
GET  /callback                           # OAuth callback
GET  /api/v1/analysis/get_personality    # Analyze personality
```

## 🗺️ Roadmap

Following [AI Engineer Roadmap 2026](https://roadmap.sh/ai-engineer):

- [x] FastAPI + Pydantic
- [x] LLM Integration (Claude API)
- [x] ML Feature Engineering
- [ ] Testing & Logging
- [ ] PostgreSQL + Alembic
- [ ] Docker Containerization
- [ ] Production Deployment
- [ ] RAG for Psychology Papers
- [ ] Team Analysis Features

## 🔒 Privacy & Compliance

- GDPR-compliant data handling
- Anonymous processing
- No persistent storage (MVP)
- User consent flows

## 📊 Market Context

- **Target**: B2B SaaS for HR teams
- **Timing**: Remote work increases need for team cohesion tools
- **Scale**: 600M+ Spotify users globally
- **Advantage**: Behavioral data > self-reported surveys

## 📝 License
