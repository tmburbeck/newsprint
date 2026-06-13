from flask import Flask, render_template
from feeds import get_articles
from rewriter import pick_lead_story, rewrite_headline

app = Flask(__name__)

@app.route("/")
def index():
    articles = get_articles()
    lead = pick_lead_story(articles)
    remaining = [a for a in articles if a != lead]

    lead['title'] = rewrite_headline(lead['title'], lead['source'])
    for article in remaining:
        article['title'] = rewrite_headline(article['title'], article['source'])

    return render_template("index.html", lead=lead, articles=remaining)

if __name__ == "__main__":
    app.run(debug=True)