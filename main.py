import openai
import os
from typing import List, Dict

# Set your OpenAI key (or use environment variable in production)
openai.api_key = os.getenv("OPENAI_API_KEY")  # <-- Make sure to set this in your env

### --- STEP 1: Generate Curriculum --- ###
def generate_curriculum(skill: str) -> List[str]:
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
    return cleaned_sections[:5]  # return only 5 sections


### --- STEP 2: Generate YouTube Search Query for Each Section --- ###
def generate_search_query(skill: str, section_title: str) -> str:
    prompt = f"Generate a YouTube search query to find a high-quality tutorial video for the section: '{section_title}' in a course about '{skill}'."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


### --- STEP 3: Search YouTube (TO DO: Integrate API or scraping here) --- ###
def search_youtube(query: str) -> List[Dict]:
    print(f"[MOCK SEARCH] Searching YouTube for: {query}")
    # Placeholder until YouTube API is added
    return [{
        "title": f"Best YouTube Video for: {query}",
        "url": f"https://youtube.com/watch?v=dummy_{query.replace(' ', '_')}",
        "views": 100000,
        "likes": 5000
    }]


### --- STEP 4: Assemble Final Course --- ###
def generate_course(skill: str) -> List[Dict]:
    outline = generate_curriculum(skill)
    course = []

    for section in outline:
        query = generate_search_query(skill, section)
        videos = search_youtube(query)
        top_video = videos[0]  # TODO: Add sorting logic later

        course.append({
            "section": section,
            "video_title": top_video['title'],
            "video_url": top_video['url'],
            "views": top_video['views'],
            "likes": top_video['likes']
        })

    return course


### --- Test Run --- ###
if __name__ == "__main__":
    skill_input = input("Enter a skill you want to learn: ")
    final_course = generate_course(skill_input)

    print("\nYour Free Course:\n")
    for i, item in enumerate(final_course, 1):
        print(f"{i}. {item['section']}")
        print(f"   Video: {item['video_title']}\n   {item['video_url']}\n")
