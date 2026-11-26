"""Fetches the latest headlines from each news outlet's RSS feed."""

import html
import re

import feedparser

# Outlet name -> RSS feed URL.
FEEDS = {
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "The Hill": "https://thehill.com/feed/",
}

# Matches any HTML tag, e.g. <p> or <a href="...">.
HTML_TAG = re.compile(r"<[^>]+>")


def get_articles(max_per_feed=5):
    """Returns up to `max_per_feed` recent articles from every feed, as a list of dicts.

    A feed that is down or returns nothing is skipped, so one broken
    outlet doesn't take the whole front page down with it.
    """
    articles = []

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"[feeds] No articles from {source} ({url})")
            continue

        for entry in feed.entries[:max_per_feed]:
            articles.append({
                "source": source,
                "title": entry.get("title", "Untitled"),
                "summary": clean_summary(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
            })

    return articles


def clean_summary(raw_summary):
    """Turns a feed's HTML summary into plain text (e.g. '<p>Rock &amp; roll</p>' -> 'Rock & roll')."""
    without_tags = HTML_TAG.sub("", raw_summary)
    return html.unescape(without_tags).strip()
