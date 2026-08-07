"""Query-Vektoren pro Big-Five-Trait fürs trait-orientierte Retrieval.

Anders als dimension_queries.py (gekeyed nach MUSIC-Musik-Dimensionen) fragt dieses Modul
direkt nach den Persönlichkeits-Traits, die hinten im Ergebnis stehen. Grund: für C/A/N gibt
es keine saubere Musik-Dimension, an der sie hängen — also groundet man jeden Trait direkt.

Formulierungs-Prinzip (symmetrischer Encoder): englischer Fließtext im Stil der Ziel-Passagen.
Die Queries sind gegen eval_retrieval.py getunt — mit diesen Formulierungen zieht jeder Trait
im ungefilterten Pfad einen validen Beleg (any-of recall@5 = 1.00, Stand 6 Paper / 514 Chunks).
Wer sie ändert, sollte das Eval erneut laufen lassen. Keys müssen exakt den TRAIT_VOCAB-Keys
entsprechen, sonst greift der optionale trait-Filter nicht.
"""

from backend.rag.embed import embed_texts

BIG_FIVE_TRAIT_QUERIES: dict[str, str] = {
    "Openness": (
        "Openness to experience is the strongest and most consistently replicated personality "
        "predictor of music preferences, relating to reflective, complex, and sophisticated "
        "music such as classical, jazz, blues, and folk."
    ),
    "Extraversion": (
        "Extraversion is related to a preference for upbeat, energetic, and rhythmic music with "
        "a major mode, high tones, and positive valence, such as pop, dance, rap, and soul."
    ),
    "Agreeableness": (
        "Agreeableness is weakly connected only to upbeat and conventional music such as pop, "
        "country, and religious music; in streaming behavior studies agreeableness was predicted "
        "with low accuracy."
    ),
    "Conscientiousness": (
        "Conscientiousness is only weakly related to music preferences; behavioral listening "
        "patterns such as repetition and low diversity add modest predictive value, and "
        "conscientiousness is the second most strongly related trait after openness."
    ),
    "Neuroticism": (
        "Neuroticism is only weakly and inconsistently correlated with music preferences; "
        "individual studies found links to intense or mellow music but these effects did not "
        "replicate."
    ),
}

_traits = list(BIG_FIVE_TRAIT_QUERIES)
_query_vectors = embed_texts([BIG_FIVE_TRAIT_QUERIES[t] for t in _traits])
BIG_FIVE_TRAIT_QUERY_VECTORS: dict[str, list[float]] = dict(zip(_traits, _query_vectors))


def big_five_query(trait: str) -> list[float]:
    return BIG_FIVE_TRAIT_QUERY_VECTORS[trait]
