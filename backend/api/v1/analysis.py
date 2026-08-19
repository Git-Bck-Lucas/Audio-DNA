from fastapi import APIRouter, Depends, HTTPException
from spotipy import Spotify 
from backend.services.llm_personality_service import analyze_personality_with_llm
from backend.services.feature_extraction_service import calculate_mainstream_score, calculate_diversity_score, calculate_content_features, calculate_temporal_features
from backend.services.retrieval_service import retrieve_grounding_context, format_grounding_context
from backend.services.spotify_data_helpers import extract_top_artists_names
from backend.services.spotify_auth_service import get_valid_access_token
from backend.api.v1.schemas import AnalysisResponse, Mode
from backend.api.rate_limit import rate_limit_analysis
from backend.db.models import User
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.repository import create_analysis

import logging

logger = logging.getLogger("audio_dna.analysis")

router = APIRouter(
    prefix='/analysis',
    tags=["analysis"]
)

@router.get('/get_personality', response_model=AnalysisResponse)
async def get_personality(user: User = Depends(rate_limit_analysis), mode: Mode = "science", db: Session = Depends(get_db)) -> AnalysisResponse: 
    logger.info("Starting Personality Analysis Request ")
    try:
        access_token = get_valid_access_token(db, user)
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
        
        raw_context = retrieve_grounding_context(db, diversity_scores["all_genres"], top_k=3)
        grounding_context = format_grounding_context(raw_context)
        
        personality_scores = analyze_personality_with_llm(
            genres=diversity_scores["all_genres"],
            mainstream_score=mainstream_score,
            top_artists=extracted_artist_names,
            diversity_scores=diversity_scores,
            content_features=content_features,
            temporal_features=temporal_features,
            grounding_context=grounding_context,
            mode=mode
        )
        logger.info("Personality analysis completed successfully")
        personality_analyis_dict =  {
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
        return create_analysis(db, user.id, personality_analyis_dict)
        
    
    except Exception as e:
        logger.error(f"Personality Analysis failed: {e}")
        raise
    

@router.get('/test')
async def test():
    return {'message': 'Test works!'}