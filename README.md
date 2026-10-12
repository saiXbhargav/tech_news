# Morning Tech & Markets Brief

A free daily email (~7:00 AM IST) with AI-summarized tech news plus Indian/US stock market moves.
Runs on GitHub Actions, so no laptop or server needs to stay on.

**Pipeline:** RSS feeds + Hacker News → dedupe → Yahoo Finance quotes → Gemini summary → HTML email via Gmail.

## Setup
1. Repo → Settings → Secrets and variables → Actions → add:
   `GEMINI_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, optional `EMAIL_TO` (comma-separated).
2. Actions tab → "Daily Tech & Markets Brief" → Run workflow (test).

## Local test
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # fill in values
.venv\Scripts\python main.py --dry-run   # writes preview.html, no email
.venv\Scripts\python main.py             # actually sends
```

## Customize
Edit `config.py`: feeds, stock tickers, lookback window, number of top stories.
Change send time in `.github/workflows/daily.yml` (cron is in UTC; IST = UTC + 5:30).
