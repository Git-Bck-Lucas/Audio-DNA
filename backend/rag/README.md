# RAG-Pipeline — Audio DNA

Diese Dokumentation erklärt die komplette Retrieval-Pipeline unter `backend/rag/`: was jedes
Modul tut, **warum** es so gebaut ist, welche Konzepte dahinterstehen, und was zuletzt geändert
wurde. Zielgruppe: ich selbst in drei Monaten.

---

## 1. Wozu das Ganze? (Big Picture)

Audio DNA leitet aus Spotify-Hördaten ein Big-Five-Persönlichkeitsprofil ab. Die Zuordnung
„Musik → Persönlichkeit" ist wissenschaftlich heikel (die Effekte sind klein). Statt den LLM
frei raten zu lassen, soll er sich auf **echte Forschungsliteratur** stützen. Genau das ist der
Job dieser RAG-Pipeline:

> **RAG = Retrieval-Augmented Generation.** Man sucht (retrieval) relevante Textstellen aus
> einer Wissensbasis und gibt sie dem LLM als Kontext mit, bevor er antwortet (generation).
> Statt „was weiß das Modell zufällig" → „was steht in *diesen* Papern".

Die Wissensbasis sind **6 Paper** zu Musikgeschmack & Persönlichkeit (`documents/`): Rentfrow &
Gosling (2003), Rentfrow/Goldberg/Levitin (2011), Langmeyer (2012), Schäfer & Mehlhorn (2017),
Anderson (2021, Spotify-Streaming-Daten) und Sust (2023). Sie werden in kleine Stücke („Chunks")
zerlegt, in Vektoren übersetzt („Embeddings") und in Postgres gespeichert. Bei einer Anfrage
übersetzen wir auch die Frage in einen Vektor und suchen die ähnlichsten Chunks.

**Zwei getrennte Aufgaben in diesem Ordner, nicht verwechseln:**

| Aufgabe | Modul | Input | Output |
|---|---|---|---|
| Genre → MUSIC-Dimension zuordnen | `genre_mapping.py` | ein Spotify-Genre-String (`"synthpop"`) | eine von 5 Dimensionen |
| Literatur durchsuchbar machen | `load_documents`, `chunking`, `embed`, `chunk_tagging`, `ingest` | PDF/MD-Paper | getaggte, embeddete Chunks in der DB |
| Passende Chunks finden | `dimension_queries`, `repository.search_similar_chunks` | eine Dimension | Top-k Belegstellen |

Das **MUSIC-Modell** (Rentfrow, Goldberg & Levitin 2011) sind 5 Musik-Präferenz-Dimensionen:
**M**ellow, **U**npretentious, **S**ophisticated, **I**ntense, **C**ontemporary.

> **Wichtige Weiterentwicklung (siehe Abschnitt „Trait-orientiertes Retrieval"):** Inzwischen gibt
> es zwei Retrieval-Ansätze. Der dimensions-orientierte Pfad (oben) war der erste. Der Produktions-
> pfad ist jetzt **trait-orientiert** (eine Query pro Big-Five-Trait), weil der Output an den 5
> Traits hängt, nicht an den 5 Musik-Dimensionen — und für C/A/N gibt es keine passende Dimension.
> Der Dimensions-Pfad ist aus dem Grounding entfernt (gemessen: identische Scores, ~2x Kontext).

---

## 2. Grundkonzepte (einmal sauber erklärt)

### Embedding
Ein neuronales Modell (`all-MiniLM-L6-v2`) übersetzt einen Text in einen Vektor aus 384 Zahlen.
Ähnliche Bedeutung → ähnliche Vektoren. So wird „Bedeutung" rechenbar.

### Cosinus-Ähnlichkeit / -Distanz
Maß dafür, wie ähnlich sich zwei Vektoren zeigen (Winkel zwischen ihnen).
- **Similarity** 1.0 = identische Richtung, 0.0 = unabhängig, -1.0 = gegensätzlich.
- **Distanz** = `1 - similarity`. pgvector rechnet in Distanz; wir rechnen für die Ausgabe
  zurück auf Similarity, weil „0.78 ähnlich" intuitiver ist als „0.22 Distanz".

### Symmetrischer Encoder (wichtig!)
`all-MiniLM-L6-v2` embeddet Frage und Zieltext mit **demselben** Modell, ohne Spezial-Präfixe.
Konsequenz: **Je ähnlicher die Frage in Sprache, Länge und Stil zum Zieltext ist, desto besser
der Treffer.** Eine deutsche 3-Wort-Frage passt schlecht auf englische Fließtext-Absätze — auch
wenn sie inhaltlich gemeint ist. Dieses Prinzip erklärt fast alle unserer Retrieval-Ergebnisse.
(Das Modell ist zudem überwiegend **englisch** trainiert → deutsche Queries sind doppelt im
Nachteil.)

---

## 3. Die Pipeline Schritt für Schritt

### 3.1 `load_documents.py` — Rohtext laden
`load_documents(path)` liest ein `.pdf` (via PyMuPDF/`fitz`) oder `.md` und gibt reinen Text
zurück. Unverändert, simpel.

### 3.2 `chunking.py` — in Stücke schneiden + Müll filtern

**Warum chunken?** Ein ganzes Paper ist als ein Vektor zu grob. Man zerlegt es in ~1000-Zeichen-
Stücke mit 200 Zeichen Überlappung (damit ein am Rand zerschnittener Gedanke nicht verloren geht).

**Was zuletzt geändert wurde — Boilerplate-Filter.** PDFs von Fachzeitschriften enthalten auf
*jeder Seite* Kopf-/Fußzeilen (Journal-Name, Autorennamen, Copyright, Download-URLs). Ungefiltert
landen die als Rauschen in den Chunks und verschlechtern die Embeddings. Zwei Mechanismen:

1. **`_BOILERPLATE_PATTERNS`** — kuratierte Regex-Liste für *bekannte, konkrete* Muster
   (APA-Copyright-Zeile, DOI-Präfix, „Downloaded from http…"). Gut für Muster, die in vielen
   Papern gleich aussehen.
2. **`_strip_repeated_lines`** — der eigentlich clevere Teil: Kopf-/Fußzeilen sind pro Paper
   *unterschiedlich* (mal „RENTFROW AND GOSLING", mal „A. Langmeyer et al."), aber sie
   **wiederholen sich wörtlich** auf jeder Seite. Also: zähle alle Zeilen (`Counter`), wirf die
   raus, die ≥3× vorkommen und kurz genug für eine Kopfzeile sind (≤150 Zeichen). Das skaliert
   automatisch auf neue Paper, ohne dass ich für jedes neue PDF Regexes pflegen muss.

**`is_boilerplate(chunk)`** ist ein Sicherheitsnetz auf Chunk-Ebene (fängt zu kurze Rest-Chunks
< 200 Zeichen ab). *Vorher hatte diese Funktion zwei Bugs* (`chunk < MIN_LENGTH` verglich String
mit Int; `chunk in _PATTERNS` prüfte Gleichheit statt Regex-Match) — beide gefixt und die Funktion
wird jetzt tatsächlich aufgerufen.

> **Ehrliche Grenze:** Der Sentence-Split `text.split(". ")` ist fragil (bricht bei „e.g.",
> „et al.", „r = .15"). Für diesen kleinen Korpus okay, aber der offensichtlichste nächste
> Verbesserungspunkt.

### 3.3 `embed.py` — Text → Vektor
- `embed_text(text)` — ein String → ein 384-dim-Vektor.
- **`embed_texts(texts)`** (neu) — eine **Liste** von Strings → Liste von Vektoren, in *einem*
  Modell-Aufruf. `SentenceTransformer.encode()` verarbeitet Batches intern viel effizienter als
  N Einzelaufrufe in einer Schleife. Wird beim Stem-Embedding und beim Batch-Genre-Mapping genutzt.

### 3.4 `chunk_tagging.py` (neu) — Chunks mit Metadaten versehen

**Zweck:** Jeden Chunk mit den MUSIC-Dimensionen und Big-Five-Traits taggen, die er *behandelt*.
Diese Tags ermöglichen später gefiltertes Retrieval (siehe 3.7).

**Warum lexikalisch (Stichwortsuche) statt per Embedding?** Beim Query-Vergleich haben wir
gesehen, dass Embeddings über diesen kleinen Korpus auf generische Chunks kollabieren. Fürs
*Tagging* will ich das Gegenteil: präzise, deterministisch, nachvollziehbar. Ein Chunk bekommt
das Tag `Intense`, wenn er charakteristisches Vokabular enthält (`"intense"`, `"rock"`, `"punk"`,
`"heavy metal"`…). `DIMENSION_VOCAB` und `TRAIT_VOCAB` sind kuratierte Wortlisten; Matching per
**Wortgrenzen-Regex** (`\brock\b`), damit `"rock"` nicht in `"rockville"` matcht.

Ein Chunk kann **mehrere** Tags tragen (die Meta-Analyse-Zusammenfassung nennt alle 5 Dimensionen)
oder **keins** (reine Methodik-Absätze). `tag_chunk(text)` gibt `(dimensions, traits)` zurück.

**Ergebnis an echten Daten:** 75% der Chunks bekommen *kein* Dimension-Tag — das sind genau die
generischen Methodik-/Boilerplate-Absätze, die wir aus der dimensionsspezifischen Suche draußen
haben wollen. (Gemessen bei 328 Chunks; nach zwei weiteren Papern hat der Korpus jetzt **514 Chunks**.)

### 3.5 `ingest.py` — alles zusammenführen
Orchestriert: für jedes Dokument → laden → chunken → für jeden Chunk embedden **und taggen** →
`Chunks`-Objekt bauen → `replace_chunks` (leert die Tabelle und schreibt alles neu, atomar).
Der neue Teil ist der `tag_chunk`-Aufruf, der `dimensions` und `traits` befüllt.

### 3.6 Datenbank: `models.py` + Migration

Die `Chunks`-Tabelle hat neu zwei Spalten:
```python
dimensions = Column(ARRAY(String), nullable=False, default=list)
traits     = Column(ARRAY(String), nullable=False, default=list)
```
`ARRAY(String)` ist ein natives Postgres-Array — ein Chunk kann mehrere Dimensionen tragen, ohne
Extra-Tabelle. Filterbar per `wert = ANY(spalte)`.

Die **Alembic-Migration** `c2d4e6f80a1b_add_chunk_metadata.py` fügt die Spalten hinzu. Wichtig:
`server_default='{}'` (leeres Array) füllt die bestehenden Zeilen, damit `NOT NULL` beim
Hinzufügen nicht bricht.

> **Konzept Migration:** Der Code-`Column` beschreibt, wie die Tabelle aussehen *soll*. Damit die
> echte DB-Tabelle nachzieht, braucht es ein Migrations-Skript (`alembic upgrade`). `replace_chunks`
> löscht nur *Zeilen*, nicht *Spalten* — die Spalte muss vorher per Migration existieren.

### 3.7 `repository.py` — die Suche

`search_similar_chunks(db, query_vector, top_k, dimension=None, trait=None)`:
```python
distance = Chunks.embedding.cosine_distance(query_vector)
query = db.query(Chunks, distance.label("distance"))
if dimension is not None:
    query = query.filter(Chunks.dimensions.any(dimension))   # dimension = ANY(chunks.dimensions)
if trait is not None:
    query = query.filter(Chunks.traits.any(trait))
rows = query.order_by(distance).limit(top_k).all()
return [(chunk, 1.0 - distance_value) for chunk, distance_value in rows]
```

Zwei Änderungen:
1. **Gibt jetzt `(Chunk, Similarity)`-Tupel zurück** statt nur Chunks — damit ich sehe, *wie gut*
   ein Treffer ist (und Strategien vergleichen kann).
2. **Optionale Filter** `dimension`/`trait` → **Hybrid-Retrieval**.

> **Konzept Hybrid-Retrieval:** reine Vektorsuche = „semantisch am ähnlichsten". Hybrid =
> erst **hart filtern** nach Metadaten (nur Chunks mit Tag `Sophisticated`), *dann* innerhalb
> dieser Teilmenge semantisch sortieren. Kombiniert Präzision (Filter) mit Semantik (Vektor).

### 3.8 `dimension_queries.py` (neu) — wie formuliere ich die Frage?

Der Knackpunkt: Mit *welchem* Vektor suche ich pro Dimension? Drei Strategien zum Vergleich:

- **A `centroid_query`** — Mittelwert aller Genre-Stem-Embeddings der Dimension. *Schwäche:*
  mittelt 15-22 stilistisch gestreute Genres zu einem unspezifischen Punkt.
- **B `description_query`** — Embedding der kurzen **deutschen** `description`. *Confound:*
  deutsch gegen englischen Korpus → doppelt benachteiligt (siehe symmetrischer Encoder).
- **C `trait_query`** — **englischer Fließtext-Satz**, der den Persönlichkeit×Dimension-Zusammenhang
  benennt, im Stil der Zielpassagen. `DIMENSION_TRAIT_QUERIES` hält diese Sätze.

**Zuletzt geschärft (Schritt 2):** Die C-Queries teilten sich anfangs zu viel Vokabular
(„preference for … music … personality traits"), was zu Kollisionen führte. Jetzt führt jede
Query mit ihren *eigenen* Adjektiven + Genres + dem spezifischen Trait (z.B. Intense →
„sensation seeking and openness … rock, punk, heavy metal, alternative").

### 3.9 `compare_query_strategies.py` (neu) — das Experiment
Läuft alle 5 Dimensionen × 4 Varianten (A, B, C, **C+Filter**) durch und druckt Treffer + Scores
nebeneinander. Das ist kein Produktionscode, sondern mein Messinstrument, um zu *sehen*, welche
Strategie schärfere Treffer liefert.

---

## 4. Was die Experimente ergeben haben (die Erkenntnisse)

1. **Score steigt klar A < B < C** (typisch ~0.33 → ~0.45 → ~0.75). Bestätigt das Prinzip
   des symmetrischen Encoders: Query in Sprache + Stil des Korpus = viel höhere Similarity.
2. **B (deutsche Beschreibung) ist eine Sackgasse:** höherer Score als A, aber kaum trennschärfer —
   die deutsche Query greift im englischen Korpus immer denselben zentralen Chunk. Sprach-Mismatch.
3. **C ist die richtige Richtung:** zieht inhaltstragende Befunde statt Methodik-Boilerplate.
4. **Der Filter (Hybrid) bringt den strukturellen Gewinn:** 75% Boilerplate sind ausgeschlossen;
   er hilft am meisten dort, wo der generische Chunk *nicht* dimensionsgetaggt war (Mellow,
   Sophisticated verbessern sich deutlich).
5. **Ehrliche Restgrenze = Chunking-Artefakt, kein Bug:** Die Schäfer-Zusammenfassung packt mehrere
   Korrelationen in einen großen Chunk. Der ist damit *korrekt* mit mehreren Dimensionen getaggt und
   taucht bei mehreren oben auf — er *ist* für alle relevant. Der nächste Hebel wäre feineres
   Chunking (eine Korrelation pro Chunk).

---

## 5. Wie man alles ausführt

Die DB läuft im Docker-Netz unter dem Hostnamen `db`. **Vom Host (Mac) aus** ist der nicht
auflösbar — der Port 5432 ist aber nach `localhost` gemappt. Also `DATABASE_URL` für Host-Runs
auf `localhost` überschreiben (echte Env-Var schlägt den `.env`-Wert):

```bash
# 1. DB starten
docker compose up -d db

# 2. Für Host-Runs: Credentials aus .env ziehen, Host auf localhost umbiegen
source venv/bin/activate
set -a && source .env && set +a
export DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"

# offline, damit sentence-transformers nicht bei jedem Start HuggingFace anpingt
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

# 3. Schema aktualisieren (Migration von der Repo-Wurzel mit explizitem Config-Pfad)
alembic -c backend/alembic.ini upgrade head

# 4. Paper einlesen, chunken, taggen, embedden, speichern
python -m backend.rag.ingest

# 5. Query-Strategien vergleichen
python -m backend.rag.compare_query_strategies
```

Einzelne Module haben `__main__`-Selbsttests: `python -m backend.rag.genre_mapping` (Regressions-
tests + Threshold-Sweep), `python -m backend.rag.chunk_tagging` (Tagging an Beispielen).

---

## 6. Geänderte/neue Dateien (Änderungsübersicht)

| Datei | Status | Kern der Änderung |
|---|---|---|
| `embed.py` | geändert | `embed_texts()` für Batch-Embedding ergänzt |
| `genre_mapping.py` | überarbeitet | Prosa-Anchor → Stem-Prototypen (Max-Similarity); Wortgrenzen- + Tie-Break-Fix im Keyword-Layer; `lru_cache`; Batch-Mapping; Threshold-Kalibrier-Harness |
| `chunking.py` | überarbeitet | Boilerplate-Filter (kuratierte Regexes + generischer Repeated-Line-Filter); `is_boilerplate`-Bugs gefixt und eingebunden |
| `chunk_tagging.py` | **neu** | Lexikalisches Tagging der Chunks mit Dimensionen/Traits |
| `ingest.py` | geändert | ruft `tag_chunk` auf, befüllt `dimensions`/`traits` |
| `dimension_queries.py` | **neu** | 3 Query-Strategien (Centroid / DE-Description / EN-Trait-Prosa), geschärfte Trait-Queries |
| `compare_query_strategies.py` | **neu** | Vergleichs-Experiment A/B/C/C+Filter über alle Dimensionen |
| `db/models.py` | geändert | `Chunks.dimensions`, `Chunks.traits` (ARRAY-Spalten) |
| `db/repository.py` | geändert | `search_similar_chunks`: Similarity-Score + optionale Dimension/Trait-Filter |
| `migrations/versions/c2d4e6f80a1b_*.py` | **neu** | Migration für die zwei neuen Spalten |

---

## 7. Offene nächste Schritte

- **RAG in den LLM-Prompt einbinden** (`llm_personality_service.py`): die gefundenen Belegstellen
  als Kontext ins Big-Five-Scoring geben — inkl. der zentralen Warnung aus der Literatur, dass
  Conscientiousness/Agreeableness/Neuroticism aus Musik **kaum** verlässlich vorhersagbar sind
  (r ≈ 0.058 im Schnitt). Das ist der eigentliche Mehrwert-Payoff der Pipeline.
- **Feineres Chunking** der Zusammenfassung (eine Korrelation pro Chunk) für perfekte Trennschärfe.
- **Robusteres Sentence-Splitting** in `chunking.py` (Abkürzungen, Statistik-Notation).
