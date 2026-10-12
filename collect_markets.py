"""Fetch latest close + daily change for indices, stocks, commodities via yfinance."""
import yfinance as yf

from config import MARKET_TICKERS


def collect() -> dict:
    """Returns {group: [{name, symbol, price, change, pct}]}. Missing data is skipped."""
    symbols = [sym for lst in MARKET_TICKERS.values() for _, sym in lst]
    try:
        data = yf.download(symbols, period="7d", interval="1d", progress=False,
                           auto_adjust=False, group_by="ticker", threads=False)
    except Exception as e:
        print(f"  [skip] market data: {e}")
        return {}

    out = {}
    for group, lst in MARKET_TICKERS.items():
        rows = []
        for name, sym in lst:
            try:
                closes = data[sym]["Close"].dropna()
                if len(closes) < 2:
                    continue
                last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
                rows.append({
                    "name": name,
                    "symbol": sym,
                    "price": last,
                    "change": last - prev,
                    "pct": (last - prev) / prev * 100,
                })
            except Exception:
                continue
        if rows:
            out[group] = rows
    print(f"  market quotes: {sum(len(r) for r in out.values())}")
    return out
