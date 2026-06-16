import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# Set style globally
plt.style.use("seaborn-v0_8-darkgrid")
COLORS = {"blue": "#2196F3", "green": "#4CAF50", "red": "#F44336", "orange": "#FF9800", "purple": "#9C27B0"}

def plot_fcf_history_and_projection(fcf_df: pd.DataFrame,
                                     proj_df: pd.DataFrame,
                                     ticker: str):
    """
    Plots historical FCF as bars and projected FCF as a dashed line.
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    # Historical FCF bars
    fcf_values = fcf_df["freeCashFlow"].values / 1e9
    years = fcf_df["fiscalDateEnding"].str[:4].values
    bars = ax.bar(years, fcf_values, color=COLORS["blue"], alpha=0.8, label="Historical FCF")

    # Projected FCF line
    proj_years = [str(int(years[-1]) + i) for i in range(1, len(proj_df)+1)]
    proj_values = proj_df["projectedFCF"].values / 1e9
    ax.plot(proj_years, proj_values, color=COLORS["orange"],
            linewidth=2.5, linestyle="--", marker="o", markersize=7, label="Projected FCF")

    # Connect last historical to first projected
    ax.plot([years[-1], proj_years[0]], [fcf_values[-1], proj_values[0]],
            color=COLORS["orange"], linewidth=2, linestyle="--", alpha=0.5)

    # Labels
    for i, (year, val) in enumerate(zip(proj_years, proj_values)):
        ax.annotate(f"${val:.0f}B", (year, val), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9, color=COLORS["orange"])

    ax.set_title(f"{ticker} — Historical & Projected Free Cash Flow", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Free Cash Flow ($B)", fontsize=11)
    ax.legend(fontsize=10)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{ticker}_fcf_chart.png", dpi=150)
    plt.show()
    print(f"✅ FCF chart saved as {ticker}_fcf_chart.png")


def plot_valuation_summary(ticker: str,
                            intrinsic_value: float,
                            current_price: float,
                            bear: float,
                            bull: float):
    """
    Plots a visual valuation summary — price vs intrinsic value range.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw valuation range bar
    ax.barh(["Valuation Range"], [bull - bear], left=bear,
            color=COLORS["green"], alpha=0.3, height=0.4, label="Bull-Bear Range")

    # Intrinsic value line
    ax.axvline(x=intrinsic_value, color=COLORS["blue"],
               linewidth=2.5, linestyle="-", label=f"Intrinsic Value: ${intrinsic_value:.2f}")

    # Current price line
    color = COLORS["red"] if current_price > intrinsic_value else COLORS["green"]
    ax.axvline(x=current_price, color=color,
               linewidth=2.5, linestyle="--", label=f"Current Price: ${current_price:.2f}")

    # Bear and Bull labels
    ax.text(bear, 0.35, f"Bear\n${bear:.0f}", ha="center", fontsize=9, color="gray")
    ax.text(bull, 0.35, f"Bull\n${bull:.0f}", ha="center", fontsize=9, color="gray")

    verdict = "OVERVALUED 🔴" if current_price > intrinsic_value else "UNDERVALUED 🟢"
    ax.set_title(f"{ticker} Valuation Summary — {verdict}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Price per Share ($)", fontsize=11)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{ticker}_valuation_summary.png", dpi=150)
    plt.show()
    print(f"✅ Valuation summary saved as {ticker}_valuation_summary.png")


def plot_sensitivity_heatmap(df: pd.DataFrame,
                              current_price: float,
                              ticker: str):
    """
    Polished sensitivity heatmap with current price annotation.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    sns.heatmap(
        df.astype(float),
        annot=True,
        fmt=".0f",
        cmap="RdYlGn",
        center=current_price,
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Intrinsic Value per Share ($)"}
    )

    ax.set_title(
        f"{ticker} DCF Sensitivity Analysis\n"
        f"Green = Undervalued vs Current Price (${current_price:.2f})   |   Red = Overvalued",
        fontsize=12, fontweight="bold"
    )
    ax.set_xlabel("FCF Growth Rate", fontsize=11)
    ax.set_ylabel("WACC", fontsize=11)
    plt.tight_layout()
    plt.savefig(f"{ticker}_sensitivity_heatmap.png", dpi=150)
    plt.show()
    print(f"✅ Sensitivity heatmap saved as {ticker}_sensitivity_heatmap.png")


def plot_wacc_breakdown(ticker: str,
                         cost_of_equity: float,
                         cost_of_debt: float,
                         weight_equity: float,
                         weight_debt: float,
                         wacc: float,
                         tax_rate: float = 0.21):
    """
    Visualizes WACC components as a stacked bar chart.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Capital Structure (pie chart)
    axes[0].pie(
        [weight_equity * 100, weight_debt * 100],
        labels=[f"Equity\n{weight_equity:.1%}", f"Debt\n{weight_debt:.1%}"],
        colors=[COLORS["blue"], COLORS["orange"]],
        autopct="%1.1f%%",
        startangle=90
    )
    axes[0].set_title("Capital Structure", fontsize=12, fontweight="bold")

    # Right: WACC breakdown bar
    equity_contribution = weight_equity * cost_of_equity * 100
    debt_contribution = weight_debt * cost_of_debt * (1 - tax_rate) * 100

    bars = axes[1].bar(
        ["Equity\nContribution", "Debt\nContribution", "WACC"],
        [equity_contribution, debt_contribution, wacc * 100],
        color=[COLORS["blue"], COLORS["orange"], COLORS["purple"]],
        alpha=0.85
    )

    for bar, val in zip(bars, [equity_contribution, debt_contribution, wacc * 100]):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                     f"{val:.2f}%", ha="center", fontsize=10, fontweight="bold")

    axes[1].set_title("WACC Components", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Rate (%)", fontsize=11)
    axes[1].set_ylim(0, max(equity_contribution, wacc * 100) * 1.3)

    plt.suptitle(f"{ticker} — WACC Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{ticker}_wacc_breakdown.png", dpi=150)
    plt.show()
    print(f"✅ WACC breakdown saved as {ticker}_wacc_breakdown.png")


if __name__ == "__main__":
    import sys
    sys.path.append("/Users/venshajmmera/projects/dcf_valuation")
    from fcf_calculator import calculate_historical_fcf, project_fcf
    from data_fetcher import get_financials
    from sensitivity import sensitivity_analysis

    ticker = "AAPL"
    current_price = 291.13
    wacc = 0.1025

    # Fetch data
    income, balance, cashflow = get_financials(ticker)
    fcf_df = calculate_historical_fcf(cashflow)
    proj_df = project_fcf(fcf_df, growth_rate=0.1439)

    # Plot 1 — FCF History & Projection
    plot_fcf_history_and_projection(fcf_df, proj_df, ticker)

    # Plot 2 — Valuation Summary
    plot_valuation_summary(ticker,
                           intrinsic_value=211.71,
                           current_price=current_price,
                           bear=72.09,
                           bull=236.17)

    # Plot 3 — Sensitivity Heatmap
    df = sensitivity_analysis(211.71, wacc, 0.2439, 98.77e9, 97e9, 35.9e9, 15.1e9)
    plot_sensitivity_heatmap(df, current_price, ticker)

    # Plot 4 — WACC Breakdown
    plot_wacc_breakdown(ticker,
                        cost_of_equity=0.1047,
                        cost_of_debt=0.02,
                        weight_equity=0.9744,
                        weight_debt=0.0256,
                        wacc=wacc)