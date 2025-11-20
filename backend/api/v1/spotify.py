from fastapi import APIRouter
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

from backend.config import settings
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


@router.get("/callback") # Nach Zustimmung
async def callback(code: str):
    spotify_o_auth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope='user-top-read user-read-recently-played playlist-read-private user-library-read' 
    )
    token_dict = spotify_o_auth.get_access_token(code) # Nimmt den Code und tauscht ihn gegen Token
    
    return token_dict

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