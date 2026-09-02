import hmac
import hashlib
from backend.config import settings

def hash_spotify_id(spotify_user_id: str) -> str:
    return hmac.new(
        settings.USER_ID_HASH_SECRET.encode(),
        spotify_user_id.encode(),
        hashlib.sha256,
    ).hexdigest()