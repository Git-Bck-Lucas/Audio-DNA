import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOauthError
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from fastapi.responses import RedirectResponse

from backend.db.session import get_db
from backend.db.repository import get_user_by_spotify_id, create_user, update_user_tokens
from backend.services.spotify_auth_service import build_spotify_oauth, get_valid_access_token
from backend.config import settings
from backend.api.v1.schemas import UserResponse
from backend.db.models import User
from backend.api.dependencies import get_current_user
from backend.services.pseudonymization import hash_spotify_id

import logging

logger = logging.getLogger("audio_dna.spotify")
# Router for everything which is connected to spotify 
# All endpoints get /spotify

router = APIRouter(
    prefix='/spotify',
    tags=["spotify"]
)

@router.get("/test") # Test Endpoint on /test
async def test():
    return {
        "message": "spotify"
    }
    
@router.get("/login")
async def login(request: Request):
    # Zufälliges, nicht erratbares Einmal-Token gegen Login-CSRF: an die Session
    # dieses Browsers gebunden, muss beim Callback exakt wiederkommen (siehe dort).
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    # Create Spofify OAuth Object with Credentials from settings
    spotify_o_auth = build_spotify_oauth()
    auth_url = spotify_o_auth.get_authorize_url(state=state) # generiere spotify-url
    return {
        "auth_url": auth_url
    }
    # Use Method get_authorize_url() to get login url
    # return url
    
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(settings.FRONTEND_URL)


@router.get("/callback")
async def callback(
    request: Request,
    db: Session = Depends(get_db),
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
): # Sage FastAPI: Führe get_db aus und gib mir das Ergebnis als db -> rugt get_db() auf
    #-> öffnet sessoin und gibt sie per yield zurück, fast api übergibt session als db an endpoint

    # Nutzer hat die Spotify-Berechtigung abgelehnt (error=access_denied, kein code) --
    # oder jemand ruft /callback ohne die erwarteten Parameter auf. Kein Grund zum
    # Crashen, einfach zurück zum Frontend, dort landet man wieder auf dem Login-Screen.
    expected_state = request.session.pop("oauth_state", None)
    if error is not None or code is None or state is None:
        return RedirectResponse(url=settings.FRONTEND_URL)

    if expected_state is None or not secrets.compare_digest(state, expected_state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    spotify_o_auth = build_spotify_oauth()
    try:
        token_dict = spotify_o_auth.get_access_token(code) # Nimmt den Code und tauscht ihn gegen Token
    except SpotifyOauthError:
        # code war ungültig/abgelaufen/schon eingelöst (z.B. Doppel-Callback durch
        # Browser-Zurück-Button) -- auch das ist kein Serverfehler, sondern ein
        # normaler Ablauf-Fall.
        return RedirectResponse(url=settings.FRONTEND_URL)

    sp = Spotify(auth=token_dict["access_token"])
    spotify_profile = sp.current_user()
    spotify_id_hash = hash_spotify_id(spotify_profile["id"])
    access_token = token_dict["access_token"]
    refresh_token = token_dict["refresh_token"]
    token_expires_at = datetime.fromtimestamp(token_dict["expires_at"], tz=timezone.utc)
    
    user = get_user_by_spotify_id(db, spotify_id_hash)
    
    if user is None:
        user = create_user(db, spotify_id_hash, access_token, refresh_token, token_expires_at)
    else:
        user = update_user_tokens(db, user, access_token, refresh_token, token_expires_at)
        
    request.session["user_id"] = user.id
        
    return RedirectResponse(url=settings.FRONTEND_URL)

@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    # Der Anzeigename wird bewusst nicht gespeichert -- in der DB steht nur der HMAC
    # der Spotify-ID. Hier wird er pro Aufruf frisch geholt und nur durchgereicht.
    # Zweck: Das Frontend soll zeigen koennen, WESSEN Sitzung gerade laeuft. Ohne das
    # ist eine fremde (z.B. veraltete) Session fuer den Nutzer unsichtbar.
    display_name: str | None = None
    try:
        access_token = get_valid_access_token(db, user)
        profile = Spotify(auth=access_token).current_user()
        display_name = profile.get("display_name") or profile.get("id")
    except Exception:
        # Best effort: /me ist der Auth-Check des Frontends. Er darf nicht scheitern,
        # nur weil eine reine Anzeige-Information nicht zu holen war -- der Nutzer
        # bleibt eingeloggt, es fehlt dann eben der Name.
        logger.warning("Spotify-Anzeigename konnte nicht geladen werden", exc_info=True)

    return UserResponse(created_at=user.created_at, display_name=display_name)