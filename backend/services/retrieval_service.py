from sqlalchemy.orm import Session
from backend.rag.genre_mapping import map_genres_to_dimensions
from backend.rag.dimension_queries import trait_query
from backend.db.repository import search_similar_chunks
from backend.db.models import Chunks
from backend.rag.trait_queries import big_five_query, BIG_FIVE_TRAIT_QUERIES


def format_grounding_context(results: list[tuple[Chunks, float]]) -> str:
    """Baut aus den (Chunk, Score)-Treffern einen Textblock fuers Prompt.
    Pro Chunk eine Quellenangabe plus der Text, nach Relevanz sortiert.
    """
    if not results:
        return "No relevant literature found."

    sorted_results = sorted(results, key=lambda hit: hit[1], reverse=True)

    # author/source/text sind Attribute am Chunk (record[0]); der Score (record[1])
    # wird bewusst nicht ausgegeben, daher der Unterstrich beim Entpacken.
    entries = [
        f"[{chunk.author}, {chunk.source}] {chunk.text}"
        for chunk, _score in sorted_results
    ]
    return "\n\n".join(entries)


def _dedupe_best(hits: list[tuple[Chunks, float]]) -> list[tuple[Chunks, float]]:
    """Pro chunk.id nur den besten Score behalten. (zieh die bestehende Logik hier rein)"""
    best_by_id: dict[int, tuple[Chunks, float]] = {}
    for chunk, score in hits:
        existing = best_by_id.get(chunk.id)
        if existing is None or score > existing[1]:
            best_by_id[chunk.id] = (chunk, score)
    return list(best_by_id.values())


def retrieve_by_traits(
    db: Session,
    top_k: int = 2,
    use_filter: bool = False,   # Filter an/aus -> damit Eval beide Varianten messen kann
) -> list[tuple[Chunks, float]]:
    all_hits: list[tuple[Chunks, float]] = []
    for trait in BIG_FIVE_TRAIT_QUERIES:
        query_vec = big_five_query(trait)
        hits = search_similar_chunks(
            db, query_vec, top_k=top_k,
            trait=trait if use_filter else None,          # Filter an/aus über den Parameter
        )
        all_hits.extend(hits)
    return all_hits   

def retrieve_grounding_context(
    db: Session,
    genres: list[str],
    top_k: int = 3,
    trait_top_k: int = 2,
) -> list[tuple[Chunks, float]]:
    mapping = map_genres_to_dimensions(genres)
    relevant_dimensions = {dim for dim in mapping.values() if dim is not None}

    dimension_hits: list[tuple[Chunks, float]] = []
    for dim in relevant_dimensions:
        query_vec = trait_query(dim)
        dimension_hits.extend(
            search_similar_chunks(db, query_vec, top_k=top_k, dimension=dim)
        )

    # --- Pfad 2: direkt pro Big-Five-Trait (neu) ---
    trait_hits = retrieve_by_traits(db, top_k=trait_top_k)

    # --- zusammenführen, Duplikate raus ---
    return _dedupe_best(dimension_hits + trait_hits)
    