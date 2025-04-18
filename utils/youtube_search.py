import os
import requests
from dotenv import load_dotenv
import random

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_youtube(query, max_results=10):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    items = response.json().get("items", [])
    if not items:
        return None
    video_id = random.choice(items)["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={video_id}"