"""Lexikalisches Tagging von Chunks mit MUSIC-Dimensionen und Big-Five-Traits.

Warum lexikalisch statt embedding-basiert: Wir haben beim Query-Vergleich gesehen, dass
Embeddings über diesen kleinen Korpus auf generische Chunks kollabieren. Fürs METADATEN-
Tagging wollen wir das Gegenteil — eine präzise, nachvollziehbare, deterministische
Zuordnung. Ein Chunk wird einer Dimension zugeordnet, wenn er charakteristisches Vokabular
dieser Dimension enthält (Dimensionsname, Kern-Adjektive, kanonische Genre-Beispiele aus dem
MUSIC-Modell). Ein Chunk kann zu mehreren Dimensionen gehören (die Meta-Analyse-
Zusammenfassung nennt alle fünf) oder zu keiner — deshalb eine Liste, kein Einzelwert.

Bewusst getrennt von genre_mapping.py: dort werden einzelne Spotify-Genre-Strings gemappt,
hier wird englischer Fließtext getaggt. Anderes Vokabular, andere Aufgabe.
"""

import re

# Kern-Vokabular pro MUSIC-Dimension: Dimensionsname + charakteristische Adjektive + kanonische
# Genre-Beispiele (aus der MUSIC-Modell-Definition, Rentfrow/Goldberg/Levitin 2011). Die
# STOMP-Bezeichnungen der Rentfrow-2003-Papers (z.B. "reflective and complex") sind mit
# aufgenommen, damit auch deren Passagen greifen.
DIMENSION_VOCAB: dict[str, list[str]] = {
    "Sophisticated": [
        "sophisticated", "reflective and complex", "reflective & complex",
        "classical", "jazz", "blues", "opera", "world music",
    ],
    "Intense": [
        "intense", "rebellious", "rock", "heavy metal", "metal", "punk",
        "alternative", "loud", "aggressive",
    ],
    "Contemporary": [
        "contemporary", "energetic and rhythmic", "rhythmic",
        "rap", "hip-hop", "hip hop", "electronica", "dance music", "soul", "funk",
    ],
    "Mellow": [
        "mellow", "romantic", "relaxing", "soft rock", "r&b", "smooth jazz",
    ],
    "Unpretentious": [
        "unpretentious", "upbeat and conventional", "sincere", "uncomplicated",
        "country", "folk", "singer-songwriter",
    ],
}

TRAIT_VOCAB: dict[str, list[str]] = {
    "Openness": ["openness", "open to experience", "open-mindedness"],
    "Conscientiousness": ["conscientiousness", "conscientious"],
    "Extraversion": ["extraversion", "extravert", "extrovert", "extroversion"],
    "Agreeableness": ["agreeableness", "agreeable"],
    "Neuroticism": ["neuroticism", "neurotic", "emotional stability"],
}


def _compile(vocab: dict[str, list[str]]) -> dict[str, list[re.Pattern]]:
    # Wortgrenzen (\b) sind hier korrekt, weil wir Fließtext taggen (anders als bei Genre-Strings
    # wie "synthpop"): verhindert, dass "soul" in "soulful" oder "rock" in "rockville" matcht.
    return {
        label: [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in terms]
        for label, terms in vocab.items()
    }


_DIMENSION_PATTERNS = _compile(DIMENSION_VOCAB)
_TRAIT_PATTERNS = _compile(TRAIT_VOCAB)


def _match(text: str, patterns: dict[str, list[re.Pattern]]) -> list[str]:
    return [label for label, pats in patterns.items() if any(p.search(text) for p in pats)]


def tag_chunk(text: str) -> tuple[list[str], list[str]]:
    """Gibt (dimensions, traits) für einen Chunk zurück — je eine Liste getroffener Labels."""
    return _match(text, _DIMENSION_PATTERNS), _match(text, _TRAIT_PATTERNS)


if __name__ == "__main__":
    samples = [
        "Openness to experience predicts a preference for sophisticated music like classical and jazz.",
        "Heavy metal and punk fans tend to score higher on sensation seeking.",
        "Participants were instructed to skip any category with which they were not familiar.",
    ]
    for s in samples:
        dims, traits = tag_chunk(s)
        print(f"dims={dims} traits={traits}  <- {s[:60]}...")
