"""Runs the whole pipeline: collect -> summarize -> render -> send.

Local test without sending:   python main.py --dry-run   (writes preview.html)
"""
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import collect_markets
import collect_news
from config import MARKET_FEEDS, TECH_FEEDS
from send_email import send
from summarize import summarize

ROOT = Path(__file__).parent
IST = timezone(timedelta(hours=5, minutes=30))


def load_dotenv() -> None:
    """Tiny .env loader for local runs (GitHub Actions uses repo secrets instead)."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    load_dotenv()

    print("Collecting tech news...")
    tech = collect_news.collect(TECH_FEEDS)
    print("Collecting market news...")
    market_news = collect_news.collect(MARKET_FEEDS)
    print("Collecting market data...")
    markets = collect_markets.collect()

    print("Summarizing...")
    ai = summarize(tech, market_news, markets)

    plain = defaultdict(list)
    for item in tech + market_news:
        if len(plain[item["category"]]) < 10:
            plain[item["category"]].append(item)

    now = datetime.now(IST)
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    html = env.get_template("email.html").render(
        date=now.strftime("%A, %d %B %Y"), ai=ai, markets=markets, plain=plain,
    )
    subject = f"☕ Tech & Markets Brief — {now.strftime('%d %b %Y')}"

    if dry_run:
        out = ROOT / "preview.html"
        out.write_text(html, encoding="utf-8")
        print(f"Dry run: wrote {out}")
    else:
        print("Sending email...")
        send(subject, html)


if __name__ == "__main__":
    main()
