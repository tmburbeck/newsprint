"""Uses Claude to pick the lead story and rewrite headlines in a 1920s style.

Every answer from Claude is saved to cache.json, so each headline is only
ever sent to the API once. If the API can't be used (no key, no internet,
rate limit), the app falls back to the original headlines instead of crashing.
"""

import hashlib
import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()  # reads ANTHROPIC_API_KEY from the .env file

MODEL = "claude-sonnet-4-6"
CACHE_FILE = "cache.json"

API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY) if API_KEY else None

if client is None:
    print("[rewriter] ANTHROPIC_API_KEY is not set - showing original headlines.")


# ---- Cache ------------------------------------------------------------------
# cache.json holds two lookup tables:
#   "lead":      fingerprint of the current headline list -> index of the lead story
#   "headlines": fingerprint of an original headline      -> its 1920s rewrite


def load_cache():
    """Reads cache.json, or returns an empty cache if it's missing or unreadable."""
    empty = {"lead": {}, "headlines": {}}
    if not os.path.exists(CACHE_FILE):
        return empty

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (json.JSONDecodeError, OSError):
        return empty

    # Anything that isn't the expected shape (e.g. an older format) is ignored.
    if not isinstance(cache, dict) or not isinstance(cache.get("lead"), dict) \
            or not isinstance(cache.get("headlines"), dict):
        return empty
    return cache


def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def fingerprint(text):
    """A short, stable ID for a piece of text, used as a cache key."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---- Talking to Claude ------------------------------------------------------


def ask_claude(prompt, max_tokens):
    """Sends one prompt to Claude and returns the text reply, or None if the API isn't available."""
    if client is None:
        return None

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as error:
        print(f"[rewriter] Claude API request failed: {error}")
        return None

    return message.content[0].text.strip()


# ---- Functions used by app.py -----------------------------------------------


def pick_lead_story(articles, cache):
    """Asks Claude which article is most newsworthy. Falls back to the first article."""
    numbered_headlines = "\n".join(
        f"{number}. [{article['source']}] {article['title']}"
        for number, article in enumerate(articles, start=1)
    )
    key = fingerprint(numbered_headlines)

    if key not in cache["lead"]:
        reply = ask_claude(
            "You are a seasoned newspaper editor. Given these headlines, reply with only "
            f"the number of the single most newsworthy story:\n\n{numbered_headlines}",
            max_tokens=100,
        )
        if reply is None:
            return articles[0]

        # Claude replies with a number like "7"; convert it to a list position.
        match = re.search(r"\d+", reply)
        index = int(match.group()) - 1 if match else 0
        cache["lead"][key] = index if 0 <= index < len(articles) else 0

    return articles[cache["lead"][key]]


def rewrite_headline(title, cache):
    """Returns the headline rewritten in 1920s style, or the original if Claude isn't available."""
    key = fingerprint(title)

    if key not in cache["headlines"]:
        rewritten = ask_claude(
            "Rewrite this modern news headline in the dramatic style of a 1920s newspaper "
            "headline. Use period-appropriate language, be punchy and theatrical. Reply with "
            f"only the rewritten headline, nothing else.\n\nOriginal: {title}",
            max_tokens=60,
        )
        if rewritten is None:
            return title
        cache["headlines"][key] = rewritten

    return cache["headlines"][key]
