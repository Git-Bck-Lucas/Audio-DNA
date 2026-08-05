import re
from collections import defaultdict
from functools import lru_cache

import numpy as np

from backend.rag.embed import embed_text, embed_texts

MUSIC_DIMENSIONS = {
    "Sophisticated": {
        "description": "komplex, intelligent, inspirierend — Klassik, Jazz, World, Avantgarde, experimentelle Elektronik",
        "keyword_stems": [
            "classical", "neoclassical", "baroque", "opera", "jazz", "fusion",
            "idm", "experimental", "avant", "drone", "post-rock",
            "ambient", "space", "world", "blues",
        ],
    },
    "Intense": {
        "description": "laut, kraftvoll, aggressiv — Rock, Punk, Metal, Hardcore",
        "keyword_stems": [
            "rock", "metal", "punk", "hardcore", "grunge",
            "industrial", "emo", "screamo", "thrash", "doom", "garage rock",
        ],
    },
    "Contemporary": {
        "description": "rhythmisch, perkussiv, elektronisch, tanzbar — Rap, Techno, House, Pop, Dance",
        "keyword_stems": [
            "techno", "house", "trance", "electro", "edm", "dnb", "drum and bass",
            "dubstep", "rap", "hip hop", "dance", "eurodance", "bounce", "electronic",
            "pop", "disco", "breakbeat", "jungle", "bass", "hardstyle", "phonk", "synthwave",
        ],
    },
    "Mellow": {
        "description": "smooth, entspannt, romantisch, ruhig — Soft Rock, Dream Pop, Soul, R&B, Downtempo",
        "keyword_stems": [
            "dream pop", "slowcore", "downtempo", "trip hop", "lo-fi", "chill",
            "shoegaze", "soft rock", "ballad", "bedroom pop", "soul", "funk", "r&b", "rnb",
        ],
    },
    "Unpretentious": {
        "description": "schlicht, aufrichtig, akustisch, bodenständig — Country, Folk, Singer-Songwriter",
        "keyword_stems": [
            "country", "folk", "singer-songwriter", "americana", "bluegrass", "acoustic",
        ],
    },
}


def _build_ordered_stems() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for name, data in MUSIC_DIMENSIONS.items():
        for stem in data["keyword_stems"]:
            pairs.append((stem, name))
    pairs.sort(key=lambda pair: len(pair[0]), reverse=True)
    return pairs


ORDERED_STEMS: list[tuple[str, str]] = _build_ordered_stems()

# Trennzeichen, die ein Genre in mehrere Wörter/Tokens aufteilen (z.B. "folk rock", "r&b").
_DELIMITER_RE = re.compile(r"[\s\-&/,]+")


def _build_stem_embeddings() -> dict[str, np.ndarray]:
    """Embedded jeden keyword_stem einmal (gebatcht) und gruppiert die Vektoren pro Dimension.

    Ersetzt den früheren Ansatz mit einem einzelnen Prosa-Anchor-Satz pro Dimension:
    ein langer Beschreibungssatz landet in einem anderen Bereich des Embedding-Raums
    als ein kurzes 1-3-Wort-Genre-Tag. Stem-Prototypen sind näher am tatsächlichen Input.
    """
    flat = [(dim, stem) for dim, data in MUSIC_DIMENSIONS.items() for stem in data["keyword_stems"]]
    vectors = embed_texts([stem for _, stem in flat])

    by_dim: dict[str, list[np.ndarray]] = defaultdict(list)
    for (dim, _stem), vec in zip(flat, vectors):
        by_dim[dim].append(np.array(vec))

    return {dim: np.stack(vecs) for dim, vecs in by_dim.items()}


DIMENSION_STEM_EMBEDDINGS: dict[str, np.ndarray] = _build_stem_embeddings()

SIMILARITY_THRESHOLD = 0.2


