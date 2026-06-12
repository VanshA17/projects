import requests
import pandas as pd

API_KEY = "J6QTNFXSAXIY32M2"  # paste your key here
BASE_URL = "https://www.alphavantage.co/query"

def get_financials(ticker: str):
    print(f"\n📦 Fetching data for: {ticker.upper()}\n")

    # --- Income Statement ---
    params = {"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    income_stmt = pd.DataFrame(data.get("annualReports", []))
    print("✅ Income Statement:")
    print(income_stmt[["fiscalDateEnding", "totalRevenue", "grossProfit", "netIncome", "ebitda"]].head(4))

    # --- Balance Sheet ---
    params = {"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    balance_sheet = pd.DataFrame(data.get("annualReports", []))
    print("\n✅ Balance Sheet:")
    if balance_sheet.empty:
        print("⚠️ Balance sheet empty — likely API rate limit hit. Try again tomorrow.")
    else:
        print(balance_sheet[["fiscalDateEnding", "totalAssets", "totalLiabilities", "totalShareholderEquity", "cashAndCashEquivalentsAtCarryingValue"]].head(4))
    
    # --- Cash Flow Statement ---
    params = {"function": "CASH_FLOW", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    cash_flow = pd.DataFrame(data.get("annualReports", []))
    # Calculate Free Cash Flow = Operating Cash Flow - Capital Expenditures
    print("\n✅ Cash Flow Statement:")
    if cash_flow.empty:
        print("⚠️ Cash flow empty — likely API rate limit hit. Try again tomorrow.")
    else:
        cash_flow["freeCashFlow"] = cash_flow["operatingCashflow"].astype(float) - cash_flow["capitalExpenditures"].astype(float).abs()
        print(cash_flow[["fiscalDateEnding", "operatingCashflow", "capitalExpenditures", "freeCashFlow"]].head(4))

    return income_stmt, balance_sheet, cash_flow


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. AAPL, MSFT, IBM): ")
    income, balance, cashflow = get_financials(ticker)