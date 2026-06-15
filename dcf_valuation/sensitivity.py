import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dcf_engine import calculate_intrinsic_value
from fcf_calculator import calculate_historical_fcf, calculate_fcf_growth_rate, project_fcf
from wacc_calculator import calculate_wacc

def sensitivity_analysis(base_intrinsic_value: float,
                          base_wacc: float,
                          base_growth_rate: float,
                          last_fcf: float,
                          total_debt: float,
                          cash: float,
                          shares: float,
                          terminal_growth: float = 0.025) -> pd.DataFrame:
    """
    Generates a heatmap of intrinsic values across
    different WACC and FCF growth rate assumptions.
    """
    # WACC range: base ± 2% in 0.5% steps
    wacc_range = np.arange(base_wacc - 0.02, base_wacc + 0.025, 0.005)

    # Growth rate range: base ± 5% in 1% steps
    growth_range = np.arange(
        max(0.02, base_growth_rate - 0.05),
        min(0.25, base_growth_rate + 0.06),
        0.01
    )

    results = {}

    for wacc in wacc_range:
        row = {}
        for growth in growth_range:
            # Project FCFs with this growth rate
            proj_fcfs = [last_fcf * (1 + growth) ** y for y in range(1, 6)]

            # Discount FCFs
            pv_fcfs = sum([fcf / (1 + wacc) ** (i+1) for i, fcf in enumerate(proj_fcfs)])

            # Terminal value
            terminal_value = proj_fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
            pv_terminal = terminal_value / (1 + wacc) ** 5

            # Intrinsic value per share
            enterprise_value = pv_fcfs + pv_terminal
            equity_value = enterprise_value - total_debt + cash
            iv_per_share = equity_value / shares

            row[f"{growth:.0%}"] = round(iv_per_share, 2)

        results[f"{wacc:.1%}"] = row

    df = pd.DataFrame(results).T
    return df


def plot_sensitivity_heatmap(df: pd.DataFrame,
                              current_price: float,
                              ticker: str):
    """Plots the sensitivity heatmap."""
    plt.figure(figsize=(14, 7))

    # Color: green = undervalued vs current price, red = overvalued
    sns.heatmap(
        df.astype(float),
        annot=True,
        fmt=".0f",
        cmap="RdYlGn",
        center=current_price,
        linewidths=0.5,
        cbar_kws={"label": "Intrinsic Value per Share ($)"}
    )

    plt.title(f"{ticker} — DCF Sensitivity Analysis\n(Green = Undervalued vs ${current_price:.2f}, Red = Overvalued)", fontsize=13)
    plt.xlabel("FCF Growth Rate", fontsize=11)
    plt.ylabel("WACC", fontsize=11)
    plt.tight_layout()
    plt.savefig(f"{ticker}_sensitivity_heatmap.png", dpi=150)
    plt.show()
    print(f"\n✅ Heatmap saved as {ticker}_sensitivity_heatmap.png")


def bull_base_bear(last_fcf: float,
                   wacc: float,
                   total_debt: float,
                   cash: float,
                   shares: float,
                   current_price: float,
                   ticker: str):
    """
    Generates bull, base, and bear case valuations.
    - Bear: lower growth, higher WACC
    - Base: historical growth, current WACC
    - Bull: higher growth, lower WACC
    """
    scenarios = {
        "🐻 Bear": {"growth": 0.05, "wacc": wacc + 0.02},
        "📊 Base": {"growth": 0.10, "wacc": wacc},
        "🐂 Bull": {"growth": 0.20, "wacc": wacc - 0.02},
    }

    print(f"\n{'='*50}")
    print(f"  SCENARIO ANALYSIS: {ticker.upper()}")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"{'='*50}")
    print(f"  {'Scenario':<12} {'Growth':<10} {'WACC':<10} {'Intrinsic Value':<18} {'Upside'}")
    print(f"  {'-'*60}")

    for name, params in scenarios.items():
        growth = params["growth"]
        wacc_s = params["wacc"]

        proj_fcfs = [last_fcf * (1 + growth) ** y for y in range(1, 6)]
        pv_fcfs = sum([fcf / (1 + wacc_s) ** (i+1) for i, fcf in enumerate(proj_fcfs)])
        terminal_value = proj_fcfs[-1] * 1.025 / (wacc_s - 0.025)
        pv_terminal = terminal_value / (1 + wacc_s) ** 5
        enterprise_value = pv_fcfs + pv_terminal
        equity_value = enterprise_value - total_debt + cash
        iv = equity_value / shares
        upside = (iv - current_price) / current_price * 100

        print(f"  {name:<12} {growth:<10.0%} {wacc_s:<10.2%} ${iv:<18.2f} {upside:+.1f}%")

    print(f"{'='*50}")


if __name__ == "__main__":
    # AAPL values from our DCF engine
    ticker = "AAPL"
    last_fcf = 98767000000      # latest FCF
    wacc = 0.1025               # from wacc_calculator
    total_debt = 97000000000    # $97B
    cash = 35934000000          # $35.9B
    shares = 15100000000        # ~15.1B shares
    current_price = 291.13

    # Bull/Base/Bear
    bull_base_bear(last_fcf, wacc, total_debt, cash, shares, current_price, ticker)

    # Sensitivity heatmap
    base_iv = 211.71
    df = sensitivity_analysis(base_iv, wacc, 0.2439, last_fcf, total_debt, cash, shares)
    print("\n✅ Sensitivity Table:")
    print(df)
    plot_sensitivity_heatmap(df, current_price, ticker)