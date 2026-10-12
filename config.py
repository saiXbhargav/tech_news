"""All tweakable settings live here: news sources, stock tickers, limits."""

# ---------- News sources (RSS) ----------
# category -> list of (source name, feed url)
TECH_FEEDS = {
    "Tech": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("Wired", "https://www.wired.com/feed/rss"),
        # HN blocks bots on its RSS, so this uses the Algolia HN API (handled in collect_news.py)
        ("Hacker News", "https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30"),
    ],
    "AI": [
        ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
        ("The Decoder", "https://the-decoder.com/feed/"),
    ],
    "Security": [
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ],
}

MARKET_FEEDS = {
    "Markets": [
        ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
        ("Livemint", "https://www.livemint.com/rss/markets"),
        ("CNBC", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    ],
}

# Only keep articles published in the last N hours
LOOKBACK_HOURS = 30
# Max articles taken from each feed (keeps the AI prompt small)
MAX_PER_FEED = 12

# ---------- Stock market (Yahoo Finance symbols via yfinance) ----------
# group name -> list of (display name, yahoo symbol)
MARKET_TICKERS = {
    "India": [
        ("Nifty 50", "^NSEI"),
        ("Sensex", "^BSESN"),
        ("Bank Nifty", "^NSEBANK"),
    ],
    "US": [
        ("S&P 500", "^GSPC"),
        ("Nasdaq", "^IXIC"),
        ("Dow Jones", "^DJI"),
    ],
    "Tech Stocks": [
        ("Apple", "AAPL"),
        ("Microsoft", "MSFT"),
        ("Nvidia", "NVDA"),
        ("Alphabet", "GOOGL"),
        ("Amazon", "AMZN"),
        ("Meta", "META"),
        ("Tesla", "TSLA"),
        ("TCS", "TCS.NS"),
        ("Infosys", "INFY.NS"),
        ("HCL Tech", "HCLTECH.NS"),
        ("Wipro", "WIPRO.NS"),
    ],
    "Commodities & FX": [
        ("USD/INR", "INR=X"),
        ("Gold", "GC=F"),
        ("Crude Oil", "CL=F"),
        ("Bitcoin", "BTC-USD"),
    ],
}

# ---------- AI ----------
# "gemini-flash-latest" always points at Google's current Flash model (free tier).
# Tried in order; later ones are fallbacks if Google is overloaded or retires a model.
GEMINI_MODELS = ["gemini-flash-latest", "gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-lite-latest"]
TOP_STORIES = 5
