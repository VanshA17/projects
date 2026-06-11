import pandas as pd
import numpy as np
from data_fetcher import get_financials

def calculate_historical_fcf(cash_flow: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts and calculates historical Free Cash Flow from cash flow statement.
    FCF = Operating Cash Flow - Capital Expenditures
    """
    df = cash_flow[["fiscalDateEnding", "operatingCashflow", "capitalExpenditures"]].copy()

    # Convert to numeric
    df["operatingCashflow"] = pd.to_numeric(df["operatingCashflow"], errors="coerce")
    df["capitalExpenditures"] = pd.to_numeric(df["capitalExpenditures"], errors="coerce")

    # FCF = OCF - CapEx (CapEx is negative in some APIs so we use abs)
    df["freeCashFlow"] = df["operatingCashflow"] - df["capitalExpenditures"].abs()

    # Sort oldest to newest
    df = df.sort_values("fiscalDateEnding").reset_index(drop=True)

    print("\n✅ Historical Free Cash Flow:")
    print(df)

    return df


def calculate_fcf_growth_rate(fcf_df: pd.DataFrame) -> float:
    """
    Calculates the historical CAGR of Free Cash Flow.
    CAGR = (Ending FCF / Beginning FCF) ^ (1/n) - 1
    """
    fcf_values = fcf_df["freeCashFlow"].dropna().values

    if len(fcf_values) < 2:
        print("⚠️ Not enough data to calculate growth rate. Using default 5%.")
        return 0.05

    beginning = fcf_values[0]
    ending = fcf_values[-1]
    n = len(fcf_values) - 1

    if beginning <= 0 or ending <= 0:
        print("⚠️ Negative FCF detected. Using default growth rate of 5%.")
        return 0.05

    cagr = (ending / beginning) ** (1 / n) - 1
    print(f"\n✅ Historical FCF CAGR: {cagr:.2%}")

    return cagr


def project_fcf(fcf_df: pd.DataFrame, growth_rate: float = None, years: int = 5) -> pd.DataFrame:
    """
    Projects future Free Cash Flows based on historical growth rate.
    """
    if growth_rate is None:
        growth_rate = calculate_fcf_growth_rate(fcf_df)

    # Cap growth rate between 2% and 25% to stay realistic
    growth_rate = max(0.02, min(growth_rate, 0.25))
    print(f"\n📈 Using growth rate: {growth_rate:.2%} (capped between 2%-25%)")

    last_fcf = fcf_df["freeCashFlow"].iloc[-1]

    projections = []
    for year in range(1, years + 1):
        projected_fcf = last_fcf * (1 + growth_rate) ** year
        projections.append({
            "year": f"Year {year}",
            "projectedFCF": round(projected_fcf, 2)
        })

    proj_df = pd.DataFrame(projections)
    print(f"\n✅ Projected FCF for next {years} years:")
    print(proj_df)

    return proj_df


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. AAPL, MSFT): ")
    income, balance, cashflow = get_financials(ticker)

    fcf_df = calculate_historical_fcf(cashflow)
    growth_rate = calculate_fcf_growth_rate(fcf_df)
    proj_df = project_fcf(fcf_df, growth_rate)