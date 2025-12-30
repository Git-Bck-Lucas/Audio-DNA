from anthropic import Anthropic
from backend.config import settings
import json
import re

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def analyze_personality_with_llm(
    genres: list,
    mainstream_score: float,
    top_artists:list,
    diversity_scores: dict,
    content_features: dict,
    temporal_features: dict
) -> dict:
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
    
    Scientific Basis:
    - Rentfrow & Gosling (2003): Genre preferences correlate with personality traits
    - Zweigenhaft (2008): Music preferences predict Openness to Experience
    - North (2010): Social aspects of music relate to Extraversion
    
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
    - Low diversity → Higher Conscientiousness
    
    3. CONTENT FEATURES:
    - Explicit content → Lower Agreeableness
    - Older music (>10 years) → Higher Conscientiousness, Openness
    - Long songs (>5min) → Higher Openness
    
    4. LISTENING BEHAVIOR:
    - High repeat ratio (>0.4) → Higher Conscientiousness
    - Very high frequency (>20/day) → Potential Neuroticism
    
    5. MAINSTREAM SCORE (lowest weight):
    - Only use as tie-breaker or supporting evidence

    Important: Base your assessment primarily on the artist names and genres, not the mainstream score.

    Return ONLY valid JSON with scores between 0.0-1.0:
    {{
    "openness": 0.0-1.0,
    "conscientiousness": 0.0-1.0,
    "extraversion": 0.0-1.0,
    "agreeableness": 0.0-1.0,
    "neuroticism": 0.0-1.0
    }}
    """
    
    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=1024,
        messages = [{"role": "user", "content": prompt}]
    )
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    
    input_costs = input_tokens * 0.000005
    output_costs = output_tokens * 0.000025
    total_costs = input_costs + output_costs
    
    response_text = message.content[0].text
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        personality_scores = json.loads(json_str)
        
        reasoning = response_text.split('```')[-1].strip()
        if reasoning.startswith('**Reasoning:**'):
            reasoning = reasoning.replace('**Reasoning:**', '').strip()
        else:
            personality_scores = json.loads(response_text)
            reasoning = None
    
    return {
        **personality_scores,
        "reasoning": reasoning,
        "api_usage": {
            "model": "claude-opus-4-5-20251101",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated_cost_usd": round(total_costs, 6)
        }
    }
    
    
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