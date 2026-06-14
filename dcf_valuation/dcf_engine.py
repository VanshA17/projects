import pandas as pd
import numpy as np
from data_fetcher import get_financials
from fcf_calculator import calculate_historical_fcf, calculate_fcf_growth_rate, project_fcf
from wacc_calculator import calculate_wacc
import requests

API_KEY = "J6QTNFXSAXIY32M2"  # same key
BASE_URL = "https://www.alphavantage.co/query"

def get_shares_outstanding(ticker: str) -> float:
    """Fetches shares outstanding to calculate per share intrinsic value."""
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    data = r.json()
    shares = float(data.get("SharesOutstanding", 0) or 0)
    print(f"✅ Shares Outstanding: {shares/1e9:.2f}B")
    return shares


def calculate_terminal_value(final_fcf: float, wacc: float, terminal_growth_rate: float = 0.025) -> float:
    """
    Terminal Value = Final Year FCF × (1 + g) / (WACC - g)
    g = terminal growth rate (long term GDP growth ~2.5%)
    This captures value beyond the 5 year projection period.
    """
    terminal_value = final_fcf * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
    print(f"\n✅ Terminal Value: ${terminal_value/1e9:.2f}B")
    return terminal_value


def discount_cash_flows(projected_fcf: pd.DataFrame, terminal_value: float, wacc: float) -> float:
    """
    Discounts all future FCFs and terminal value back to present value.
    PV = FCF / (1 + WACC)^year
    """
    pv_fcfs = []
    for i, row in projected_fcf.iterrows():
        year = i + 1
        pv = row["projectedFCF"] / (1 + wacc) ** year
        pv_fcfs.append(pv)

    # Discount terminal value
    n_years = len(projected_fcf)
    pv_terminal = terminal_value / (1 + wacc) ** n_years

    total_pv = sum(pv_fcfs) + pv_terminal

    print(f"\n✅ Present Value Breakdown:")
    print(f"   PV of FCFs:          ${sum(pv_fcfs)/1e9:.2f}B")
    print(f"   PV of Terminal Value: ${pv_terminal/1e9:.2f}B")
    print(f"   Total Enterprise Value: ${total_pv/1e9:.2f}B")

    return total_pv


def calculate_intrinsic_value(ticker: str) -> dict:
    """
    Full DCF pipeline:
    1. Fetch financials
    2. Calculate historical FCF + growth rate
    3. Project future FCFs
    4. Calculate WACC
    5. Calculate terminal value
    6. Discount everything → Enterprise Value
    7. Subtract debt, add cash → Equity Value
    8. Divide by shares → Intrinsic Value per Share
    """
    print(f"\n{'='*50}")
    print(f"  DCF VALUATION: {ticker.upper()}")
    print(f"{'='*50}")

    # Step 1 — Fetch financials
    income, balance, cashflow = get_financials(ticker)

    # Step 2 — Historical FCF
    fcf_df = calculate_historical_fcf(cashflow)
    growth_rate = calculate_fcf_growth_rate(fcf_df)

    # Step 3 — Project FCFs
    proj_df = project_fcf(fcf_df, growth_rate, years=5)

    # Step 4 — WACC
    wacc = calculate_wacc(ticker)

    # Step 5 — Terminal Value
    final_fcf = proj_df["projectedFCF"].iloc[-1]
    terminal_value = calculate_terminal_value(final_fcf, wacc)

    # Step 6 — Discount cash flows → Enterprise Value
    enterprise_value = discount_cash_flows(proj_df, terminal_value, wacc)

    # Step 7 — Equity Value = Enterprise Value - Debt + Cash
    if not balance.empty:
        total_debt = float(balance["shortLongTermDebtTotal"].iloc[0] if "shortLongTermDebtTotal" in balance.columns else 0)
        cash = float(balance["cashAndCashEquivalentsAtCarryingValue"].iloc[0] if "cashAndCashEquivalentsAtCarryingValue" in balance.columns else 0)
    else:
        # Fallback: use known values or prompt user
        print(f"\n⚠️ Balance sheet unavailable. Using fallback values.")
        print(f"   For AAPL: Total Debt ~$97B, Cash ~$36B (as of 2025)")
        try:
            total_debt = float(input("   Enter total debt in billions (e.g. 97): ")) * 1e9
            cash = float(input("   Enter cash in billions (e.g. 36): ")) * 1e9
        except:
            total_debt = 97e9
            cash = 36e9

    equity_value = enterprise_value - total_debt + cash

    # Step 8 — Intrinsic Value per Share (fetch from OVERVIEW)
    # Step 8 — Intrinsic Value per Share
    # Derive shares from market cap / current price (most reliable with free API)
    shares = 0

    # Try OVERVIEW endpoint
    params = {"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    overview = r.json()
    shares = float(overview.get("SharesOutstanding") or 0)

    # Fallback — derive from market cap and current price
    if shares == 0 and current_price > 0:
        market_cap_overview = float(overview.get("MarketCapitalization") or 0)
        if market_cap_overview > 0:
            shares = market_cap_overview / current_price
            print(f"✅ Shares Outstanding (derived): {shares/1e9:.2f}B")

    # Final fallback — ask user
    if shares == 0:
        print("⚠️ Could not derive shares outstanding automatically.")
        try:
            shares = float(input("   Enter shares outstanding in billions (e.g. 15.1): ")) * 1e9
        except:
            shares = 15.1e9  # AAPL approximate

    intrinsic_value_per_share = equity_value / shares if shares > 0 else 0
    # Current market price
    params = {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": API_KEY}
    r = requests.get(BASE_URL, params=params)
    quote_data = r.json().get("Global Quote", {})
    current_price = float(quote_data.get("05. price", 0) or 0)

    # Fallback — ask user to input current price manually
    if current_price == 0:
        print(f"\n⚠️ Could not fetch live price automatically.")
        print(f"   Please check Google Finance or Yahoo Finance for {ticker} current price.")
        try:
            current_price = float(input(f"   Enter current market price for {ticker}: $"))
        except:
            current_price = 0

    upside = ((intrinsic_value_per_share - current_price) / current_price * 100) if current_price > 0 else 0

    print(f"\n{'='*50}")
    print(f"  VALUATION SUMMARY: {ticker.upper()}")
    print(f"{'='*50}")
    print(f"  Intrinsic Value:   ${intrinsic_value_per_share:.2f}")
    print(f"  Current Price:     ${current_price:.2f}")
    print(f"  Upside/Downside:   {upside:+.1f}%")
    print(f"  Verdict:           {'🟢 UNDERVALUED' if upside > 0 else '🔴 OVERVALUED'}")
    print(f"{'='*50}")

    return {
        "ticker": ticker,
        "intrinsic_value": intrinsic_value_per_share,
        "current_price": current_price,
        "upside": upside
    }


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. AAPL, MSFT): ")
    result = calculate_intrinsic_value(ticker)