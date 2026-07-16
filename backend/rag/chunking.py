import re
from collections import Counter

_BOILERPLATE_PATTERNS = [
    re.compile(r"this article is intended solely for", re.IGNORECASE),
    re.compile(r"this document is copyrighted by the american psychological association", re.IGNORECASE),
    re.compile(r"©\s?\d{4}"),                       # Copyright-Jahr, z.B. "© 2012"
    re.compile(r"\bDOI:\s?10\.\d+", re.IGNORECASE), # DOI-Präfix
    re.compile(r"^downloaded from https?://", re.IGNORECASE),  # PDF-Hosting-Footer (z.B. UC Press)
    re.compile(r"^download:\s?https?://", re.IGNORECASE),      # Artikel-Download-Link-Footer
]

MIN_CHUNK_LENGTH = 200

# Laufköpfe/-füße (Zeitschriftenname, Artikeltitel, Autorennamen) wiederholen sich wörtlich
# auf jeder PDF-Seite, sind aber von Paper zu Paper unterschiedlich — das lässt sich nicht
# sinnvoll als feste Regex-Liste pflegen (skaliert nicht, sobald ein neues Paper dazukommt).
# Stattdessen: Zeilen, die im Dokument mehrfach identisch vorkommen und kurz genug sind, um
# eine Kopf-/Fußzeile statt echter Fließtext zu sein, generisch rauswerfen.
REPEATED_LINE_THRESHOLD = 3
MAX_HEADER_LINE_LENGTH = 150


def _strip_repeated_lines(text: str) -> str:
    lines = text.split("\n")
    counts = Counter(line.strip() for line in lines if line.strip())
    repeated = {
        line for line, count in counts.items()
        if count >= REPEATED_LINE_THRESHOLD and len(line) <= MAX_HEADER_LINE_LENGTH
    }
    return "\n".join(line for line in lines if line.strip() not in repeated)


def _strip_boilerplate_patterns(text: str) -> str:
    lines = text.split("\n")
    return "\n".join(
        line for line in lines
        if not any(pattern.search(line) for pattern in _BOILERPLATE_PATTERNS)
    )


def is_boilerplate(chunk: str) -> bool:
    """Sicherheitsnetz auf Chunk-Ebene, nachdem das Line-Stripping oben schon gelaufen ist:
    fängt verwaiste Mini-Chunks ab (z.B. Overlap-Reste), die trotzdem noch durchrutschen."""
    if len(chunk.strip()) < MIN_CHUNK_LENGTH:
        return True
    return any(pattern.search(chunk) for pattern in _BOILERPLATE_PATTERNS)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: The full document text
        chunk_size: Max characters per chunk
        overlap: Characters to repeat between chunks
    """
    text = _strip_repeated_lines(text)
    text = _strip_boilerplate_patterns(text)

    # TODO: Split text into sentences first
    # Hint: text.split(". ") is simple but works for papers
    sentences = text.split(". ")
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    # TODO: Build chunks by adding sentences until chunk_size is reached
    for sentence in sentences:
        if current_length + len(sentence) <= chunk_size:
            current_chunk.append(sentence)
            current_length += len(sentence)
        else:
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s) > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_length += len(s)
                
            chunks.append(". ".join(current_chunk))
            current_chunk = overlap_sentences
            current_length = overlap_length
            current_chunk.append(sentence)
            current_length += len(sentence)
    
    if current_chunk:
        chunks.append(". ".join(current_chunk))

    return [c for c in chunks if not is_boilerplate(c)]

""""
if __name__ == "__main__":
    text = load_documents("backend/rag/documents/Schaefer_Mehlhorn_2017.md")
    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks[:3]):
       for i in range(min(3, len(chunks) - 1)):
        print(f"--- Ende Chunk {i} ---")
        print(chunks[i][-150:])
        print(f"--- Anfang Chunk {i+1} ---")
        print(chunks[i+1][:150])
        print()
"""