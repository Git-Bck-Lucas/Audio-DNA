from collections import defaultdict
import json
from backend.services.spotify_data_helpers import extract_genres_from_artists

GENRES_PERSONALITY_MAP = {
    "rock": { # Beispielwerte, wichtig hier ist, diesen Teil mit wissenschaftlichen Papern zu begründen
        "openness": 0.8, # 0 niedrig bis 1 hoch
        "conscientiousness": 0.5,
        "extraversion": 0.7,
        "agreeableness": 0.4,
        "neuroticism": 0.6
    },
    "pop": {
        "openness": 0.5,
        "conscientiousness": 0.6,
        "extraversion": 0.8,
        "agreeableness": 0.7,
        "neuroticism": 0.4
    },
    "techno": {
        "openness": 0.9,
        "conscientiousness": 0.6,
        "extraversion": 0.5,
        "agreeableness": 0.4,
        "neuroticism": 0.7
    }
}


def calulate_personality_from_genres(genres: list) -> dict:
    """

    Args:
        genres (list): List of Music Genres 

    Returns:
        dict: Dictionary with average Big 5 Scores based on Music Genres
    """
    if not genres:
        return {}
    TRAITS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
    # Dictionary Comprehenision 
    personality_dict = {trait: 0.0 for trait in TRAITS}
    matched_genres_count = 0
    for genre in genres:
        if genre in GENRES_PERSONALITY_MAP:
            matched_genres_count += 1
            print("Genre: ", genre)
            for key in GENRES_PERSONALITY_MAP[genre].keys():
                personality_dict[key] += GENRES_PERSONALITY_MAP[genre][key]
    if matched_genres_count == 0:
        return {} 
    for key in personality_dict.keys():
        personality_dict[key] = round(personality_dict[key]/matched_genres_count, 3)
    return personality_dict
    
        
if __name__ == "__main__":
    
    #genres = ['techno', 'pop', 'rap']
    
    #result = calulate_personality_from_genres(genres)
    
    #print(result)
    
    # Mock Spotify Response (realistisch!)
    # Hierher echten Spotify Response kopieren, besser zum testen
    mock_top_artists_string = """
    {
        "items": [
            {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/67lytN32YpUxiSeWlKfHJ3"
            },
            "followers": {
                "href": null,
                "total": 1162603
            },
            "genres": [
                "cloud rap"
            ],
            "href": "https://api.spotify.com/v1/artists/67lytN32YpUxiSeWlKfHJ3",
            "id": "67lytN32YpUxiSeWlKfHJ3",
            "images": [
                {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb9203ea92f4c538f41e6eea8c",
                "width": 640
                },
                {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051749203ea92f4c538f41e6eea8c",
                "width": 320
                },
                {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1789203ea92f4c538f41e6eea8c",
                "width": 160
                }
            ],
            "name": "Yung Lean",
            "popularity": 67,
            "type": "artist",
            "uri": "spotify:artist:67lytN32YpUxiSeWlKfHJ3"
            },
            {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/5APEQlUaQ5K70LgPqAdTuU"
            },
            "followers": {
                "href": null,
                "total": 99780
            },
            "genres": [
                "dream pop",
                "lo-fi indie"
            ],
            "href": "https://api.spotify.com/v1/artists/5APEQlUaQ5K70LgPqAdTuU",
            "id": "5APEQlUaQ5K70LgPqAdTuU",
            "images": [
                {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb32571710adedb8524a42ac48",
                "width": 640
                },
                {
                "height": 320,
                "url": "https://i.scdn.co/image/ab6761610000517432571710adedb8524a42ac48",
                "width": 320
                },
                {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f17832571710adedb8524a42ac48",
                "width": 160
                }
            ],
            "name": "Night Tapes",
            "popularity": 59,
            "type": "artist",
            "uri": "spotify:artist:5APEQlUaQ5K70LgPqAdTuU"
            },
            {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/4cWhaaPUsxFe3z7fPNfzwL"
            },
            "followers": {
                "href": null,
                "total": 7980
            },
            "genres": [
                "hard house",
                "eurodance",
                "trance",
                "hypertechno",
                "hard techno",
                "acid techno"
            ],
            "href": "https://api.spotify.com/v1/artists/4cWhaaPUsxFe3z7fPNfzwL",
            "id": "4cWhaaPUsxFe3z7fPNfzwL",
            "images": [
                {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb0e926b63345d8d9b506f9250",
                "width": 640
                },
                {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051740e926b63345d8d9b506f9250",
                "width": 320
                },
                {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1780e926b63345d8d9b506f9250",
                "width": 160
                }
            ],
            "name": "Arman John",
            "popularity": 34,
            "type": "artist",
            "uri": "spotify:artist:4cWhaaPUsxFe3z7fPNfzwL"
            }
    ]}
    """
    
    mock_top_artists = json.loads(mock_top_artists_string)
    
    
    extracted_genres = extract_genres_from_artists(mock_top_artists)
    
    print(extracted_genres)