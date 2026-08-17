from fastapi import APIRouter, Depends, Request
from spotipy import Spotify
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.api.v1.schemas import UserResponse
from backend.db.session import get_db
from backend.db.repository import get_user_by_spotify_id, create_user, update_user_tokens
from backend.services.spotify_auth_service import build_spotify_oauth
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
async def login():
    # Create Spofify OAuth Object with Credentials from settings
    spotify_o_auth = build_spotify_oauth()
    auth_url = spotify_o_auth.get_authorize_url() # generiere spotify-url
    return {
        "auth_url": auth_url
    }
    # Use Method get_authorize_url() to get login url 
    # return url 


@router.get("/callback", response_model=UserResponse) # Nach Zustimmung
async def callback(code: str, request: Request, db: Session = Depends(get_db)): # Sage FastAPI: Führe get_db aus und gib mir das Ergebnis als db -> rugt get_db() auf 
    #-> öffnet sessoin und gibt sie per yield zurück, fast api übergibt session als db an endpoint
    spotify_o_auth = build_spotify_oauth()
    token_dict = spotify_o_auth.get_access_token(code) # Nimmt den Code und tauscht ihn gegen Token
    sp = Spotify(auth=token_dict["access_token"])
    spotify_profile = sp.current_user()
    spotify_user_id = spotify_profile["id"]
    access_token = token_dict["access_token"]
    refresh_token = token_dict["refresh_token"]
    token_expires_at = datetime.fromtimestamp(token_dict["expires_at"], tz=timezone.utc)
    
    user = get_user_by_spotify_id(db, spotify_user_id)
    
    if user is None:
        user = create_user(db, spotify_user_id, access_token, refresh_token, token_expires_at)
    else:
        user = update_user_tokens(db, user, access_token, refresh_token, token_expires_at)
        
    request.session["user_id"] = user.id
        
    return user