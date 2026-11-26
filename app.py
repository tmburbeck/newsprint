"""The Daily Newsprint: a Flask app that serves today's news as a 1920s broadsheet."""

from flask import Flask, render_template

from feeds import get_articles
from rewriter import load_cache, pick_lead_story, rewrite_headline, save_cache

app = Flask(__name__)


@app.route("/")
def front_page():
    # 1. Gather the latest articles from every outlet.
    articles = get_articles()
    if not articles:
        return "No stories available right now. Check the RSS feeds.", 503

    # 2. Pick the lead story (chosen from the original, un-rewritten headlines).
    cache = load_cache()
    lead = pick_lead_story(articles, cache)
    other_articles = [article for article in articles if article is not lead]

    # 3. Rewrite every headline in 1920s style.
    for article in articles:
        article["title"] = rewrite_headline(article["title"], cache)

    # 4. Save any new answers from Claude so the next visit is instant.
    save_cache(cache)

    return render_template("index.html", lead=lead, articles=other_articles)


if __name__ == "__main__":
    app.run(debug=True)
