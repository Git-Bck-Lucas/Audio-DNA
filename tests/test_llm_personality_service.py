from unittest.mock import patch, MagicMock
from backend.services.llm_personality_service import analyze_personality_with_llm
from backend.api.v1.schemas import PersonalityScores, TraitScore


@patch('backend.services.llm_personality_service.client')  # Ersetzt Anthropic Client
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
    mock_grounding_context = (
        "[Schaefer & Mehlhorn, Schaefer_Mehlhorn_2017] Openness to Experience is the most "
        "reliable predictor of musical taste, correlating with a preference for sophisticated "
        "music such as classical and jazz (r ≈ .15–.21). Conscientiousness, Agreeableness and "
        "Neuroticism show near-zero, non-replicating correlations with music.\n\n"
        "[Rentfrow & Gosling, Rentfrow_Gosling_2003] Openness loads strongly on the Reflective "
        "and Complex dimension; Extraversion relates to Energetic and Rhythmic (contemporary) music."
    )

    # Mock Claude API Response. Structured Outputs: parse() liefert parsed_output als
    # validierte PersonalityScores-Instanz.
    mock_message = MagicMock()
    mock_message.parsed_output = PersonalityScores(
        openness=TraitScore(score=0.8, confidence="high", reasoning="Test reasoning"),
        conscientiousness=TraitScore(score=0.6, confidence="low", reasoning="Test reasoning"),
        extraversion=TraitScore(score=0.7, confidence="medium", reasoning="Test reasoning"),
        agreeableness=TraitScore(score=0.5, confidence="low", reasoning="Test reasoning"),
        neuroticism=TraitScore(score=0.4, confidence="low", reasoning="Test reasoning"),
        summary="Test summary",
    )
    mock_message.usage.input_tokens = 500
    mock_message.usage.output_tokens = 100

    mock_client.messages.parse.return_value = mock_message

    result = analyze_personality_with_llm(
        genres=mock_genres,
        mainstream_score=mock_mainstream_score,
        top_artists=mock_top_artists,
        diversity_scores=mock_diversity_scores,
        content_features=mock_content_features,
        temporal_features=mock_temporal_features,
        grounding_context=mock_grounding_context,
    )

    assert result["openness"]["score"] == 0.8
    assert result["openness"]["confidence"] == "high"
    assert result["conscientiousness"]["score"] == 0.6
    assert result["mode"] == "science"  # Default-Modus, wenn nicht übergeben
    assert result["api_usage"]["input_tokens"] == 500
    assert result["api_usage"]["output_tokens"] == 100
    assert result["api_usage"]["estimated_cost_usd"] == round(500 * 0.000005 + 100 * 0.000025, 6)
