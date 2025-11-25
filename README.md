# Audio-DNA

Audio DNA - Musik - basierte Persönlichkeitsanalyse als Service 

Problem: Unternehmen suchen nach innovativen Wegen für Team-Building und Persönlichkeitsassessments --> b2b SAAS 

1. Mitarbeiter verbinden anonym ihre Spofify/Apple Music 
2. AI analysiert Musikgeschmack --> Persönlichkeitsanalyse (Big Five)
3. Generiert Team-Kompatibiläts-Reports 
4. Schlägt gemeinsame Playlisten für bessere Zusammenarbeit vor 
5. Identifiziert "Cultural Fit" bei Bewerbern 
6. Automatierte Team Kompatibilitätsanalysen basierend auf Musikgeschmack

Tech Implementation: Complex RAG (Musikdaten + Psychologie Papers), Multi-tenant FastAPI Backend, Async Processing, Docker + K8s für Enterprise Deployment,
sophisticated monitoring, CI/CD Pipeline, MCP Server für Integration

Wissenschaftliche Basis: Forscher haben mit 5.808 Spotify-Nutzern und 17,6 Millionen Songs bewiesen, dass die Big Five Persönlichkeitsmerkmale durch Musikpräferenzen mit "moderater bis hoher Genauigkeit" vorhergesagt werden können --> https://www.researchgate.net/publication/342854806_Just_the_Way_You_Are_Linking_Music_Listening_on_Spotify_and_Personality

Vorteil: Studien zeigen, dass Unternehmen mit regelmäßigen Persönlichkeitsassessments 15% mehr Engagement und 25% weniger Turnover haben -->
https://www.predictiveindex.com/blog/personality-tests-for-team-building/

Echtes Verhalten statt Selbsteinschätzung 

Skalierbarkeit: API-Integration macht es sehr einfach für Unternehmen

Datenschutz first --> DSGVO --> Bezug zur Masterarbeit 

Timing: HR-Tech boomt, Spotify hat 600 Millionen Nutzer, Remote Work macht Team Building wichtiger denn je 

Wichtige Befehle:

Virtuelle Umgebung starten: venv/bin/activate

Rest API starten: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

Rest API im Browser öffnen: http://127.0.0.1:8000/docs

Zum Spotify API login Endpoint gelangen: GET /api/v1/spotify/login --> http://127.0.0.1:8000/api/v1/spotify/login
