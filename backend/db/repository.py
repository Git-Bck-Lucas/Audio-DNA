# Kapselung aller DB Operationen an einem Ort. Mit Python. Um nicht in SQL in den Endpoint schreiben zu müssen
from sqlalchemy.orm import Session # Übersetzt Python Ausdrücke in SQL
from backend.db.models import User, Analysis, Chunks

def get_user_by_spotify_id(db: Session, spotify_user_id: str) -> User | None:
    return db.query(User).filter(User.spotify_user_id == spotify_user_id).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, spotify_user_id: str, access_token: str, refresh_token: str, token_expires_at) -> User:
    user = User(spotify_user_id = spotify_user_id, access_token = access_token, refresh_token = refresh_token, token_expires_at = token_expires_at)
    db.add(user)
    db.commit()
    db.refresh(user) # Holt Datenbankwerte die PostgreSQL generiert hat zurück
    return user

def create_analysis(db: Session, user_id: int, result: dict) -> Analysis:
    analysis = Analysis(user_id = user_id, result = result)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def update_user_tokens(db: Session, user: User, access_token: str, refresh_token: str, token_expires_at) -> User:
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.token_expires_at = token_expires_at
    db.commit()
    db.refresh(user)
    return user

def replace_chunks(db: Session, chunks: list[Chunks]) -> None:
    """Leert die chunks-Tabelle und schreibt die neuen — atomar, ein Commit."""
    db.query(Chunks).delete()
    db.add_all(chunks)
    db.commit()
    
def search_similar_chunks(
    db: Session,
    query_vector: list[float],
    top_k: int = 5,
    dimension: str | None = None,
    trait: str | None = None,
) -> list[tuple[Chunks, float]]:
    """Findet die top_k ähnlichsten Chunks und gibt je (Chunk, Similarity) zurück.

    pgvector liefert eine Cosinus-DISTANZ (0 = identisch, 2 = gegensätzlich). Wir geben
    stattdessen die intuitivere Similarity = 1 - Distanz zurück (1.0 = perfekt, 0.0 = orthogonal),
    damit sich Treffer verschiedener Query-Strategien direkt vergleichen lassen.

    Hybrid-Retrieval: Mit `dimension` und/oder `trait` wird die Vektorsuche VORHER auf Chunks
    eingeschränkt, die im Metadaten-Tag die jeweilige Dimension/den Trait tragen ("wert = ANY(spalte)").
    So verschwinden die generischen Chunks, die bei reiner Vektorsuche für jede Dimension oben landen.
    """
    distance = Chunks.embedding.cosine_distance(query_vector)
    query = db.query(Chunks, distance.label("distance"))
    if dimension is not None:
        query = query.filter(Chunks.dimensions.any(dimension))
    if trait is not None:
        query = query.filter(Chunks.traits.any(trait))
    rows = query.order_by(distance).limit(top_k).all()
    return [(chunk, 1.0 - distance_value) for chunk, distance_value in rows]

if __name__ == "__main__":
    # Kurzer Smoke-Test der Score-Rückgabe. Für den vollen Strategie-Vergleich:
    #   python -m backend.rag.compare_query_strategies
    from backend.db.database import SessionLocal
    from backend.rag.dimension_queries import centroid_query

    with SessionLocal() as db:
        for dim in ("Sophisticated", "Contemporary"):
            print(f"\n=== {dim} (stem-centroid) ===")
            for chunk, score in search_similar_chunks(db, centroid_query(dim), top_k=7):
                print(f"  sim={score:.3f}  [{chunk.source}] {chunk.text[:80]}...")