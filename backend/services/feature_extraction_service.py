import math 
import json
from backend.services.spotify_data_helpers import (
    extract_artist_popularities, 
    extract_follower_counts, 
    extract_genres_from_artists
)

def calculate_mainstream_score(top_artists_response:dict) -> float:
    """
    Calculate Mainstream Score based on Popularity Score and Number of Followers. 
    
    Args: Spotify Top Artists Response
    
    Returns: Floatscore between 0.0 (Niche) and 1.0 (Mainstream)
    """
    print()
    if not top_artists_response.get('items') or len(top_artists_response['items']) == 0:
        return 0.5 # neutral
    
    # Extract Data mit Helper Functions 
    popularities = extract_artist_popularities(top_artists_response)
    follower_counts = extract_follower_counts(top_artists_response)
    
    # Calculate Average Popularity 
    average_popularity = math.fsum(popularities)/len(popularities)
    
    # Calculate Average Followers 
    average_follower_count = math.fsum(follower_counts)/len(follower_counts)
    
    # Normalize Follower Score --> Log Scale 
    follower_score = math.log10(average_follower_count + 1) / 6.0
    follower_score = min(follower_score, 1.0)
    
    # Combine and Return 
    mainstream_score = (average_popularity / 100 + follower_score) / 2 #später evtl. mit Gewichtungen arbeiten
    return round(mainstream_score, 2)
    
    
if __name__ == '__main__':
    
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
    
    
    # extracted_genres = extract_genres_from_artists(mock_top_artists)
    
    calculate_mainstream_score(mock_top_artists)