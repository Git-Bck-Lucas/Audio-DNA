from backend.rag.embed import embed_text
import numpy as np

MUSIC_DIMENSIONS = {
    "Sophisticated": {
        "description": "komplex, intelligent, inspirierend — Klassik, Jazz, World, Avantgarde, experimentelle Elektronik",
        "anchor": "complex intelligent sophisticated inspiring music: classical, jazz, blues, avant-garde, "
                  "experimental electronic, IDM, ambient, world",
        "keyword_stems": [
            "classical", "neoclassical", "baroque", "opera", "jazz", "fusion",
            "idm", "experimental", "avant", "drone", "post-rock",
            "ambient", "space", "world", "blues",
        ],
    },
    "Intense": {
        "description": "laut, kraftvoll, aggressiv — Rock, Punk, Metal, Hardcore",
        "anchor": "loud aggressive forceful intense music: rock, punk, heavy metal, hardcore, grunge",
        "keyword_stems": [
            "rock", "metal", "punk", "hardcore", "grunge",
            "industrial", "emo", "screamo", "thrash", "doom", "garage rock",
        ],
    },
    "Contemporary": {
        "description": "rhythmisch, perkussiv, elektronisch, tanzbar — Rap, Techno, House, Pop, Dance",
        "anchor": "rhythmic percussive electronic danceable music: rap, hip hop, techno, house, trance, "
                  "drum and bass, dubstep, dance, pop, electronica",
        "keyword_stems": [
            "techno", "house", "trance", "electro", "edm", "dnb", "drum and bass",
            "dubstep", "rap", "hip hop", "dance", "eurodance", "bounce", "electronic",
            "pop", "disco", "breakbeat", "jungle", "bass", "hardstyle", "phonk", "synthwave",
        ],
    },
    "Mellow": {
        "description": "smooth, entspannt, romantisch, ruhig — Soft Rock, Dream Pop, Soul, R&B, Downtempo",
        "anchor": "smooth relaxing romantic mellow music: soft rock, dream pop, soul, funk, r&b, "
                  "downtempo, trip hop, slowcore, shoegaze",
        "keyword_stems": [
            "dream pop", "slowcore", "downtempo", "trip hop", "lo-fi", "chill",
            "shoegaze", "soft rock", "ballad", "bedroom pop", "soul", "funk", "r&b", "rnb",
        ],
    },
    "Unpretentious": {
        "description": "schlicht, aufrichtig, akustisch, bodenständig — Country, Folk, Singer-Songwriter",
        "anchor": "sincere uncomplicated acoustic rootsy music: country, folk, singer-songwriter, americana",
        "keyword_stems": [
            "country", "folk", "singer-songwriter", "americana", "bluegrass", "acoustic",
        ],
    },
}

ANCHOR_VECTORS: dict[str, list[float]] = {
    name: embed_text(data["anchor"])
    for name, data in MUSIC_DIMENSIONS.items()
}

def _cosine(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def _build_ordered_stems() -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = [] # liste aus tuplen 

    # TODO: über MUSIC_DIMENSIONS iterieren.
    for name, data in MUSIC_DIMENSIONS.items():
         for stem in data["keyword_stems"]:
             pairs.append((stem, name))

    pairs.sort(key=lambda pair: len(pair[0]), reverse=True)

    return pairs

ORDERED_STEMS: list[tuple[str, str]] = _build_ordered_stems()

SIMILARITY_THRESHOLD = 0.2


def map_genre_to_dimension(genre: str) -> str | None:
    """Ordnet ein Genre einer der 5 MUSIC-Dimensionen zu, oder None (unmapped)."""
    g = genre.lower().strip()

    for stem, dim in ORDERED_STEMS:
        if stem in g:        # "in" auf zwei Strings = Substring-Check
            return dim


    genre_vec = embed_text(g)
    best_dim: str | None = None
    best_score = -1.0
    for dim, anchor_vec in ANCHOR_VECTORS.items():   # dim = Name, anchor_vec = Vektor
        score = _cosine(genre_vec, anchor_vec)
        if score > best_score:
            best_dim = dim
            best_score = score

    # Schicht 3 — Schwelle
    if best_score < SIMILARITY_THRESHOLD:
        return None
    return best_dim
    
if __name__ == "__main__":
    test_genres = [
        # gängig — sollten höher scoren und grob sinnvoll liegen
        "reggae", "salsa", "gospel", "ska", "grime", "drill", "lounge",
        # nischig / nicht-englisch — Test, ob die Schwelle sie als "unmapped" abfängt
        "klezmer", "polka", "schlager", "bossa nova", "gregorian chant", "throat singing",
    ]
    for genre in test_genres:
        print(genre, "->", map_genre_to_dimension(genre))