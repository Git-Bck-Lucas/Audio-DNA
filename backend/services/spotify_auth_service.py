from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from spotipy.oauth2 import SpotifyOAuth
from backend.config import settings
from backend.db.models import User
from backend.db.repository import update_user_tokens

EXPIRY_BUFFER = timedelta(seconds=60)

def build_spotify_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-top-read user-read-recently-played playlist-read-private user-library-read',
    )

def get_valid_access_token(db: Session, user: User) -> str:
    now = datetime.now(timezone.utc)
    
    if user.token_expires_at > now + EXPIRY_BUFFER:
        return user.access_token
    
    oauth = build_spotify_oauth()
    token_dict = oauth.refresh_access_token(user.refresh_token)
    
    new_access = token_dict["access_token"]
    new_refresh = token_dict.get("refresh_token", user.refresh_token)
    new_expires = datetime.fromtimestamp(token_dict["expires_at"], tz=timezone.utc)
    
    user = update_user_tokens(db, user, new_access, new_refresh, new_expires)
    return user.access_token
    
    
    
    
    