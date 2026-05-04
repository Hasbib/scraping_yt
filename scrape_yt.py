from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import os

API_KEY = "AIzaSyBhNJUEN5loUvBEKOajdDCPod7aqUlFgiI"
youtube = build("youtube", "v3", developerKey=API_KEY)


def get_video_info(video_id):
    res = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()
    item = res["items"][0]
    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "channel_id": item["snippet"]["channelId"],
        "published": item["snippet"]["publishedAt"],
        "views": item["statistics"].get("viewCount"),
        "likes": item["statistics"].get("likeCount"),
        "comments_count": item["statistics"].get("commentCount"),
    }


def get_channel_info(channel_id):
    res = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    ).execute()
    item = res["items"][0]
    return {
        "channel_name": item["snippet"]["title"],
        "subscribers": item["statistics"].get("subscriberCount"),
        "total_videos": item["statistics"].get("videoCount"),
        "total_views": item["statistics"].get("viewCount"),
    }


def get_comments(video_id, max_results=100):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=min(max_results, 100)
    )
    while request and len(comments) < max_results:
        res = request.execute()
        for item in res["items"]:
            c = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": c["authorDisplayName"],
                "text": c["textDisplay"],
                "likes": c["likeCount"],
                "published": c["publishedAt"],
            })
        request = youtube.commentThreads().list_next(request, res)
    return comments


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["id", "en"])
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        return f"Transcript tidak tersedia: {e}"


# ── MAIN ──────────────────────────────────────────
VIDEO_ID = "hn2oSlBEMHI"  # ✅ ganti video ID di sini

video      = get_video_info(VIDEO_ID)
channel    = get_channel_info(video["channel_id"])
comments   = get_comments(VIDEO_ID, max_results=200)
transcript = get_transcript(VIDEO_ID)

# Buat folder per video
version = 1
while os.path.exists(f"hasil_v{version}_{VIDEO_ID}"):
    version += 1
    
folder = f"hasil_v{version}_{VIDEO_ID}"
os.makedirs(folder, exist_ok=True)

# Simpan semua file
pd.DataFrame([video]).to_csv(f"{folder}/video_info.csv", index=False)
pd.DataFrame([channel]).to_csv(f"{folder}/channel_info.csv", index=False)
pd.DataFrame(comments).to_csv(f"{folder}/comments.csv", index=False)

with open(f"{folder}/transcript.txt", "w", encoding="utf-8") as f:
    f.write(transcript)

print(f"✅ Semua data disimpan di folder: {folder}/")