import json

def extract_genres_from_artists(top_artists_response: dict, unique = True) -> list:
    all_genres = []
    for artist in top_artists_response['items']: # Greife auf die Liste des Dicts zu und iteriere über diese
        artist_genres = artist['genres']
        all_genres.extend(artist_genres)
    
    if unique == True:
        unique_genres = list(set(all_genres))
        
        return unique_genres
    
    return all_genres


def extract_artist_popularities(top_artists_response: dict) -> list:
    all_popularity_scores = []
    for artist in top_artists_response['items']:
        all_popularity_scores.append(artist['popularity'])
    
    return all_popularity_scores
    
    
def extract_follower_counts(top_artists_response: dict) -> list:
    all_follower_counts = []
    for artist in top_artists_response['items']:
        all_follower_counts.append(artist['followers']['total'])
    
    return all_follower_counts
        
    
    
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
    
    follower_counts = extract_follower_counts(mock_top_artists)
    
    print(follower_counts)