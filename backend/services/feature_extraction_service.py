import math 
from collections import Counter
import json
from datetime import datetime

from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances

from backend.services.spotify_data_helpers import (
    extract_artist_popularities, 
    extract_follower_counts, 
    extract_genres_from_artists,
    extract_track_data,
    extract_recently_played_data
)

# Global Model
#sentence_transformer_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
sentence_transformer_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

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
    follower_score = math.log10(average_follower_count + 1) / 6.0 # evtl. später überarbeiten
    follower_score = min(follower_score, 1.0)
    
    # Combine and Return 
    mainstream_score = (average_popularity / 100 + follower_score) / 2 #später evtl. mit Gewichtungen arbeiten
    return round(mainstream_score, 2)

def cluster_genres_by_similarity(genres: list) -> dict:
    """

    Args:
        genres (list): List of genres

    Returns:
        int: Number of Genre Clusters
    """
    # Context String 
    context_genres = [f"{genre} music genre"for genre in genres]
    embeddings = sentence_transformer_model.encode(context_genres)
    
    dist_matrix = cosine_distances(embeddings)
    
    agg = AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=0.33,
    metric='precomputed',
    linkage="average"
    )
    
    labels_agg =agg.fit_predict(dist_matrix)
    cluster_dict = {}
    for label in set(labels_agg):
        items = [g for g, l in zip(genres, labels_agg) if l == label]
        cluster_dict[f"cluster_{int(label)}"] = items
    
    #return(len(set(labels_agg))) # Unte
    return {
        "number_genres": len(set(labels_agg)),
        "genres_cluster_dict": cluster_dict
    }
    
    
    
def calculate_diversity_score(top_artists_response: dict) -> dict:
    """

    Args:
        top_artists_response (dict): Spotify Top artists Response

    Returns:
        dict: Diversity Scores
    """
    all_genres = extract_genres_from_artists(top_artists_response)
    
    if len(all_genres) == 0:
        return None
    
    cluster_result = cluster_genres_by_similarity(all_genres)
    
    # Shanon entropy 
    
    all_genres_with_duplicates = extract_genres_from_artists(top_artists_response, unique=False)
    genre_counter = Counter(all_genres_with_duplicates)
    total = len(all_genres_with_duplicates)
    
    probabilities = [count/total for count in genre_counter.values()]
    shannon_entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    
    # Normalization 
    max_entropy = math.log2(len(genre_counter)) if len(genre_counter) > 0 else 1
    normalized_entropy = shannon_entropy / max_entropy if max_entropy > 0 else 0
    
    
    return {
        "all_genres": all_genres,
        "all_genres_count": len(all_genres),
        "genres_cluster_count": cluster_result["number_genres"],
        "artist_count": len(top_artists_response['items']),  # ← NEU
        "genre_cluster_dict": cluster_result["genres_cluster_dict"],
        "shannon_entropy": round(normalized_entropy, 3)
    }
    
def calculate_average(values: list) -> float:
    return sum(values)/len(values) if len(values) > 0 else 0.0
    
    
def calculate_content_features(top_tracks_response: dict) -> dict:
    track_data = extract_track_data(top_tracks_response)
    if len(track_data) == 0:
        return None

    explicit_count = sum(1 for data in track_data.values() if data['explicit'])
    explicit_ratio = explicit_count/len(track_data)
    # Average Song Length
    durations = [data['duration_ms'] for data in track_data.values()]
    average_song_length_ms = calculate_average(durations)
    # Music Age (Durchschnittsalter der Songs)
    track_ages = [int(datetime.now().strftime('%Y')) - int(data['release_date'].split('-')[0]) for data in track_data.values()]
    average_song_age = calculate_average(track_ages)
    # Track Popularity Average
    popularities = [data['popularity'] for data in track_data.values()]
    average_popularity = calculate_average(popularities)
    
    return {
         "average_song_length_sec": round(average_song_length_ms / 1000, 1),
        "average_song_length_min": round(average_song_length_ms / 60_000, 2),
        "explicit_ratio": round(explicit_ratio, 2),
        "average_song_age": round(average_song_age, 2),
        "average_popularity": round(average_popularity, 2)
    }
    
def calculate_temporal_features(recently_played_response: dict) -> dict:
    recently_played_data = extract_recently_played_data(recently_played_response)
    if not recently_played_data or len(recently_played_data) == 0:
        return None
    
    all_time_stamps = [timestamp for data in recently_played_data.values() for timestamp in data['played_at']]
    if len(all_time_stamps) == 0:
        return None
    max_played_at = datetime.strptime(max(all_time_stamps), '%Y-%m-%dT%H:%M:%S.%fZ')
    min_played_at = datetime.strptime(min(all_time_stamps), '%Y-%m-%dT%H:%M:%S.%fZ')
    diff = max_played_at - min_played_at
    # Repeat Behavior berechnen

    unique_tracks = list(set(recently_played_data.keys()))
    total_plays = len(all_time_stamps)
    total_days = diff.total_seconds() / 86400
    #metrics
    listining_frequency = total_plays/total_days if total_plays > 0 and total_days > 0 else 0
    repeat_ratio = (total_plays - len(unique_tracks)) / total_plays if total_plays > 0  else 0
    
    return {
        "listining_frequency": listining_frequency,
        "repeat_ratio": repeat_ratio,
    }
    
    
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
    
    # calculate_mainstream_score(mock_top_artists)
    
    example_genres = ['rock', 'pop', 'acid techno', 'techno', 'trance', 'metal', 'rap', 'hip hop', 'trance']
    
    print(cluster_genres_by_similarity(example_genres))