import re
import pandas as pd
from urllib.parse import urlparse, parse_qs
from preprocessText import preprocess
from googleapiclient.discovery import build
import isodate
import os

api_keys = os.environ.get('API_KEY')
current_key_index = 0  # Declare current_key_index as a global variable

def get_video_id(url):
    video_id = None
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if parsed_url.netloc == 'youtu.be':
        video_id = parsed_url.path[1:]
    elif parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
        if 'v' in query_params:
            video_id = query_params['v'][0]
    return video_id

def get_next_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(api_keys)
    return api_keys[current_key_index]

def get_video_metadata(video_id):
    try:
        # Get the next API key
        api_key = get_next_api_key()

        # Set up the YouTube Data API client
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Call the API to retrieve video metadata
        response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()

        # Extract the relevant metadata
        if 'items' in response and len(response['items']) > 0:
            video = response['items'][0]
            metadata = {
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'channel_title': video['snippet']['channelTitle'],
                'publish_date': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'views': video['statistics']['viewCount'],
                'likes': video['statistics']['likeCount'],
                'comments': video['statistics']['commentCount'],
                'category_id': video['snippet']['categoryId'],
                'thumbnail_link': video['snippet']['thumbnails']['default']['url']
            }
            return metadata

    except Exception as e:
        print("An error occurred:", str(e))

    return None

def get_metadata(url):
    # Set up the YouTube Data API client
    video_id = get_video_id(url)
    metadata = get_video_metadata(video_id)
    if metadata is not None:
        # Create a DataFrame from the metadata
        df = pd.DataFrame([metadata])
        df['duration'] = df['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())
        df['cleanTitle'] = df['title'].apply(preprocess)
        df['cleanTitle'] = df['cleanTitle'].apply(lambda x: ' '.join(x))
        df['titleLength'] = df['title'].apply(lambda x: len(x))
        df['descriptionLength'] = df['description'].apply(lambda x: len(x))
        df['thumbnail_link'] = df['thumbnail_link'].str.replace('default.jpg', 'maxresdefault.jpg')
        return df
    else: 
        return 0

