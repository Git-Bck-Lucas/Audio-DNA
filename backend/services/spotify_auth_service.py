from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
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
        # Ohne das schreibt/liest spotipy standardmäßig einen Token-Cache-File auf
        # Disk (.cache), den sich alle Requests/Nutzer dieses Servers teilen würden --
        # get_access_token() würde dann bei jedem Login zuerst dort nachsehen und im
        # schlimmsten Fall den Token eines ANDEREN Nutzers zurückgeben, statt den
        # übergebenen code einzulösen. MemoryCacheHandler ohne Startwert ist pro
        # Request eine frische, leere Instanz -- erzwingt den echten Code-Austausch.
        cache_handler=MemoryCacheHandler(),
    )

def get_valid_access_token(db: Session, user: User) -> str:
    now = datetime.now(timezone.utc)
    
    if user.token_expires_at > now + EXPIRY_BUFFER:
        return user.access_token
    
    oauth = build_spotify_oauth()
    try:
        token_dict = oauth.refresh_access_token(user.refresh_token)
    except SpotifyOauthError:
        # Nutzer hat den App-Zugriff in seinen Spotify-Einstellungen entzogen, oder
        # der refresh_token ist sonst ungültig geworden -- kein Serverfehler, der
        # Nutzer muss sich einfach neu einloggen.
        raise HTTPException(status_code=401, detail="spotify_reauth_required")

    new_access = token_dict["access_token"]
    new_refresh = token_dict.get("refresh_token", user.refresh_token)
    new_expires = datetime.fromtimestamp(token_dict["expires_at"], tz=timezone.utc)
    
    user = update_user_tokens(db, user, new_access, new_refresh, new_expires)
    return user.access_token
    
    
    
    
    