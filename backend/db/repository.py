# Kapselung aller DB Operationen an einem Ort. Mit Python. Um nicht in SQL in den Endpoint schreiben zu müssen
from sqlalchemy.orm import Session # Übersetzt Python Ausdrücke in SQL
from backend.db.models import User, Analysis, Chunks

def get_user_by_spotify_id(db: Session, spotify_user_id: str) -> User | None:
    return db.query(User).filter(User.spotify_user_id == spotify_user_id).first()

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