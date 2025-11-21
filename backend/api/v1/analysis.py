from fastapi import APIRouter
from spotipy import Spotify # maybe not necessary 

# Service funktion aus personality_service.py 
from backend.services.personality_service import extract_genres_from_artists, calulate_personality_from_genres
from backend.services.feature_extraction_service import calculate_mainstream_score

router = APIRouter(
    prefix='/analysis',
    tags=["analysis"]
)

@router.get('/get_personality')
async def get_personality(access_token: str) -> dict: 
    spotify_object = Spotify(
        auth=access_token
    )
    current_top_artists = spotify_object.current_user_top_artists()
    extracted_genres = extract_genres_from_artists(current_top_artists)
    personality_scores = calulate_personality_from_genres(extracted_genres)
    mainstream_score = calculate_mainstream_score(current_top_artists)
    return {
        "personality": personality_scores,
        "analysis_details": {
            "genres_found": extracted_genres,
            "genre_count": len(extracted_genres),
            "artists_analyzed": len(current_top_artists['items']),
            "mainstream_score": mainstream_score
        }
    }
    

@router.get('/test')
async def test():
    return {'message': 'Test works!'}