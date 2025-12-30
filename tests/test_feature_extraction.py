import pytest 
from backend.services.feature_extraction_service import (calculate_mainstream_score, 
                                                         calculate_diversity_score,
                                                         calculate_content_features,
                                                         calculate_average,
                                                         calculate_temporal_features)


def test_calculate_mainstream_score_basic():
    mock_response = {
        "items": [
            {
                "popularity": 80,
                "followers": {"total": 1000000}
            },
            {
                "popularity": 60,
                "followers": {"total": 500000}
            }
        ]
    }
    
    score = calculate_mainstream_score(mock_response)
    
    assert 0.0 <= score <= 1.0
    assert isinstance(score, float)
    
def test_calculate_mainstream_score_empty():
    mock_response = {}
    
    score = calculate_mainstream_score(mock_response)
    
    assert score == 0.5
    assert isinstance(score, float)
    
def test_calculate_diversity_score_basic():
    mock_response = {
        "items": [
            {
                "name": "AC/DC",
                "genres": ["rock", "hard rock"],
                "popularity": 80,
                "followers": {"total": 5000000}
            },
            {
                "name": "Daft Punk",
                "genres": ["electronic", "house"],
                "popularity": 75,
                "followers": {"total": 3000000}
            },
            {
                "name": "Kendrick Lamar",
                "genres": ["hip hop", "rap"],
                "popularity": 90,
                "followers": {"total": 8000000}
            },
            {
                "name": "Miles Davis",
                "genres": ["jazz"],
                "popularity": 70,
                "followers": {"total": 1000000}
            }
        ]
    }
    
    result = calculate_diversity_score(mock_response)
    
    assert isinstance(result, dict)
    assert result["all_genres_count"] > 0
    assert result["genres_cluster_count"] > 0
    assert 0.0 <= result["shannon_entropy"] >= 1.0
    assert result["artist_count"] == 4
    
def test_calculate_diversity_score_empty():
    mock_response = {
        "items": []
    }
    
    result = calculate_diversity_score(mock_response)
    
    assert result is None
     
def test_calculate_content_feature_basic():
    mock_response = {
        "items": [
            {
                "name": "Song 1",
                "explicit": True,
                "duration_ms": 240000,
                "popularity": 80,
                "album": {
                    "release_date": "2020-05-15"
                }
            },
            {
                "name": "Song 2",
                "explicit": False,
                "duration_ms": 180000,
                "popularity": 60,
                "album": {
                    "release_date": "2015-03-20"
                }
            }
        ]
    }
    
    result = calculate_content_features(mock_response)
    
    assert isinstance(result, dict)
    assert result["average_song_length_sec"] > 0
    assert result["average_song_length_min"] > 0
    assert 0.0 <= result["explicit_ratio"] <= 1.0
    assert result["average_song_age"] > 0
    assert result["average_popularity"] > 0
    
def test_calculate_content_features_empty():
    mock_response = {
        "items": []
    }
    
    result = calculate_content_features(mock_response)
    
    assert result is None
    
def test_calculate_average_basic():
    mock_values = [10,20,30,40]
    
    result = calculate_average(mock_values)
    
    assert result == 25.0
    


def test_calculate_average_empty():
    mock_values = []
    result = calculate_average(mock_values)
    
    assert result == 0.0
    
def test_calculate_average_single():
    mock_values = [10]
    result = calculate_average(mock_values)
    
    assert result == 10.0
    
def test_calculate_temporal_features_basic():
    mock_response = {
        "items": [
            {
                "track": {"id": "track1", "name": "Song 1"},
                "played_at": "2024-01-01T10:00:00.000Z"
            },
            {
                "track": {"id": "track2", "name": "Song 2"},
                "played_at": "2024-01-01T12:00:00.000Z"
            },
            {
                "track": {"id": "track1", "name": "Song 1"},
                "played_at": "2024-01-02T10:00:00.000Z"
            }
        ]
    }
    
    result = calculate_temporal_features(mock_response)
    
    assert isinstance(result, dict)
    assert result["listening_frequency"] > 0.0
    assert 0.0 <= result["repeat_ratio"] <= 1.0
    
def test_calculate_temporal_features_empty():
    mock_response = {
        "items": []
    }
    
    result = calculate_content_features(mock_response)
    
    assert result is None
