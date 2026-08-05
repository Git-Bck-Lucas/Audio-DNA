from anthropic import Anthropic
from backend.config import settings
import json

from backend.logging_config import logger
from backend.api.v1.schemas import PersonalityScores

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def analyze_personality_with_llm(
    genres: list,
    mainstream_score: float,
    top_artists:list,
    diversity_scores: dict,
    content_features: dict,
    temporal_features: dict,
    grounding_context: str,
) -> dict:
    logger.info("Starting LLM Analysis")
    music_profile = {
        "genres": genres,
        "mainstream_score": mainstream_score,
        "top_artists": top_artists,
        "diversity": {
            "genre_count": diversity_scores["all_genres_count"],
            "genre_clusters": diversity_scores["genres_cluster_count"],
            "shannon_entropy": diversity_scores["shannon_entropy"]
        },
        "content": {
            "avg_song_length_min": content_features["average_song_length_min"],
            "explicit_ratio": content_features["explicit_ratio"],
            "avg_song_age": content_features["average_song_age"]
        },
        "listening_behaviour": {
            "frequency_per_day": temporal_features["listening_frequency"],
            "repeat_ratio": temporal_features["repeat_ratio"]
        }
    }
    
    prompt = f"""
    You are a music psychology expert. Analyze this person's music listening data and provide Big Five personality scores.
    
    Relevant scientific literature (retrieved for this user's genres):
    <retrieved_literature>
    {grounding_context}
    </retrieved_literature>   
    
    Music Profile:
    {json.dumps(music_profile, indent=2)}
    
    Analysis Guidelines (ordered by importance):

    1. GENRES & ARTISTS (highest weight):
    - Niche/experimental genres → High Openness
    - Diverse genres → High Openness
    - Mainstream pop → Higher Extraversion, Agreeableness
    - Electronic/abstract → High Openness, lower Agreeableness
    
    2. DIVERSITY METRICS:
    - High genre clusters (>10) → High Openness
    - High entropy (>0.8) → High Openness
    
    3. CONTENT FEATURES:
    - Older music (>10 years) → Higher Openness
    - Long songs (>5min) → Higher Openness
    
    4. LISTENING BEHAVIOR:
    - Listening behavior (repeat ratio, frequency) is not a reliable predictor of Big Five traits from music data. Use only as weak supporting context.
    
    5. MAINSTREAM SCORE (lowest weight):
    - Only use as tie-breaker or supporting evidence

    Important: Base your assessment primarily on the artist names and genres, not the mainstream score.    
    Calibration (highest priority):
    - Use the literature in <retrieved_literature> as your main source.
    - If there is a conflict between the guidelines and the literature, always prefer the literature.
    - Music data reliably predicts only Openness. For Conscientiousness, Agreeableness and Neuroticism the
      relationship is near zero, so keep those scores close to the neutral midpoint (~0.5) and express low
      confidence rather than guessing.

    Provide a score between 0.0 and 1.0 for each of the five traits, plus a short reasoning
    that cites the retrieved literature.
    """
    try:
        message = client.messages.parse(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages = [{"role": "user", "content": prompt}],
            output_format=PersonalityScores,
        )
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        
        input_costs = input_tokens * 0.000005
        output_costs = output_tokens * 0.000025
        total_costs = input_costs + output_costs
        logger.info(f"Cost: {total_costs}")
        
        scores = message.parsed_output
        
        
        return {
            **scores.model_dump(),
            "api_usage": {
                "model": "claude-opus-4-8",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "estimated_cost_usd": round(total_costs, 6)
            }
        }
    except Exception as e:
        logger.error(f'Analysis failed: {e}')
        raise
    
    
if __name__ == "__main__":

    test_dict ={
                
            "personality": {
                "test": "test"
            },
            "analysis_details": {
                "genres_found": [
                "classic rock",
                "german indie",
                "rock and roll",
                "lo-fi indie",
                "alternative metal",
                "neue deutsche welle",
                "german hip hop",
                "acid techno",
                "idm",
                "rap metal",
                "space music",
                "dream pop",
                "electronica",
                "trance",
                "rock",
                "rap rock",
                "eurodance",
                "drum and bass",
                "hard house",
                "german indie pop",
                "darkwave",
                "hypertechno",
                "hard rock",
                "nu metal",
                "downtempo",
                "cold wave",
                "cloud rap",
                "hard techno",
                "ambient"
                ],
                "artists_analyzed": 20,
                "mainstream_score": 0.79
            },
            "diversity": {
                "total_genre_count": 29,
                "genre_clusters": 17,
                "genre_cluster_dict": {
                "cluster_0": [
                    "electronica",
                    "eurodance"
                ],
                "cluster_1": [
                    "alternative metal",
                    "rap metal",
                    "rap rock",
                    "nu metal"
                ],
                "cluster_2": [
                    "acid techno",
                    "trance"
                ],
                "cluster_3": [
                    "darkwave",
                    "cold wave"
                ],
                "cluster_4": [
                    "classic rock",
                    "rock and roll",
                    "rock"
                ],
                "cluster_5": [
                    "drum and bass"
                ],
                "cluster_6": [
                    "ambient"
                ],
                "cluster_7": [
                    "hard house",
                    "hard rock",
                    "hard techno"
                ],
                "cluster_8": [
                    "neue deutsche welle"
                ],
                "cluster_9": [
                    "hypertechno"
                ],
                "cluster_10": [
                    "german indie",
                    "german hip hop",
                    "german indie pop"
                ],
                "cluster_11": [
                    "space music"
                ],
                "cluster_12": [
                    "dream pop"
                ],
                "cluster_13": [
                    "downtempo"
                ],
                "cluster_14": [
                    "idm"
                ],
                "cluster_15": [
                    "lo-fi indie"
                ],
                "cluster_16": [
                    "cloud rap"
                ]
                },
                "shannon_entropy": 0.942
            },
            "content_features": {
                "average_song_length_sec": 239.5,
                "average_song_length_min": 3.99,
                "explicit_ratio": 0.1,
                "average_song_age": 6.7,
                "average_popularity": 33.35
            },
            "recently_played": {
                "listening frequence": 29.2,
                "repeat_ratio": 0.08
            }
        }