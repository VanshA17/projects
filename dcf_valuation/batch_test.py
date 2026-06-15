from cache import get_cached
import requests
import pandas as pd
from data_fetcher import fetch_with_cache

API_KEY = "J6QTNFXSAXIY32M2"
BASE_URL = "https://www.alphavantage.co/query"

# Known values for major stocks (hardcoded to avoid API limits)
STOCK_DATA = {
    "AAPL":  {"last_fcf": 98.77e9,  "wacc": 0.1025, "debt": 97e9,   "cash": 35.9e9, "shares": 15.1e9,  "price": 291.13},
    "MSFT":  {"last_fcf": 70.0e9,   "wacc": 0.0900, "debt": 45e9,   "cash": 80e9,   "shares": 7.4e9,   "price": 415.00},
    "GOOGL": {"last_fcf": 60.0e9,   "wacc": 0.0950, "debt": 14e9,   "cash": 110e9,  "shares": 12.3e9,  "price": 178.00},
    "AMZN":  {"last_fcf": 50.0e9,   "wacc": 0.1000, "debt": 67e9,   "cash": 86e9,   "shares": 10.5e9,  "price": 195.00},
    "TSLA":  {"last_fcf": 2.0e9,    "wacc": 0.1100, "debt": 5e9,    "cash": 29e9,   "shares": 3.2e9,   "price": 248.00},
}

def batch_valuation(growth_rate: float = 0.10, years: int = 5):
    """
    Runs DCF valuation on multiple stocks using hardcoded data.
    Avoids API rate limits entirely.
    """
    print(f"\n{'='*75}")
    print(f"  BATCH DCF VALUATION — {len(STOCK_DATA)} Stocks")
    print(f"{'='*75}")
    print(f"  {'Ticker':<8} {'Intrinsic Value':<18} {'Market Price':<15} {'Upside':<12} {'Verdict'}")
    print(f"  {'-'*70}")

    results = []
    for ticker, data in STOCK_DATA.items():
        last_fcf = data["last_fcf"]
        wacc = data["wacc"]
        debt = data["debt"]
        cash = data["cash"]
        shares = data["shares"]
        price = data["price"]

        # Project FCFs
        proj_fcfs = [last_fcf * (1 + growth_rate) ** y for y in range(1, years+1)]

        # Discount FCFs
        pv_fcfs = sum([fcf / (1 + wacc) ** (i+1) for i, fcf in enumerate(proj_fcfs)])

        # Terminal value
        terminal_value = proj_fcfs[-1] * 1.025 / (wacc - 0.025)
        pv_terminal = terminal_value / (1 + wacc) ** years

        # Intrinsic value
        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value - debt + cash
        iv = equity_value / shares
        upside = (iv - price) / price * 100
        verdict = "🟢 BUY" if upside > 10 else "🔴 SELL" if upside < -10 else "🟡 HOLD"

        print(f"  {ticker:<8} ${iv:<17.2f} ${price:<14.2f} {upside:+.1f}%{'':5} {verdict}")
        results.append({"ticker": ticker, "intrinsic_value": iv, "market_price": price, "upside": upside, "verdict": verdict})

    print(f"{'='*75}")
    return pd.DataFrame(results)


if __name__ == "__main__":
    df = batch_valuation(growth_rate=0.10)
    print(f"\n✅ Summary saved!")
    df.to_csv("batch_valuation_results.csv", index=False)