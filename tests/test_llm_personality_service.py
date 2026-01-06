import json

from unittest.mock import patch, MagicMock
from backend.services.llm_personality_service import analyze_personality_with_llm
import pytest

@patch('backend.services.llm_personality_service.client') # Ersetzt Anthophic Client
def test_analyze_personality_with_llm(mock_client):
    # Mock input data 
    mock_genres = ["rock", "electronic"]
    mock_mainstream_score = 0.7
    mock_top_artists = ["Artist 1", "Artist 2"]
    mock_diversity_scores = {
        "all_genres_count": 10,
        "genres_cluster_count": 5,
        "shannon_entropy": 0.85
    }
    mock_content_features = {
        "average_song_length_min": 4.5,
        "explicit_ratio": 0.2,
        "average_song_age": 8.0
    }
    mock_temporal_features = {
        "listening_frequency": 15.0,
        "repeat_ratio": 0.3
    }
    
    # Mock Claude API Response
    mock_message = MagicMock() # leeres Fake Objekt
    mock_message.content = [ # Content setzen 
        MagicMock(text='```json\n{"openness": 0.8, "conscientiousness": 0.6, "extraversion": 0.7, "agreeableness": 0.5, "neuroticism": 0.4}\n```')
    ] # message.content[0].text gibt dieses Objekt

    # WICHTIG: usage ist ein Objekt mit Attributen!
    mock_message.usage.input_tokens = 500
    mock_message.usage.output_tokens = 100
    
    # Mock konfigurieren und aktivieren
    mock_client.messages.create.return_value = mock_message # Wenn client.messages.create() aufgerufen wird → gib mock_message zurück
    
    result = analyze_personality_with_llm(
        genres=mock_genres,
        mainstream_score=mock_mainstream_score,
        top_artists=mock_top_artists,
        diversity_scores=mock_diversity_scores,
        content_features=mock_content_features,
        temporal_features=mock_temporal_features
    )
    
    assert result["openness"] == 0.8
    assert result["conscientiousness"] == 0.6
    assert result["api_usage"]["input_tokens"] == 500
    assert result["api_usage"]["output_tokens"] == 100
    assert result["api_usage"]["estimated_cost_usd"] == round(500 * 0.000005 + 100 * 0.000025, 6)



# Claude wirft kaputtes Json 
@patch('backend.services.llm_personality_service.client')
def test_analyze_personality_with_llm_invalid_json(mock_client):
    # Mock input data 
    mock_genres = ["rock", "electronic"]
    mock_mainstream_score = 0.7
    mock_top_artists = ["Artist 1", "Artist 2"]
    mock_diversity_scores = {
        "all_genres_count": 10,
        "genres_cluster_count": 5,
        "shannon_entropy": 0.85
    }
    mock_content_features = {
        "average_song_length_min": 4.5,
        "explicit_ratio": 0.2,
        "average_song_age": 8.0
    }
    mock_temporal_features = {
        "listening_frequency": 15.0,
        "repeat_ratio": 0.3
    }
    
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='No valid json')]
    
    mock_message.usage.input_tokens = 500
    mock_message.usage.output_tokens = 100
    
    mock_client.messages.create.return_value = mock_message
    
    with pytest.raises(json.JSONDecodeError):
        analyze_personality_with_llm(
            genres=mock_genres,
            mainstream_score=mock_mainstream_score,
            top_artists=mock_top_artists,
            diversity_scores=mock_diversity_scores,
            content_features=mock_content_features,
            temporal_features=mock_temporal_features
        )
    
    
    
    
    
    
