# Kapselung aller DB Operationen an einem Ort. Mit Python. Um nicht in SQL in den Endpoint schreiben zu müssen
from sqlalchemy.orm import Session # Übersetzt Python Ausdrücke in SQL
from backend.db.models import User 

def get_user_by_spotify_id(db: Session, spotify_user_id: str) -> User | None:
    return db.query(User).filter(User.spotify_user_id == spotify_user_id).first()

def create_user(db: Session, spotify_user_id: str, access_token: str, refresh_token: str, token_expires_at) -> User:
    user = User(spotify_user_id = spotify_user_id, access_token = access_token, refresh_token = refresh_token, token_expires_at = token_expires_at)
    db.add(user)
    db.commit()
    db.refresh(user) # Holt Datenbankwerte die PostgreSQL generiert hat zurück
    return user