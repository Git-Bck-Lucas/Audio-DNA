from sqlalchemy.orm import Session
from backend.rag.genre_mapping import map_genres_to_dimensions
from backend.rag.dimension_queries import trait_query
from backend.db.repository import search_similar_chunks
from backend.db.models import Chunks


def retrieve_grounding_context(db: Session, genres: list[str], top_k: int = 3) -> list[tuple[Chunks, float]]:
    
    mapping = map_genres_to_dimensions(genres)
    relevant_dimensions = {dim for dim in mapping.values() if dim is not None}
    
    all_hits: list[tuple[Chunks, float]] = []
    for dim in relevant_dimensions:
        query_vec = trait_query(dim)
        hits = search_similar_chunks(db, query_vec, top_k=top_k, dimension=dim)
        all_hits.extend(hits)
    best_by_id: dict[int, tuple[Chunks, float]] = {}
    for chunk, score in all_hits:
        existing = best_by_id.get(chunk.id)
        if existing is None or score > existing[1]:
            best_by_id[chunk.id] = (chunk, score)
            
    return list(best_by_id.values())


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
    