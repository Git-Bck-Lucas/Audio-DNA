import pytest
from httpx import AsyncClient, ASGITransport # Http Client für API Tests
from unittest.mock import patch, MagicMock  # Ersetzt Funktionen/Objekte temporär
from backend.main import app
from backend.api.dependencies import get_current_user  # zum Überschreiben im Test
from backend.api.rate_limit import _hits, MAX_REQUESTS


@pytest.fixture
def authenticated_user():
    """Simuliert einen eingeloggten User, ohne echten Cookie/Session-Flow.

    setup (vor yield): Auth-Dependency durch einen Fake ersetzen -> jeder
        Depends(get_current_user) bekommt diesen MagicMock statt echter Prüfung.
    teardown (nach yield): Override wieder entfernen, damit er nicht in andere
        Tests leckt. Läuft auch dann, wenn der Test mit AssertionError abbricht.
    """
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=1)
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def reset_rate_limit():
    _hits.clear()
    yield
    _hits.clear()
    

@pytest.mark.asyncio # sagt pytest: Das ist ein async test
@patch('backend.api.v1.analysis.get_valid_access_token') # Ersetzt Token-Holen/Refresh
@patch('backend.api.v1.analysis.format_grounding_context')
@patch('backend.api.v1.analysis.retrieve_grounding_context')
@patch('backend.api.v1.analysis.create_analysis')
@patch('backend.api.v1.analysis.Spotify') # Ersetzt spotify klasse
@patch('backend.api.v1.analysis.analyze_personality_with_llm') # Ersetzt LLM Funktion
async def test_get_personality_endpoint_success(mock_llm, mock_spotify_class, mock_create_analysis, mock_retrieve, mock_format, mock_get_valid_token, authenticated_user):
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
    mock_get_valid_token.return_value = "test_token" # gueltiger Token, Refresh-Logik wird separat getestet
    mock_create_analysis.return_value = MagicMock(id=1, user_id=1, result={}, created_at="2024-01-01")

    # Retrieval mitmocken: sonst laueft der Endpoint echtes pgvector-SQL gegen SQLite (CI) und crasht.
    mock_retrieve.return_value = []
    mock_format.return_value = ""

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
        response = await client.get("/api/v1/analysis/get_personality")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["user_id"] == 1
    assert data["result"] == {}
    assert "created_at" in data

@pytest.mark.asyncio
@patch('backend.api.v1.analysis.get_valid_access_token')
@patch('backend.api.v1.analysis.format_grounding_context')
@patch('backend.api.v1.analysis.retrieve_grounding_context')
@patch('backend.api.v1.analysis.create_analysis')
@patch('backend.api.v1.analysis.Spotify')
@patch('backend.api.v1.analysis.analyze_personality_with_llm')
async def test_rate_limit_returns_429(mock_llm, mock_spotify_class, mock_create_analysis, mock_retrieve, mock_format, mock_get_valid_token, authenticated_user, reset_rate_limit):
    """Nach MAX_REQUESTS erlaubten Calls muss der nächste 429 liefern."""
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
    mock_get_valid_token.return_value = "test_token" # gueltiger Token, Refresh-Logik wird separat getestet
    mock_create_analysis.return_value = MagicMock(id=1, user_id=1, result={}, created_at="2024-01-01")

    # Retrieval mitmocken: sonst laueft der Endpoint echtes pgvector-SQL gegen SQLite (CI) und crasht.
    mock_retrieve.return_value = []
    mock_format.return_value = ""

    mock_llm.return_value = {
        "openness": 0.8,
        "conscientiousness": 0.6,
        "extraversion": 0.7,
        "agreeableness": 0.5,
        "neuroticism": 0.4,
        "reasoning": "Test reasoning"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        statuses = []
        for _ in range(MAX_REQUESTS + 1):          # 5 erlaubte + 1 zu viel
            resp = await client.get("/api/v1/analysis/get_personality")
            statuses.append(resp.status_code)

    assert statuses[:MAX_REQUESTS] == [200] * MAX_REQUESTS   # erste 5 ok
    assert statuses[MAX_REQUESTS] == 429                     # der 6. abgewiesen

