import json
import hashlib

CACHE_FILE = "cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def pick_lead_story(articles):
    headlines = "\n".join(
        [f"{i + 1}. [{a['source']}] {a['title']}" for i, a in enumerate(articles)]
    )

    key = hashlib.md5(headlines.encode()).hexdigest()
    cache = load_cache()

    if key in cache:
        index = cache[key]
        return articles[index]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"You are a seasoned newspaper editor. Given these headlines, reply with only the number of the single most newsworthy story:\n\n{headlines}"
            }
        ]
    )

    response = message.content[0].text.strip()
    index = int(''.join(filter(str.isdigit, response))) - 1
    cache[key] = index
    save_cache(cache)
    return articles[index]

    response = message.content[0].text.strip()
    index = int(''.join(filter(str.isdigit, response))) - 1
    return articles[index]

def rewrite_headline(title, source):
    cache = load_cache()
    key = hashlib.md5(title.encode()).hexdigest()

    if key in cache:
        return cache[key]

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=60,
        messages=[
            {
                "role": "user",
                "content": f"Rewrite this modern news headline in the dramatic style of a 1920s newspaper headline. Use period-appropriate language, be punchy and theatrical. Reply with only the rewritten headline, nothing else.\n\nOriginal: {title}"
            }
        ]
    )

    rewritten = message.content[0].text.strip()
    cache[key] = rewritten
    save_cache(cache)
    return rewritten