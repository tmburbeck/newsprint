# The Daily Newsprint

A Flask web application that aggregates real-time news from major outlets and reimagines them with vintage 1920s broadsheet aesthetics.

## Features

- **Live RSS feeds** from Reuters, BBC, AP, NPR, and The Hill — articles update automatically
- **AI-powered lead story selection** — Claude picks the most newsworthy story of the moment
- **1920s headline rewriting** — Claude rewrites every headline in the dramatic style of a vintage newspaper
- **Broadsheet layout** — three-column grid with period-appropriate fonts and styling
- **Response caching** — API calls are cached so the app stays fast after the first load

## Tech Stack

- Python / Flask
- Jinja2 templating
- feedparser (RSS parsing)
- Anthropic API (claude-sonnet-4-6)
- HTML / CSS (Google Fonts — Playfair Display, UnifrakturMaguntia, Oswald, Libre Baskerville)

## Setup

1. Clone the repository
git clone https://github.com/tmburbeck/newsprint.git
cd newsprint

2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install flask feedparser anthropic python-dotenv

3. Create a `.env` file in the project root
ANTHROPIC_API_KEY=your-api-key-here

4. Run the app
python app.py

5. Visit `http://127.0.0.1:5000` in your browser

## Project Structure

```
newsprint/
├── app.py              # Flask routes
├── feeds.py            # RSS fetching logic
├── rewriter.py         # Anthropic API calls and caching
├── templates/
│   └── index.html      # Jinja2 front page template
├── static/
│   └── style.css       # Vintage broadsheet styling
├── .env                # API key (not committed)
└── requirements.txt    # Dependencies
```

## Notes

- The first page load will be slow as Claude rewrites all headlines and selects the lead story
- Subsequent loads are fast thanks to local JSON caching
- Never commit your `.env` file — it's excluded via `.gitignore`