import pytest 
from httpx import AsyncClient, ASGITransport # Http Client für API Tests
from unittest.mock import patch, MagicMock  # Ersetzt Funktionen/Objekte temporär
from backend.main import app

@pytest.mark.asyncio # sagt pytest: Das ist ein async test
@patch('backend.api.v1.analysis.Spotify') # Ersetzt spotify klasse
@patch('backend.api.v1.analysis.analyze_personality_with_llm') # Ersetzt LLM Funktion
async def test_get_personality_endpoint_success(mock_llm, mock_spotify_class):
    """Test erfolgreicher API Call mit gemockten Spotify Daten"""
    # simuliert spotify api response
    mock_artists = {
        "items": [
            {
                "name": "AC/DC",
                "genres": ["rock", "hard rock"],
                "popularity": 80,
                "followers": {"total": 5000000}
            }
        ]
    }
    
    mock_tracks = {
        "items": [
            {
                "name": "Song 1",
                "explicit": False,
                "duration_ms": 240000,
                "popularity": 80,
                "album": {"release_date": "2020-05-15"}
            }
        ]
    }
    
    mock_recently_played = {
        "items": [
            {
                "track": {"id": "track1", "name": "Song 1"},
                "played_at": "2024-01-01T10:00:00.000Z"
            }
        ]
    }
    
    mock_spotify_instance = MagicMock() # Fake spotify object, hat automatisch alle Methoden/Attribute die du brauchst
    mock_spotify_instance.current_user_top_artists.return_value = mock_artists
    mock_spotify_instance.current_user_top_tracks.return_value = mock_tracks
    mock_spotify_instance.current_user_recently_played.return_value = mock_recently_played
    mock_spotify_class.return_value = mock_spotify_instance
    
    mock_llm.return_value = {
        "openness": 0.8,
        "conscientiousness": 0.6,
        "extraversion": 0.7,
        "agreeableness": 0.5,
        "neuroticism": 0.4,
        "reasoning": "Test reasoning"
    }
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/v1/analysis/get_personality",
            params={"access_token": "test_token"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "personality" in data
    assert data["personality"]["openness"] == 0.8