def _max_similarity(genre_vec: np.ndarray, dim: str) -> float:
    """Cosine-Similarity zum ähnlichsten Stem-Prototyp einer Dimension (kein Centroid).

    Ein Centroid würde bei stilistisch weit gestreuten Dimensionen (z.B. Sophisticated:
    "classical" + "idm" + "world") in semantisches Niemandsland fallen. Max-Similarity
    vergleicht stattdessen gegen jedes bekannte Beispiel einzeln — das ähnlichste gewinnt.
    """
    matrix = DIMENSION_STEM_EMBEDDINGS[dim]
    genre_norm = genre_vec / np.linalg.norm(genre_vec)
    matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return float((matrix_norm @ genre_norm).max())


def _keyword_match(g: str) -> str | None:
    """Keyword-Layer mit zwei unabhängigen Fixes gegenüber reinem Substring-Matching:

    Fix A — Wortgrenzen nur anwenden, wenn das Genre selbst ein Trennzeichen enthält
    UND der Stem keins enthält. Sonst bleibt reines Substring-Matching bestehen, damit
    zusammengeschriebene Compounds wie "synthpop", "citypop", "electropop" weiterhin
    über den Stem "pop" erkannt werden (dort gibt es keine Wortgrenze zwischen "synth"
    und "pop" im Sinne von \\b — ein strikter Wortgrenzen-Check würde diese Treffer
    brechen).

    Fix B — bei mehreren gleich langen Treffern aus unterschiedlichen Dimensionen
    (z.B. "emo rap": "emo" vs. "rap", beide Länge 3) entscheidet nicht mehr zufällig
    die Dict-Insertion-Reihenfolge von MUSIC_DIMENSIONS, sondern explizit das hintere
    Wort gewinnt — Compound-Genre-Tags folgen meist dem Muster Modifier+Head
    ("emo rap", "folk metal"), das hintere Wort ist die spezifischere Kopf-Genre.
    """
    has_delimiter = bool(_DELIMITER_RE.search(g))
    candidates: list[tuple[int, int, str]] = []  # (stem_len, position_in_g, dim)

    for stem, dim in ORDERED_STEMS:
        if has_delimiter and not _DELIMITER_RE.search(stem):
            pattern = rf"(?<!\w){re.escape(stem)}(?!\w)"
        else:
            pattern = re.escape(stem)
        match = re.search(pattern, g)
        if match:
            candidates.append((len(stem), match.start(), dim))

    if not candidates:
        return None

    max_len = max(c[0] for c in candidates)
    longest = [c for c in candidates if c[0] == max_len]
    dims = {c[2] for c in longest}
    if len(dims) == 1:
        return longest[0][2]

    longest.sort(key=lambda c: c[1])
    return longest[-1][2]  # Tie-Break: hinteres/rechtes Wort gewinnt (siehe Docstring)


def _best_dimension_and_score(g: str) -> tuple[str, float]:
    """Ungecachte Hilfsfunktion für die Threshold-Kalibrierung (siehe __main__ unten):
    gibt Dimension + Score VOR Anwendung von SIMILARITY_THRESHOLD zurück, damit ein
    Threshold-Sweep nicht gegen eine bereits gecachte, fest thresholdete Entscheidung läuft.
    """
    genre_vec = np.array(embed_text(g))
    scores = {dim: _max_similarity(genre_vec, dim) for dim in MUSIC_DIMENSIONS}
    best_dim = max(scores, key=scores.get)
    return best_dim, scores[best_dim]


@lru_cache(maxsize=None)
def _map_normalized(g: str) -> str | None:
    dim = _keyword_match(g)
    if dim is not None:
        return dim

    best_dim, best_score = _best_dimension_and_score(g)
    if best_score < SIMILARITY_THRESHOLD:
        return None
    return best_dim


def map_genre_to_dimension(genre: str) -> str | None:
    """Ordnet ein Genre einer der 5 MUSIC-Dimensionen zu, oder None (unmapped)."""
    return _map_normalized(genre.lower().strip())


