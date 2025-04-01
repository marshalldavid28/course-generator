from flask import Flask, render_template, request
import openai
import os
from googleapiclient.discovery import build

openai.api_key = os.getenv("OPENAI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

def generate_curriculum(skill):
    prompt = f"""
    Create a 5-part beginner-friendly course outline for someone who wants to learn "{skill}".
    Each part should focus on a different major concept or skill area. Return only the section titles as a list.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    sections = response.choices[0].message.content.strip().split("\n")
    cleaned_sections = [s.lstrip("0123456789.- ") for s in sections if s.strip()]
    return cleaned_sections[:5]

def generate_search_query(skill, section_title):
    prompt = f"Generate a YouTube search query to find a high-quality tutorial video for the section: '{section_title}' in a course about '{skill}'."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def search_youtube(query):
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    search_response = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=5,
        type="video"
    ).execute()

    videos = []
    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        video_title = item["snippet"]["title"]

        stats = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()
        video_stats = stats["items"][0]["statistics"]
        views = int(video_stats.get("viewCount", 0))
        likes = int(video_stats.get("likeCount", 0))

        videos.append({
            "title": video_title,
            "url": f"https://youtube.com/watch?v={video_id}",
            "views": views,
            "likes": likes
        })

    # Sort by views and likes (engagement)
    videos.sort(key=lambda x: (x['views'], x['likes']), reverse=True)
    return videos

def generate_course(skill):
    outline = generate_curriculum(skill)
    course = []
    for section in outline:
        query = generate_search_query(skill, section)
        videos = search_youtube(query)
        top_video = videos[0] if videos else {"title": "No video found", "url": "#", "views": 0, "likes": 0}
        course.append({
            "section": section,
            "video_title": top_video['title'],
            "video_url": top_video['url'],
            "views": top_video['views'],
            "likes": top_video['likes']
        })
    return course

@app.route("/", methods=["GET", "POST"])
def index():
    course = []
    skill = ""
    if request.method == "POST":
        skill = request.form.get("skill")
        if skill:
            course = generate_course(skill)
    return render_template("index.html", course=course, skill=skill)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
