import requests
import pandas as pd
from cache import get_cached, set_cached
from data_fetcher import fetch_with_cache

API_KEY = "J6QTNFXSAXIY32M2"  # same key as data_fetcher.py
BASE_URL = "https://www.alphavantage.co/query"

def get_beta(ticker: str) -> float:
    """Fetches beta of the stock from Alpha Vantage."""
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY}
    data = fetch_with_cache(params, f"{ticker}_{params['function']}")
    beta = float(data.get("Beta", 1.0))  # default to 1.0 if not found
    print(f"✅ Beta: {beta}")
    return beta


def calculate_cost_of_equity(beta: float,risk_free_rate: float = 0.045,market_premium: float = 0.055) -> float:
    """
    CAPM: Cost of Equity = Risk Free Rate + Beta × Market Risk Premium
    - Risk free rate: ~4.5% (current US 10yr treasury yield)
    - Market risk premium: ~5.5% (historical US equity premium)
    """
    cost_of_equity = risk_free_rate + beta * market_premium
    print(f"\n✅ Cost of Equity (CAPM):")
    print(f"   Risk Free Rate:      {risk_free_rate:.2%}")
    print(f"   Beta:                {beta:.2f}")
    print(f"   Market Premium:      {market_premium:.2%}")
    print(f"   Cost of Equity:      {cost_of_equity:.2%}")
    return cost_of_equity


def calculate_cost_of_debt(ticker: str) -> float:
    """
    Cost of Debt = Interest Expense / Total Debt
    Fetched from income statement and balance sheet.
    """
    # Income statement for interest expense
    params = {"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    income_data = r.json().get("annualReports", [{}])[0]
    interest_expense = abs(float(income_data.get("interestExpense", 0) or 0))

    # Balance sheet for total debt
    params = {"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    balance_data = r.json().get("annualReports", [{}])[0]
    total_debt = float(balance_data.get("shortLongTermDebtTotal", 1) or 1)

    cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.04
    cost_of_debt = max(0.02, min(cost_of_debt, 0.15))  # cap between 2%-15%

    print(f"\n✅ Cost of Debt:")
    print(f"   Interest Expense:    ${interest_expense/1e9:.2f}B")
    print(f"   Total Debt:          ${total_debt/1e9:.2f}B")
    print(f"   Cost of Debt:        {cost_of_debt:.2%}")
    return cost_of_debt


def calculate_wacc(ticker: str, tax_rate: float = 0.21) -> float:
    """
    WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1 - Tax Rate))
    E = Market Cap (Equity)
    D = Total Debt
    V = E + D
    """
    # Get market cap from overview
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY}
    data = fetch_with_cache(params, f"{ticker}_{params['function']}")

    market_cap = float(data.get("MarketCapitalization", 0) or 0)
    beta = float(data.get("Beta", 1.0) or 1.0)

    # Get cost of equity and debt
    cost_of_equity = calculate_cost_of_equity(beta)
    cost_of_debt = calculate_cost_of_debt(ticker)

    # Capital structure weights
    params = {"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    balance_data = r.json().get("annualReports", [{}])[0]
    total_debt = float(balance_data.get("shortLongTermDebtTotal", 0) or 0)

    # Fallback if market cap unavailable
    if market_cap == 0:
        print("⚠️ Market cap unavailable from API. Using fallback.")
        try:
            market_cap = float(input("   Enter market cap in billions (e.g. 3200): ")) * 1e9
        except:
            market_cap = 3200e9  # AAPL approximate

    total_value = market_cap + total_debt
    weight_equity = market_cap / total_value if total_value > 0 else 0.95
    weight_debt = total_debt / total_value if total_value > 0 else 0.05

    # WACC formula
    wacc = (weight_equity * cost_of_equity) + \
           (weight_debt * cost_of_debt * (1 - tax_rate))

    print(f"\n✅ WACC Calculation:")
    print(f"   Market Cap:          ${market_cap/1e9:.2f}B")
    print(f"   Total Debt:          ${total_debt/1e9:.2f}B")
    print(f"   Weight Equity:       {weight_equity:.2%}")
    print(f"   Weight Debt:         {weight_debt:.2%}")
    print(f"   Tax Rate:            {tax_rate:.2%}")
    print(f"   WACC:                {wacc:.2%}")

    return wacc


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. AAPL, MSFT): ")
    wacc = calculate_wacc(ticker)