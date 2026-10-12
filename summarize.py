"""Stage 3: ask Gemini (free tier) to pick top stories, group them and write short summaries.

If there is no API key or the call fails, returns None and the email falls back to plain headlines.
"""
import json
import os
import time

import requests

from config import GEMINI_MODELS, TOP_STORIES

PROMPT = """You are the editor of a daily morning briefing on technology and stock markets for a
reader in India. Below are today's articles (JSON, each with an "id").

Return ONLY JSON with this exact shape:
{{
  "headline": "one punchy sentence capturing the biggest story of the day",
  "top": [{{"id": <int>, "summary": "2 sentences", "why": "1 sentence: why it matters"}}],
  "sections": [{{"name": "<section name>", "items": [{{"id": <int>, "summary": "1 sentence"}}]}}],
  "market_take": "3-4 sentences explaining what moved Indian and US markets and why, using the market data and market news"
}}

Rules:
- "top": the {top} most important tech stories.
- "sections": group the remaining worthwhile tech stories into sections such as
  "AI & ML", "Big Tech", "Startups & Funding", "Security", "Dev & Open Source", "Gadgets & Science".
  Skip duplicates, ads, deals/discount posts and trivial items. Max 6 items per section.
- Only use ids that exist below. Do not invent facts beyond the given text.

MARKET DATA (last close, % change):
{markets}

ARTICLES:
{articles}
"""


def _market_lines(markets: dict) -> str:
    return "\n".join(
        f"{r['name']}: {r['price']:.2f} ({r['pct']:+.2f}%)"
        for rows in markets.values() for r in rows
    ) or "unavailable"


def summarize(tech: list[dict], market_news: list[dict], markets: dict) -> dict | None:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("  no GEMINI_API_KEY -> skipping AI summary")
        return None

    all_items = tech + market_news
    articles = json.dumps(
        [{"id": i, "cat": it["category"], "title": it["title"], "text": it["summary"]}
         for i, it in enumerate(all_items)],
        ensure_ascii=False,
    )
    prompt = PROMPT.format(top=TOP_STORIES, markets=_market_lines(markets), articles=articles)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3},
    }

    models = [os.getenv("GEMINI_MODEL")] if os.getenv("GEMINI_MODEL") else GEMINI_MODELS
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            for attempt in range(3):  # retry briefly when Google is overloaded
                resp = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=120)
                if resp.status_code not in (429, 503):
                    break
                time.sleep(10 * (attempt + 1))
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(text)
            print(f"  AI summary ok ({model})")
            return _attach(result, all_items)
        except Exception as e:
            print(f"  [warn] {model} failed: {e}")
    return None


def _attach(result: dict, items: list[dict]) -> dict:
    """Swap ids for the real article (title/link/source) so links never get hallucinated."""
    def resolve(entries):
        out = []
        for e in entries or []:
            idx = e.get("id")
            if isinstance(idx, int) and 0 <= idx < len(items):
                out.append({**items[idx], "ai_summary": e.get("summary", ""), "why": e.get("why", "")})
        return out

    return {
        "headline": result.get("headline", ""),
        "top": resolve(result.get("top")),
        "sections": [
            {"name": s.get("name", "More"), "items": resolve(s.get("items"))}
            for s in result.get("sections", []) if s.get("items")
        ],
        "market_take": result.get("market_take", ""),
    }
