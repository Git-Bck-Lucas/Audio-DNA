from backend.db.database import SessionLocal
from backend.rag.embed import embed_text
from backend.db.repository import search_similar_chunks

# Gelabeltes Set: (Frage, charakteristischer Ausschnitt des richtigen Chunks).
# Die Ausschnitte sind gegen den Korpus verifiziert (jeweils in 1-2 Chunks), damit ein
# recall=0 wirklich ein Retrieval-Fehler ist und nicht ein kaputtes Label.
EVAL_CASES: list[tuple[str, str]] = [
    (
        "Which personality trait most reliably predicts a preference for sophisticated, complex music like classical and jazz?",
        "strongest and most replicated",  # Chunk: Openness -> Sophisticated ist der staerkste Effekt
    ),
    (
        "What is the average correlation between personality traits and musical style preferences across all studies?",
        "0.058",  # Schaefer-Chunk: Gesamt-Mittel r = 0.058, near-zero
    ),
    (
        "Which Big Five traits show no consistent relationship with music preferences?",
        "No consistent relationship",  # Non-Significant-Traits-Chunk
    ),
    (
        "How does listening to intense music like heavy metal relate to physiological arousal?",
        "heavy metal fans",  # Rentfrow-Chunk zu Arousal
    ),
    (
        "What functions does music listening serve, such as mood regulation and identity expression?",
        "mood regulation",  # Chunk zu den Funktionen des Musikhoerens
    ),
    (
        "Do music preferences reveal something about a person's unconscious or inner personality?",
        "window into the unconscious",  # Cattell/Rentfrow-Chunk
    ),
]


def recall_at_k(db, cases: list[tuple[str, str]], k: int) -> float:
    hits = 0
    for query, expected in cases:
        query_vec = embed_text(query)
        results = search_similar_chunks(db, query_vec, top_k=k)  # Liste von (chunk, score)
        # Treffer, wenn der erwartete Ausschnitt im Text irgendeines der k Chunks vorkommt
        found = any(expected.lower() in chunk.text.lower() for chunk, _ in results)
        if found:
            hits += 1
    return hits / len(cases)


if __name__ == "__main__":
    with SessionLocal() as db:
        for k in (1, 3, 5):
            print(f"recall@{k} = {recall_at_k(db, EVAL_CASES, k):.2f}")
