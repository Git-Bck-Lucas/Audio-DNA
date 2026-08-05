"""Query-Vektor-Strategien für das Retrieval pro MUSIC-Dimension.

Der Retrieval-Zweck ist NICHT "finde Chunks, in denen das Wort 'Jazz' vorkommt", sondern
"finde die Passagen der Paper, die etwas über diese Musik-Dimension und ihren Zusammenhang
mit Persönlichkeit aussagen". Welcher Query-Vektor das am schärfsten trifft, hängt stark
davon ab, wie gut er zur *Form* der Zieltexte passt.

Warum der bisherige Centroid unscharf ist (deine Beobachtung bestätigt):
all-MiniLM-L6-v2 ist ein SYMMETRISCHER Satz-Encoder (primär auf Englisch trainiert). Query
und Zielpassage laufen durch dasselbe Modell, ohne "query:"/"passage:"-Präfixe. Faustregel:
Je ähnlicher der Query in Sprache, Länge und Stil zu den Zielpassagen ist, desto schärfer
die Cosinus-Similarity. Ein Mittelwert aus 15-22 kurzen Genre-Wörtern (Centroid) landet an
einem Punkt, der zu keinem konkreten Fließtext-Abschnitt besonders nah ist — deshalb tauchen
für fast jede Dimension dieselben generischen Methodik-Chunks auf.

Dieses Modul stellt drei Strategien nebeneinander, damit du den Effekt isolieren kannst.
Vergleichs-Skript: backend/rag/compare_query_strategies.py
"""

from backend.rag.embed import embed_text, embed_texts
from backend.rag.genre_mapping import DIMENSION_STEM_EMBEDDINGS, MUSIC_DIMENSIONS


def centroid_query(dim: str) -> list[float]:
    """Strategie A (bestehend): Mittelwert aller Stem-Embeddings der Dimension.

    Schwäche: mittelt stilistisch weit gestreute Genres (z.B. Sophisticated: "classical",
    "idm", "world", "ambient") zu einem unspezifischen Punkt — dem eigentlichen Auslöser
    der unscharfen Treffer.
    """
    return DIMENSION_STEM_EMBEDDINGS[dim].mean(axis=0).tolist()


def description_query(dim: str) -> list[float]:
    """Strategie B (wie von dir gewünscht): Embedding der kurzen `description`.

    Idee: ein gezielter Kurztext trifft die Dimension besser als ein gemittelter Stem-Wolke.

    ACHTUNG, Confound: die `description`-Texte sind DEUTSCH, der Korpus (die Paper) ist
    ENGLISCH. all-MiniLM-L6-v2 ist überwiegend englisch trainiert. Falls B schlechter
    abschneidet als erwartet, lässt sich nicht sauber sagen, ob das an "Beschreibung statt
    Centroid" oder am Sprach-Mismatch liegt. Bewusst so belassen, weil genau das dein
    gewünschter Vergleich war — Strategie C isoliert die Sprach-Frage.
    """
    return embed_text(MUSIC_DIMENSIONS[dim]["description"])


# Strategie C (Ergänzung): englischer FLIESSTEXT-Query, der explizit den
# Persönlichkeit×Dimension-Zusammenhang benennt — also in Sprache UND Stil nah an den
# Zielpassagen der Paper. Formuliert in Anlehnung an die Kernaussagen der Meta-Analyse
# (Schäfer & Mehlhorn 2017: Openness→Sophisticated ist der stärkste Effekt, Extraversion
# →Contemporary, Sensation Seeking→Intense usw.). Die Formulierungen sind bewusst
# handgeschrieben und dürfen getunt werden — sie sind der Hebel, an dem du drehst.
#
# Hinweis: C ändert gegenüber B ZWEI Dinge gleichzeitig (Sprache DE→EN + Framing
# Stichwort→Persönlichkeits-Aussage). Wenn du die Sprache isoliert testen willst, embedde
# zusätzlich eine reine englische Übersetzung der `description` — hier weggelassen, um den
# Vergleich auf drei aussagekräftige Strategien zu begrenzen.
# (2) Geschärfte Queries: jede führt mit den EIGENEN Adjektiven + Genres + dem spezifischen
# Trait-Link, statt dem geteilten Muster "preference for ... music ... personality traits".
# Weniger gemeinsames Vokabular => weniger Kollision auf denselben generischen Magnet-Chunk.
# Bei Mellow bewusst KEIN starker Trait-Claim (die Literatur findet dort keinen verlässlichen
# Zusammenhang) — stattdessen dimensions-eigene Deskriptoren.
DIMENSION_TRAIT_QUERIES: dict[str, str] = {
    "Sophisticated": (
        "Openness to experience correlates with a preference for sophisticated, reflective, "
        "and complex music such as classical, jazz, opera, and world music."
    ),
    "Intense": (
        "Sensation seeking and openness correlate with a preference for intense, loud, and "
        "rebellious music such as rock, punk, heavy metal, and alternative."
    ),
    "Contemporary": (
        "Extraversion correlates with a preference for energetic, rhythmic, and upbeat "
        "contemporary music such as rap, hip-hop, dance, and electronica."
    ),
    "Mellow": (
        "A preference for mellow, romantic, and relaxing music such as soft rock, R&B, and "
        "smooth jazz reflects emotional and aesthetic sensitivity."
    ),
    "Unpretentious": (
        "Extraversion correlates with a preference for unpretentious, sincere, and acoustic "
        "music such as country, folk, and singer-songwriter styles."
    ),
}

_dims = list(DIMENSION_TRAIT_QUERIES) # gibt die 5 dimensionsnamen als liste
_query_vectors = embed_texts([DIMENSION_TRAIT_QUERIES[d] for d in _dims])
DIMENSION_TRAIT_QUERY_VECTORS: dict[str, list[float]] = dict(zip(_dims, _query_vectors)) # fügt namen und vektoren paarweise zu einem dict zusammen


def trait_query(dim: str) -> list[float]:
    """Strategie C: englischer Fließtext-Query im Stil der Zielpassagen (siehe oben)."""
    return DIMENSION_TRAIT_QUERY_VECTORS[dim]
