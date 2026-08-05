"""Vergleicht die Query-Strategien aus dimension_queries.py nebeneinander.

Zweck: pro Dimension sehen, welche Strategie SCHÄRFERE Treffer liefert — also (a) höhere
Similarity-Scores und vor allem (b) inhaltlich zur Dimension passende Chunks statt für alle
Dimensionen derselben generischen Methodik-Passagen.

Voraussetzung:
  1. DB läuft (docker compose up -d db)
  2. chunks-Tabelle ist befüllt:  python -m backend.rag.ingest
Ausführen:
  python -m backend.rag.compare_query_strategies

Lesehilfe für die Ausgabe:
  - Vergleiche die drei Blöcke einer Dimension: liefern sie DIESELBEN Chunks (dann trennt die
    Strategie nicht) oder je andere?
  - "Gut" heißt nicht nur hoher Score, sondern: taucht derselbe Chunk bei mehreren Dimensionen
    ganz oben auf (= unspezifisch) oder ist er für genau diese Dimension einschlägig?
"""

from backend.db.database import SessionLocal
from backend.db.repository import search_similar_chunks
from backend.rag.genre_mapping import MUSIC_DIMENSIONS
from backend.rag.dimension_queries import centroid_query, description_query, trait_query

# Reihenfolge = didaktische Reihenfolge: von unschärfster (A) zu erwartet schärfster (C).
# Jeder Eintrag: (Label, Query-Builder, Dimension-als-Filter?). Der letzte kombiniert die beste
# Query-Strategie (C) mit dem Metadaten-Filter (Hybrid-Retrieval) — das ist der eigentliche Test.
STRATEGIES = [
    ("A: stem-centroid   (DE-Genres, gemittelt)", centroid_query, False),
    ("B: description     (DE-Prosa)",             description_query, False),
    ("C: trait-prose     (EN-Fließtext)",         trait_query, False),
    ("C+filter: trait-prose + dimension-filter",  trait_query, True),
]

TOP_K = 3


def main() -> None:
    with SessionLocal() as db:
        for dim in MUSIC_DIMENSIONS:
            print(f"\n{'=' * 72}\nDIMENSION: {dim}\n{'=' * 72}")
            for label, build_query, use_filter in STRATEGIES:
                query_vec = build_query(dim)
                results = search_similar_chunks(
                    db, query_vec, top_k=TOP_K,
                    dimension=dim if use_filter else None,
                )
                print(f"\n  [{label}]")
                if not results:
                    print("    (keine Chunks mit diesem Dimension-Tag)")
                for chunk, score in results:
                    snippet = " ".join(chunk.text[:120].split())  # Zeilenumbrüche glätten
                    print(f"    sim={score:.3f}  [{chunk.source}]  {snippet}...")


if __name__ == "__main__":
    main()
