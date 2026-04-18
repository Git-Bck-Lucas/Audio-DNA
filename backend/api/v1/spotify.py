from fastapi import APIRouter, Depends
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from datetime import datetime

from sqlalchemy.orm import Session

from backend.config import settings
from backend.api.v1.schemas import UserResponse
from backend.db.session import get_db
from backend.db.repository import get_user_by_spotify_id, create_user, update_user_tokens
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
    spotify_o_auth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-top-read user-read-recently-played playlist-read-private user-library-read'
    )
    auth_url = spotify_o_auth.get_authorize_url() # generiere spotify-url
    return {
        "auth_url": auth_url
    }
    # Use Method get_authorize_url() to get login url 
    # return url 


@router.get("/callback", response_model=UserResponse) # Nach Zustimmung
async def callback(code: str, db: Session = Depends(get_db)): # Sage FastAPI: Führe get_db aus und gib mir das Ergebnis als db -> rugt get_db() auf 
    #-> öffnet sessoin und gibt sie per yield zurück, fast api übergibt session als db an endpoint
    spotify_o_auth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-top-read user-read-recently-played playlist-read-private user-library-read' 
    )
    token_dict = spotify_o_auth.get_access_token(code) # Nimmt den Code und tauscht ihn gegen Token
    sp = Spotify(auth=token_dict["access_token"])
    spotify_profile = sp.current_user()
    spotify_user_id = spotify_profile["id"]
    access_token = token_dict["access_token"]
    refresh_token = token_dict["refresh_token"]
    token_expires_at = datetime.fromtimestamp(token_dict["expires_at"])
    
    user = get_user_by_spotify_id(db, spotify_user_id)
    
    if user is None:
        user = create_user(db, spotify_user_id, access_token, refresh_token, token_expires_at)
    else:
        user = update_user_tokens(db, user, access_token, refresh_token, token_expires_at)
        
    return user

@router.get("/top-tracks")
async def get_top_tracks(access_token: str):
    spotify_object = Spotify(
        auth=access_token
    )
    current_top_tracks = spotify_object.current_user_top_tracks()
    return current_top_tracks


"""
Currently not possible due to spotify restrictions
@router.get("/audio-features")
async def audio_features(access_token: str, track_id: str):
    spotify_object = Spotify(
        auth=access_token
    )
    audio_features = spotify_object.audio_features(track_id)
    
    return audio_features
"""

@router.get("/top-artists")
async def get_top_artists(access_token: str):
    spotify_object = Spotify(
        auth=access_token
    )
    current_top_artists = spotify_object.current_user_top_artists()
    return current_top_artists

# playlist-read-private
@router.get("/read-private-playlist")
async def read_private_playlist(access_token: str):
    spotify_object = Spotify(
        auth=access_token
    )
    private_playlists = spotify_object.current_user_playlists()
    return private_playlists

# get all tracks vom playlist 
@router.get("get-tracks-from-playlist")
async def get_tracks_from_playlist(access_token:str, playlist_id: str):
    spotify_object = Spotify(
        auth=access_token
    )
    playlist_tracks = spotify_object.playlist_items(playlist_id)
    return playlist_tracks

# user-follow-read

# user-top-read