def map_genres_to_dimensions(genres: list[str]) -> dict[str, str | None]:
    """Batch-Variante für mehrere Genres auf einmal (z.B. alle Genres eines Users).

    Löst den Keyword-Layer pro Item auf (billig) und embedded nur die verbleibenden
    unbekannten Genres in einem gebatchten embed_texts()-Call statt einer Schleife.
    Bewusst getrennt von _map_normalized/lru_cache gehalten — beides zu vereinheitlichen
    lohnt den Komplexitätsaufwand für dieses ~150-Zeilen-Modul nicht.
    """
    normalized = {g.lower().strip() for g in genres}
    result: dict[str, str | None] = {}
    to_embed: list[str] = []

    for g in normalized:
        dim = _keyword_match(g)
        if dim is not None:
            result[g] = dim
        else:
            to_embed.append(g)

    if to_embed:
        vectors = embed_texts(to_embed)
        for g, vec in zip(to_embed, vectors):
            genre_vec = np.array(vec)
            scores = {dim: _max_similarity(genre_vec, dim) for dim in MUSIC_DIMENSIONS}
            best_dim = max(scores, key=scores.get)
            result[g] = best_dim if scores[best_dim] >= SIMILARITY_THRESHOLD else None

    return {g: result[g.lower().strip()] for g in genres}


if __name__ == "__main__":
    # Regressionstests für den Keyword-Layer (Wortgrenzen-Fix + Tie-Break) — bypassen den Threshold.
    KEYWORD_LAYER_CASES: list[tuple[str, str]] = [
        ("synthpop", "Contemporary"),
        ("citypop", "Contemporary"),
        ("electropop", "Contemporary"),
        ("post-rock", "Sophisticated"),
        ("r&b", "Mellow"),
        ("emo rap", "Contemporary"),
        ("folk metal", "Intense"),
    ]
    print("--- Keyword-Layer Regressionstests ---")
    for genre, expected in KEYWORD_LAYER_CASES:
        actual = map_genre_to_dimension(genre)
        status = "OK" if actual == expected else "FEHLER"
        print(f"{status}: {genre!r} -> {actual} (erwartet: {expected})")

    # Handgelabelte Fälle ohne Keyword-Treffer, zur Threshold-Kalibrierung der Embedding-Fallback-Schicht.
    EMBEDDING_FALLBACK_POSITIVES: list[tuple[str, str]] = [
        ("bossa nova", "Mellow"),
        ("gregorian chant", "Sophisticated"),
        ("klezmer", "Sophisticated"),
        ("salsa", "Contemporary"),
        ("gospel", "Mellow"),
        ("reggae", "Mellow"),
    ]
    # Sollten unmapped (None) bleiben — liegen inhaltlich außerhalb des MUSIC-Modells.
    EMBEDDING_FALLBACK_NEGATIVES: list[str] = [
        "asmr", "white noise", "field recording", "spoken word",
    ]

    print("\n--- Threshold-Sweep (Embedding-Fallback) ---")
    for threshold in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]:
        hits = sum(
            1 for g, expected in EMBEDDING_FALLBACK_POSITIVES
            if _best_dimension_and_score(g)[1] >= threshold
            and _best_dimension_and_score(g)[0] == expected
        )
        false_positives = sum(
            1 for g in EMBEDDING_FALLBACK_NEGATIVES
            if _best_dimension_and_score(g)[1] >= threshold
        )
        print(
            f"threshold={threshold:.2f}  "
            f"recall={hits}/{len(EMBEDDING_FALLBACK_POSITIVES)}  "
            f"false_positives={false_positives}/{len(EMBEDDING_FALLBACK_NEGATIVES)}"
        )

    print("\n--- Weitere Beispiele (informativ, kein Erwartungswert) ---")
    for genre in ["polka", "schlager", "throat singing", "drill", "grime", "ska"]:
        print(genre, "->", map_genre_to_dimension(genre))
