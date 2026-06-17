import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append("/Users/venshajmmera/projects/dcf_valuation")

from data_fetcher import get_financials
from fcf_calculator import calculate_historical_fcf, calculate_fcf_growth_rate, project_fcf
from wacc_calculator import calculate_wacc
from sensitivity import sensitivity_analysis, bull_base_bear
from visualizer import (plot_fcf_history_and_projection,
                         plot_valuation_summary,
                         plot_sensitivity_heatmap,
                         plot_wacc_breakdown)

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="DCF Valuation Tool",
    page_icon="📈",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────
st.title("📈 DCF Stock Valuation Tool")
st.markdown("*Automated Discounted Cash Flow analysis for any US-listed stock*")
st.divider()

# ── Sidebar Inputs ────────────────────────────────────────
st.sidebar.header("⚙️ Inputs")
ticker = st.sidebar.text_input("Stock Ticker", value="AAPL").upper()
current_price = st.sidebar.number_input("Current Market Price ($)", value=291.13, step=0.01)
years = st.sidebar.slider("Projection Years", min_value=3, max_value=10, value=5)
terminal_growth = st.sidebar.slider("Terminal Growth Rate (%)", min_value=1.0, max_value=4.0, value=2.5) / 100
tax_rate = st.sidebar.slider("Tax Rate (%)", min_value=10, max_value=35, value=21) / 100

st.sidebar.divider()
st.sidebar.header("🔧 Manual Overrides")
manual_growth = st.sidebar.number_input("FCF Growth Rate Override (%, 0 = auto)", value=0.0, step=0.5) / 100
manual_wacc = st.sidebar.number_input("WACC Override (%, 0 = auto)", value=0.0, step=0.1) / 100
total_debt = st.sidebar.number_input("Total Debt ($B)", value=97.0, step=1.0) * 1e9
cash = st.sidebar.number_input("Cash ($B)", value=35.9, step=1.0) * 1e9
shares = st.sidebar.number_input("Shares Outstanding ($B)", value=15.1, step=0.1) * 1e9

run = st.sidebar.button("🚀 Run Valuation", type="primary")

