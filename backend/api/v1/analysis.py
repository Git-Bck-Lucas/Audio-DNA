from fastapi import APIRouter
from spotipy import Spotify 
from backend.services.personality_service import extract_genres_from_artists, calulate_personality_from_genres
from backend.services.llm_personality_service import analyze_personality_with_llm
from backend.services.feature_extraction_service import calculate_mainstream_score, calculate_diversity_score, calculate_content_features, calculate_temporal_features
from backend.services.spotify_data_helpers import extract_top_artists_names

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
    
    current_top_tracks = spotify_object.current_user_top_tracks()
    
    recently_played_tracks = spotify_object.current_user_recently_played(limit=50)
    
    diversity_scores = calculate_diversity_score(current_top_artists)
    content_features = calculate_content_features(current_top_tracks)
    temporal_features = calculate_temporal_features(recently_played_tracks)
    mainstream_score = calculate_mainstream_score(current_top_artists)
    extracted_artist_names = extract_top_artists_names(current_top_artists)
    
    personality_scores = analyze_personality_with_llm(
        genres=diversity_scores["all_genres"],
        mainstream_score=mainstream_score,
        top_artists=extracted_artist_names,
        diversity_scores=diversity_scores,
        content_features=content_features,
        temporal_features=temporal_features
    )
    return {
    "personality": personality_scores,
    "analysis_details": {
        "top_artists": extracted_artist_names,
        "genres_found": diversity_scores["all_genres"],
        "artists_analyzed": diversity_scores["artist_count"],
        "mainstream_score": mainstream_score
    },
    "diversity": {
        "total_genre_count": diversity_scores["all_genres_count"],
        "genre_clusters": diversity_scores["genres_cluster_count"],
        "genre_cluster_dict": diversity_scores["genre_cluster_dict"],
        "shannon_entropy": diversity_scores["shannon_entropy"]
    },
    "content_features": {
        "average_song_length_sec": content_features["average_song_length_sec"],
        "average_song_length_min": content_features["average_song_length_min"],
        "explicit_ratio": content_features["explicit_ratio"],
        "average_song_age": content_features["average_song_age"],
        "average_popularity": content_features["average_popularity"]
    },
    "recently_played": {
        "listening frequence": temporal_features["listening_frequency"],
        "repeat_ratio": temporal_features["repeat_ratio"]
    }
}
    

@router.get('/test')
async def test():
    return {'message': 'Test works!'}