import requests
import pandas as pd
from cache import get_cached, set_cached

API_KEY = "J6QTNFXSAXIY32M2"
BASE_URL = "https://www.alphavantage.co/query"

def fetch_with_cache(params: dict, cache_key: str) -> dict:
    """Fetches from API or returns cached result if available."""
    cached = get_cached(cache_key)
    if cached:
        print(f"   (using cached data for {cache_key})")
        return cached

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    # Only cache if valid data returned
    if "annualReports" in data or "Global Quote" in data or "Beta" in data or "MarketCapitalization" in data:
        set_cached(cache_key, data)

    return data

def get_financials(ticker: str):
    print(f"\n📦 Fetching data for: {ticker.upper()}\n")

    # --- Income Statement ---
    params = {"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": API_KEY}
    data = fetch_with_cache(params, f"{ticker}_income")
    income_stmt = pd.DataFrame(data.get("annualReports", []))
    print("✅ Income Statement:")
    if income_stmt.empty:
        print("⚠️ Empty — rate limit hit")
    else:
        print(income_stmt[["fiscalDateEnding", "totalRevenue", "grossProfit", "netIncome", "ebitda"]].head(4))

    # --- Balance Sheet ---
    params = {"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY}
    data = fetch_with_cache(params, f"{ticker}_balance")
    balance_sheet = pd.DataFrame(data.get("annualReports", []))
    print("\n✅ Balance Sheet:")
    if balance_sheet.empty:
        print("⚠️ Empty — rate limit hit")
    else:
        print(balance_sheet[["fiscalDateEnding", "totalAssets", "totalLiabilities", "totalShareholderEquity", "cashAndCashEquivalentsAtCarryingValue"]].head(4))

    # --- Cash Flow Statement ---
    params = {"function": "CASH_FLOW", "symbol": ticker, "apikey": API_KEY}
    data = fetch_with_cache(params, f"{ticker}_cashflow")
    cash_flow = pd.DataFrame(data.get("annualReports", []))
    print("\n✅ Cash Flow Statement:")
    if cash_flow.empty:
        print("⚠️ Empty — rate limit hit")
    else:
        cash_flow["freeCashFlow"] = cash_flow["operatingCashflow"].astype(float) - cash_flow["capitalExpenditures"].astype(float).abs()
        print(cash_flow[["fiscalDateEnding", "operatingCashflow", "capitalExpenditures", "freeCashFlow"]].head(4))

    return income_stmt, balance_sheet, cash_flow