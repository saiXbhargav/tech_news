"""Stage 1 + 2: fetch RSS feeds, keep recent items, remove duplicates."""
import html
import re
import time
from calendar import timegm
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

import feedparser
import requests

from config import LOOKBACK_HOURS, MAX_PER_FEED

HEADERS = {"User-Agent": "Mozilla/5.0 (tech-digest bot; +https://github.com)"}


def _clean(text: str, limit: int = 300) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def _fetch_hn(category: str, url: str) -> list[dict]:
    hits = requests.get(url, headers=HEADERS, timeout=20).json()["hits"]
    hits = [h for h in hits if h.get("points", 0) >= 100]
    hits.sort(key=lambda h: h.get("points", 0), reverse=True)
    return [{
        "category": category,
        "source": "Hacker News",
        "title": _clean(h.get("title", ""), 200),
        "link": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
        "summary": f"{h.get('points', 0)} points, {h.get('num_comments', 0)} comments on Hacker News",
        "ts": h.get("created_at_i", time.time()),
    } for h in hits[:MAX_PER_FEED]]


def _fetch_feed(category: str, source: str, url: str) -> list[dict]:
    if "hn.algolia.com" in url:
        try:
            items = _fetch_hn(category, url)
            print(f"  {source}: {len(items)} items")
            return items
        except Exception as e:
            print(f"  [skip] {source}: {e}")
            return []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"  [skip] {source}: {e}")
        return []

    cutoff = time.time() - LOOKBACK_HOURS * 3600
    items = []
    for entry in feed.entries:
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        ts = timegm(published) if published else time.time()
        if ts < cutoff:
            continue
        items.append({
            "category": category,
            "source": source,
            "title": _clean(entry.get("title", ""), 200),
            "link": entry.get("link", ""),
            "summary": _clean(entry.get("summary", "")),
            "ts": ts,
        })
        if len(items) >= MAX_PER_FEED:
            break
    print(f"  {source}: {len(items)} items")
    return items


def _dedupe(items: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for item in items:
        t = item["title"].lower()
        if not t:
            continue
        if any(SequenceMatcher(None, t, k["title"].lower()).ratio() > 0.8 for k in kept):
            continue
        kept.append(item)
    return kept


def collect(feeds: dict) -> list[dict]:
    jobs = [(cat, src, url) for cat, lst in feeds.items() for src, url in lst]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(lambda j: _fetch_feed(*j), jobs)
    items = [i for r in results for i in r]
    items.sort(key=lambda i: i["ts"], reverse=True)
    return _dedupe(items)
