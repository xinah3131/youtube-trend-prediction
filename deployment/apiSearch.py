import re
import pandas as pd
from urllib.parse import urlparse, parse_qs
from preprocessText import preprocess
from googleapiclient.discovery import build
import isodate
import os

apiKeys = os.environ.get('API_KEY')
class YouTubeService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.service = build('youtube', 'v3', developerKey=api_key)
    
    def switch_api_key(self):
        current_key_index = apiKeys.index(self.api_key)
        next_key_index = (current_key_index + 1) % len(apiKeys)
        self.api_key = apiKeys[next_key_index]
        self.service = build('youtube', 'v3', developerKey=self.api_key)

# Initialize the YouTube service with the first API key
youtube = YouTubeService(apiKeys[2])

def get_next_api_key():
    current_key_index = apiKeys.index(youtube.api_key)
    next_key_index = (current_key_index + 1) % len(apiKeys)
    youtube.switch_api_key()
    return apiKeys[next_key_index]



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
            try:
                comments = video['statistics']['commentCount']
            except KeyError:
                comments = 0
            metadata = {
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'channel_title': video['snippet']['channelTitle'],
                'publish_date': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'views': video['statistics']['viewCount'],
                'likes': video['statistics']['likeCount'],
                'comments': comments,
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

def get_trending_videos(country_code):
    try:
        api_key = get_next_api_key()  # Replace with your own YouTube Data API key
        youtube = build('youtube', 'v3', developerKey=api_key)

        try:
            response = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                chart='mostPopular',
                regionCode=country_code,
                maxResults=10  # Adjust the number of videos you want to retrieve
            ).execute()

            trending_videos = []
            for item in response['items']:
                title = item['snippet']['title']
                description = item['snippet']['description'],
                channel_title = item['snippet']['channelTitle']
                publish_date = item['snippet']['publishedAt']
                duration = item['contentDetails']['duration']                
                views = item['statistics']['viewCount']
                try:
                    likes = item['statistics']['likeCount']
                except KeyError:
                    likes = "Hidden!"
                try:
                    comments = item['statistics']['commentCount']
                except KeyError:
                    comments = "Hidden!"
                category_id = item['snippet']['categoryId']
                thumbnail_link = item['snippet']['thumbnails']['default']['url']
                duration = isodate.parse_duration(duration)
                duration = duration.total_seconds()
                trending_videos.append({
                    'title': title,
                    'description':description,
                    'channel_title': channel_title,
                    'publish_date': publish_date,
                    'duration': duration,
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'category_id': category_id,
                    'thumbnail_link': thumbnail_link
                })
            df = pd.DataFrame(trending_videos)
            df['views'] = df['views'].astype(int)
            df['likes'] = df['likes'].astype(str)
            df['comments'] = df['comments'].astype(str)
            df['category_id'] = df['category_id'].astype(int)
            df['thumbnail_link'] = df['thumbnail_link'].str.replace('default.jpg', 'maxresdefault.jpg')
            return df

        except Exception as e:
            print('An error occurred:', str(e))
            return None
        
    except Exception as e:
        print("An error occurred:", str(e))