# ── Main Content ──────────────────────────────────────────
if run:
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            # Fetch financials
            income, balance, cashflow = get_financials(ticker)

            if cashflow.empty:
                st.error("⚠️ Could not fetch data. API rate limit may be hit. Try again later.")
                st.stop()

            # Calculate FCF
            fcf_df = calculate_historical_fcf(cashflow)
            growth_rate = manual_growth if manual_growth > 0 else calculate_fcf_growth_rate(fcf_df)
            proj_df = project_fcf(fcf_df, growth_rate, years=years)

            # WACC
            wacc = manual_wacc if manual_wacc > 0 else calculate_wacc(ticker)

            # DCF calculation
            proj_fcfs = proj_df["projectedFCF"].values
            pv_fcfs = sum([fcf / (1 + wacc) ** (i+1) for i, fcf in enumerate(proj_fcfs)])
            terminal_value = proj_fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
            pv_terminal = terminal_value / (1 + wacc) ** years
            enterprise_value = pv_fcfs + pv_terminal
            equity_value = enterprise_value - total_debt + cash
            intrinsic_value = equity_value / shares if shares > 0 else 0
            upside = (intrinsic_value - current_price) / current_price * 100

            # ── Valuation Summary ─────────────────────────
            st.header("💰 Valuation Summary")
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Intrinsic Value", f"${intrinsic_value:.2f}")
            col2.metric("Current Price", f"${current_price:.2f}")
            col3.metric("Upside/Downside", f"{upside:+.1f}%",
                        delta=f"{upside:+.1f}%",
                        delta_color="normal")
            col4.metric("Verdict",
                        "🟢 UNDERVALUED" if upside > 10 else "🔴 OVERVALUED" if upside < -10 else "🟡 FAIR VALUE")

            st.divider()

            # ── FCF Chart ─────────────────────────────────
            st.header("📊 Free Cash Flow Analysis")
            col1, col2 = st.columns([2, 1])

            with col1:
                fig, ax = plt.subplots(figsize=(12, 5))
                plt.style.use("seaborn-v0_8-darkgrid")
                fcf_values = fcf_df["freeCashFlow"].values / 1e9
                hist_years = fcf_df["fiscalDateEnding"].str[:4].values
                ax.bar(hist_years, fcf_values, color="#2196F3", alpha=0.8, label="Historical FCF")
                proj_years = [str(int(hist_years[-1]) + i) for i in range(1, len(proj_df)+1)]
                proj_values = proj_df["projectedFCF"].values / 1e9
                ax.plot(proj_years, proj_values, color="#FF9800", linewidth=2.5,
                        linestyle="--", marker="o", markersize=7, label="Projected FCF")
                ax.plot([hist_years[-1], proj_years[0]], [fcf_values[-1], proj_values[0]],
                        color="#FF9800", linewidth=2, linestyle="--", alpha=0.5)
                ax.set_title(f"{ticker} — FCF History & Projection", fontsize=13, fontweight="bold")
                ax.set_xlabel("Year")
                ax.set_ylabel("FCF ($B)")
                ax.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

            with col2:
                st.subheader("📋 Projected FCFs")
                display_df = proj_df.copy()
                display_df["projectedFCF"] = display_df["projectedFCF"].apply(lambda x: f"${x/1e9:.2f}B")
                st.dataframe(display_df[["year", "projectedFCF"]], hide_index=True)
                st.metric("FCF Growth Rate", f"{growth_rate:.2%}")
                st.metric("WACC", f"{wacc:.2%}")

            st.divider()

            # ── Sensitivity Heatmap ───────────────────────
            st.header("🔥 Sensitivity Analysis")
            df_sensitivity = sensitivity_analysis(
                intrinsic_value, wacc, growth_rate,
                fcf_df["freeCashFlow"].iloc[-1],
                total_debt, cash, shares
            )

            fig2, ax2 = plt.subplots(figsize=(14, 7))
            sns.heatmap(df_sensitivity.astype(float), annot=True, fmt=".0f",
                        cmap="RdYlGn", center=current_price, linewidths=0.5,
                        ax=ax2, cbar_kws={"label": "Intrinsic Value ($)"})
            ax2.set_title(f"{ticker} Sensitivity — WACC vs FCF Growth Rate\n"
                          f"Green = Undervalued vs ${current_price:.2f}",
                          fontsize=12, fontweight="bold")
            ax2.set_xlabel("FCF Growth Rate")
            ax2.set_ylabel("WACC")
            plt.tight_layout()
            st.pyplot(fig2)

            st.divider()

            # ── Bull/Base/Bear ────────────────────────────
            st.header("🎯 Scenario Analysis")
            scenarios = {
                "🐻 Bear": {"growth": 0.05, "wacc": wacc + 0.02},
                "📊 Base": {"growth": growth_rate, "wacc": wacc},
                "🐂 Bull": {"growth": min(growth_rate + 0.05, 0.25), "wacc": wacc - 0.02},
            }

            scenario_results = []
            for name, params in scenarios.items():
                g, w = params["growth"], params["wacc"]
                pf = [fcf_df["freeCashFlow"].iloc[-1] * (1 + g) ** y for y in range(1, years+1)]
                pv = sum([f / (1 + w) ** (i+1) for i, f in enumerate(pf)])
                tv = pf[-1] * (1 + terminal_growth) / (w - terminal_growth)
                ptv = tv / (1 + w) ** years
                ev = pv + ptv
                eqv = ev - total_debt + cash
                iv = eqv / shares
                up = (iv - current_price) / current_price * 100
                scenario_results.append({
                    "Scenario": name,
                    "Growth Rate": f"{g:.0%}",
                    "WACC": f"{w:.2%}",
                    "Intrinsic Value": f"${iv:.2f}",
                    "Upside": f"{up:+.1f}%"
                })

            st.dataframe(pd.DataFrame(scenario_results), hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Make sure your API key is set and the ticker is valid.")

else:
    st.info("👈 Enter a stock ticker in the sidebar and click **Run Valuation** to start!")
    st.markdown("""
    ### How it works:
    1. Enter any US stock ticker (e.g. AAPL, MSFT, GOOGL)
    2. Enter the current market price
    3. Adjust assumptions if needed
    4. Click Run Valuation

    ### What you get:
    - 📊 Intrinsic value per share
    - 📈 FCF history & 5-year projection
    - 🔥 Sensitivity heatmap
    - 🎯 Bull/Base/Bear scenarios
    """)