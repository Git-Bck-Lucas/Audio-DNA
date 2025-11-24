from fastapi import APIRouter
from spotipy import Spotify # maybe not necessary 

# Service funktion aus personality_service.py 
from backend.services.personality_service import extract_genres_from_artists, calulate_personality_from_genres
from backend.services.feature_extraction_service import calculate_mainstream_score, calculate_diversity_score

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
    
    # Diversity als Dict
    diversity_scores = calculate_diversity_score(current_top_artists)
    
    # Personality
    personality_scores = calulate_personality_from_genres(diversity_scores["all_genres"])
    
    # Mainstream
    mainstream_score = calculate_mainstream_score(current_top_artists)
    return {
    "personality": personality_scores,
    "analysis_details": {
        "genres_found": diversity_scores["all_genres"],
        "artists_analyzed": diversity_scores["artist_count"],  # ← Von diversity
        "mainstream_score": mainstream_score
    },
    "diversity": {
        "total_genre_count": diversity_scores["all_genres_count"],
        "genre_clusters": diversity_scores["genres_cluster_count"],
        "genre_cluster_dict": diversity_scores["genre_cluster_dict"],
        "shannon_entropy": diversity_scores["shannon_entropy"]
    }
}
    

@router.get('/test')
async def test():
    return {'message': 'Test works!'}