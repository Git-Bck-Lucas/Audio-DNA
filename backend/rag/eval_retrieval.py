from backend.db.database import SessionLocal
from backend.rag.embed import embed_text
from backend.rag.trait_queries import big_five_query
from backend.db.repository import search_similar_chunks

# ===========================================================================
# Teil 1 (Legacy): Roh-Retrieval-Sanity-Check
# ---------------------------------------------------------------------------
# Rohe Frage embedden, ungefiltert suchen. Misst NICHT den Produktionspfad,
# sondern nur, ob der Korpus die Antwort überhaupt findbar enthält.
# Die Ausschnitte sind gegen den Korpus verifiziert (jeweils in 1-2 Chunks),
# damit ein recall=0 wirklich ein Retrieval-Fehler ist und kein kaputtes Label.
# ===========================================================================
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


# ===========================================================================
# Teil 2 (primär): Trait-orientiertes Eval — spiegelt den Produktionspfad
# ---------------------------------------------------------------------------
# Nutzt dieselbe big_five_query() pro Trait wie retrieval_service. Frage-Semantik:
# "zieht die Trait-Query IRGENDEINEN korrekten Beleg für diesen Trait?" — deshalb
# "any-of": pro Trait mehrere verifizierte Belegstellen, ein Treffer genügt.
# (Single-gold-recall unterschätzt, weil pro Trait mehrere valide Chunks existieren.)
#
# Baseline (6 Paper / 514 Chunks), UNGEFILTERT:  recall@1 = 0.80, recall@5 = 1.00
# Gefiltert (trait-Tag) ist schlechter (recall@5 = 0.80): valide, aber ungetaggte
# Chunks (v.a. der Neuroticism-Beleg bei Schaefer, dessen Überschrift beim Chunking
# abgetrennt wurde) fallen raus. => Produktions-Trait-Pfad UNGEFILTERT fahren.
# Den Filter zurückholen, sobald Tagging/feineres Chunking verbessert ist.
#
# Jeder Ausschnitt ist gegen den Korpus verifiziert (1-2 Chunks), Quelle im Kommentar.
# ===========================================================================
TRAIT_EVAL_CASES: dict[str, list[str]] = {
    "Openness": [
        "strongest and most replicated",              # Schaefer: staerkster/replizierter Effekt
        "most strongly related to music listening",   # Sust: Openness r=.25, staerkste Domain
    ],
    "Extraversion": [
        "high tones, and positive valence",           # Sust: E -> major mode / positive valence (Audio)
        "Extraversion → Cont",                         # Schaefer: Extraversion -> Contemporary
    ],
    "Agreeableness": [
        "only to U&C",                                 # Langmeyer: A nur mit Upbeat & Conventional
        ".26 for Agreeableness and .37 for Emotional", # Sust/Anderson: Streaming-Vorhersage A=.26
        "connections to Agreeable",                    # Langmeyer: A-Verbindungen vs. andere Studien
    ],
    "Conscientiousness": [
        "followed by Conscientiousness",               # Sust: nach Openness (r=.25) folgt C (r=.13)
        "second most strongly r",                      # Sust: C zweitstaerkste Domain (Verhalten/ML)
    ],
    "Neuroticism": [
        "links to Intense or Mellow music",            # Schaefer: N -> Intense/Mellow, repliziert nicht
        "positive emotion words in lyric",             # Sust: Emotional Stability -> Lyrics
        "weakly correl",                               # Langmeyer: N weakly correlated
    ],
}


def trait_recall_at_k(
    db,
    cases: dict[str, list[str]],
    k: int,
    use_filter: bool = False,
) -> float:
    """Any-of recall: pro Trait ein Treffer genuegt, wenn einer der verifizierten
    Ausschnitte in den top_k Chunks der Trait-Query vorkommt.

    use_filter=False entspricht dem empfohlenen Produktions-Trait-Pfad (siehe oben).
    """
    hits = 0
    for trait, snippets in cases.items():
        query_vec = big_five_query(trait)
        results = search_similar_chunks(db, query_vec, top_k=k, trait=trait if use_filter else None)
        found = any(
            any(snippet.lower() in chunk.text.lower() for snippet in snippets)
            for chunk, _ in results
        )
        if found:
            hits += 1
    return hits / len(cases)


if __name__ == "__main__":
    with SessionLocal() as db:
        print("== Teil 1: Roh-Retrieval-Sanity-Check ==")
        for k in (1, 3, 5):
            print(f"recall@{k} = {recall_at_k(db, EVAL_CASES, k):.2f}")

        print("\n== Teil 2: Trait-Eval (Produktionspfad, any-of) ==")
        for use_filter in (False, True):
            print(f"-- filter={use_filter} --")
            for k in (1, 3, 5):
                print(f"recall@{k} = {trait_recall_at_k(db, TRAIT_EVAL_CASES, k, use_filter):.2f}")
