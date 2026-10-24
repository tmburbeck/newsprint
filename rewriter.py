import hashlib
import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = "cache.json"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def pick_lead_story(articles):
    if not articles:
        return None

    headlines = "\n".join(
        [f"{i + 1}. [{a['source']}] {a['title']}" for i, a in enumerate(articles)]
    )

    key = hashlib.md5(headlines.encode()).hexdigest()
    cache = load_cache()

    cached = cache.get(key)
    if isinstance(cached, int) and 0 <= cached < len(articles):
        return articles[cached]

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

    match = re.search(r"\d+", message.content[0].text)
    index = int(match.group()) - 1 if match else 0
    if not (0 <= index < len(articles)):
        index = 0

    cache[key] = index
    save_cache(cache)
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