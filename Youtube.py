from apiclient.discovery import build
from apiclient.errors import HttpError
from datetime import timedelta
from Video import Video
import re
import os

youtube = build('youtube', 'v3', developerKey=os.getenv('API_KEY'))

class Youtube:

  @staticmethod
  def get_videos (search, max_results):
    try:
      search_response = youtube.search().list(
        q=search,
        part="id,snippet",
        maxResults=max_results
      ).execute()

      videos = []

      for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
          # print(search_result)
          thumbnail = search_result['snippet']['thumbnails']['default']['url']
          video_response = youtube.videos().list(id=search_result['id']['videoId'], part="contentDetails, statistics").execute()

          hours_pattern = re.compile(r'(\d+)H')
          minutes_pattern = re.compile(r'(\d+)M')
          seconds_pattern = re.compile(r'(\d+)S')

          duration = video_response['items'][0]['contentDetails']['duration']

          if duration == 'P0D':
            continue

          views = video_response['items'][0]['statistics']['viewCount']
          likes = video_response['items'][0]['statistics']['likeCount']
          comments = video_response['items'][0]['statistics']['commentCount']
          
          hours = hours_pattern.search(duration)
          minutes = minutes_pattern.search(duration)
          seconds = seconds_pattern.search(duration)

          hours = int(hours.group(1)) if hours else 0
          minutes = int(minutes.group(1)) if minutes else 0
          seconds = int(seconds.group(1)) if seconds else 0

          video_seconds = timedelta(hours = hours, minutes = minutes, seconds = seconds).total_seconds()

          video_seconds = int(video_seconds)

          minutes, seconds = divmod(video_seconds, 60)
          hours, minutes = divmod(minutes, 60)

          if seconds < 10:
            str_seconds = f'0{seconds}'
          else:
            str_seconds = seconds
          
          if minutes < 10:
            str_minutes = f'0{minutes}'
          else:
            str_minutes = minutes
          
          if hours < 10:
            str_hours = f'0{hours}'
          else:
            str_hours = hours

          real_duration = f'{str_hours}:{str_minutes}:{str_seconds}'

          link = f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
          video = Video(search_result["snippet"]["title"], search_result["snippet"]["description"], link, thumbnail, real_duration, views, likes, comments)

          videos.append(video)
      
      return videos
    
    except:
      videos = []
      return videos