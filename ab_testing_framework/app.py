import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import sys
sys.path.append("/Users/venshajmmera/projects/ab_testing_framework")

from ab_tester import ABTester
from power_analysis import minimum_sample_size, post_hoc_power_check, bonferroni_correction
from simulator import simulate_ab_test
from diagnostics import check_sample_ratio_mismatch

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="A/B Testing Framework",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 A/B Testing Framework")
st.markdown("*Production-grade statistical testing for experiments*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
mode = st.sidebar.radio("Data Source", ["Upload CSV", "Use Simulated Data"])
alpha = st.sidebar.slider("Significance Level (α)", 0.01, 0.10, 0.05, 0.01)
metric_type = st.sidebar.selectbox("Metric Type", ["continuous", "binary"])

# ── Data Loading ──────────────────────────────────────────
control, treatment = None, None

if mode == "Upload CSV":
    st.sidebar.info("CSV must have columns: 'group' (control/treatment) and 'value'")
    uploaded = st.sidebar.file_uploader("Upload experiment CSV", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        control = df[df["group"] == "control"]["value"].values
        treatment = df[df["group"] == "treatment"]["value"].values
        st.success(f"✅ Loaded {len(df)} rows — Control: {len(control)}, Treatment: {len(treatment)}")

elif mode == "Use Simulated Data":
    st.sidebar.subheader("Simulation Settings")
    n_control = st.sidebar.number_input("Control Size", value=5000, step=500)
    n_treatment = st.sidebar.number_input("Treatment Size", value=5000, step=500)

    if metric_type == "binary":
        control_rate = st.sidebar.slider("Control Conversion Rate (%)", 1.0, 20.0, 4.2) / 100
        treatment_rate = st.sidebar.slider("Treatment Conversion Rate (%)", 1.0, 20.0, 5.8) / 100
        _, control, treatment = simulate_ab_test(
            n_control=int(n_control), n_treatment=int(n_treatment),
            control_conversion=control_rate, treatment_conversion=treatment_rate,
            metric_type="binary"
        )
    else:
        control_mean = st.sidebar.slider("Control Mean", 10.0, 100.0, 50.0)
        treatment_mean = st.sidebar.slider("Treatment Mean", 10.0, 100.0, 52.0)
        _, control, treatment = simulate_ab_test(
            n_control=int(n_control), n_treatment=int(n_treatment),
            metric_type="continuous"
        )
        # Override means
        np.random.seed(42)
        control = np.random.normal(control_mean, 10, int(n_control))
        treatment = np.random.normal(treatment_mean, 10, int(n_treatment))

    st.sidebar.success("✅ Simulated data ready!")

run = st.sidebar.button("🚀 Run Analysis", type="primary")

# ── Analysis ──────────────────────────────────────────────
if run and control is not None and treatment is not None:
    tester = ABTester(control, treatment, alpha=alpha)

    # ── Summary Metrics ───────────────────────────────────
    st.header("📊 Experiment Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Control Mean", f"{control.mean():.4f}")
    col2.metric("Treatment Mean", f"{treatment.mean():.4f}")
    col3.metric("Lift", f"{((treatment.mean()-control.mean())/control.mean()*100):+.2f}%")
    col4.metric("Sample Size", f"{len(control)+len(treatment):,}")

    st.divider()

    # ── Statistical Tests ─────────────────────────────────
    st.header("🔬 Statistical Tests")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("T-Test (Continuous)")
        t_result = tester.t_test()
        st.metric("P-Value", f"{t_result['p_value']:.4f}")
        st.metric("T-Statistic", f"{t_result['t_stat']:.4f}")
        st.success("✅ Significant" if t_result["significant"] else "❌ Not Significant")

        d = tester.cohen_d()
        size = "Negligible" if abs(d) < 0.2 else "Small" if abs(d) < 0.5 else "Medium" if abs(d) < 0.8 else "Large"
        st.metric("Cohen's d (Effect Size)", f"{d:.4f} ({size})")

    with col2:
        st.subheader("Z-Test (Binary/Proportion)")
        z_result = tester.proportion_z_test()
        st.metric("P-Value", f"{z_result['p_value']:.4f}")
        st.metric("Z-Statistic", f"{z_result['z_stat']:.4f}")
        st.success("✅ Significant" if z_result["significant"] else "❌ Not Significant")

        lower, upper = tester.confidence_interval()
        st.metric("95% CI Lower", f"{lower:.4f}")
        st.metric("95% CI Upper", f"{upper:.4f}")

    st.divider()

    # ── Distribution Plot ─────────────────────────────────
    st.header("📈 Distribution Comparison")
    fig, ax = plt.subplots(figsize=(12, 5))
    plt.style.use("seaborn-v0_8-darkgrid")
    sns.kdeplot(control, ax=ax, color="#2196F3", linewidth=2.5,
                label=f"Control (μ={control.mean():.3f})", fill=True, alpha=0.3)
    sns.kdeplot(treatment, ax=ax, color="#FF9800", linewidth=2.5,
                label=f"Treatment (μ={treatment.mean():.3f})", fill=True, alpha=0.3)
    ax.axvline(control.mean(), color="#2196F3", linestyle="--", linewidth=1.5)
    ax.axvline(treatment.mean(), color="#FF9800", linestyle="--", linewidth=1.5)
    ax.set_title("Control vs Treatment Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.legend(fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)

    st.divider()

    # ── Power Analysis ────────────────────────────────────
    st.header("⚡ Power Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Post-Hoc Power Check")
        power_result = post_hoc_power_check(control, treatment, alpha=alpha)
        st.metric("Achieved Power", f"{power_result['achieved_power']:.2%}")
        st.metric("Effect Size", f"{power_result['effect_size']:.4f}")
        if power_result["achieved_power"] >= 0.80:
            st.success("✅ Well powered — results reliable")
        elif power_result["achieved_power"] >= 0.60:
            st.warning("⚠️ Borderline — interpret with caution")
        else:
            st.error("❌ Underpowered — results unreliable")

    with col2:
        st.subheader("Minimum Sample Size Calculator")
        effect_input = st.selectbox("Effect Size", ["Small (0.2)", "Medium (0.5)", "Large (0.8)"])
        power_input = st.selectbox("Desired Power", ["70%", "80%", "90%"])
        effect_map = {"Small (0.2)": 0.2, "Medium (0.5)": 0.5, "Large (0.8)": 0.8}
        power_map = {"70%": 0.70, "80%": 0.80, "90%": 0.90}
        n = minimum_sample_size(
            effect_size=effect_map[effect_input],
            power=power_map[power_input],
            alpha=alpha
        )
        st.metric("Required per Group", f"{n:,}")
        st.metric("Total Required", f"{n*2:,}")

    st.divider()

    # ── Diagnostics ───────────────────────────────────────
    st.header("🔍 Experiment Diagnostics")
    col1, col2, col3 = st.columns(3)

    srm = abs(len(control)/(len(control)+len(treatment)) - 0.5) > 0.01
    col1.metric("Sample Ratio Mismatch", "⚠️ Detected" if srm else "✅ Clean")

    novelty = False
    mid = len(treatment) // 2
    if len(treatment) > 10:
        early_mean = treatment[:mid].mean()
        late_mean = treatment[mid:].mean()
        drop = (early_mean - late_mean) / early_mean * 100
        novelty = drop > 20
    col2.metric("Novelty Effect", "⚠️ Detected" if novelty else "✅ Clean")
    col3.metric("Overall Health", "⚠️ Check Issues" if (srm or novelty) else "✅ Experiment Clean")

    st.divider()

    # ── Multiple Testing ──────────────────────────────────
    st.header("🔧 Multiple Testing Correction")
    st.info("Simulating 3 metrics tested simultaneously")
    p_values = [t_result["p_value"], z_result["p_value"], 0.001]
    metric_names = ["Primary Metric", "Secondary Metric", "Guardrail Metric"]

    correction_df = []
    corrected_alpha = alpha / len(p_values)
    for name, p in zip(metric_names, p_values):
        correction_df.append({
            "Metric": name,
            "P-Value": f"{p:.4f}",
            "Bonferroni Significant": "✅ Yes" if p < corrected_alpha else "❌ No",
            "Original Significant": "✅ Yes" if p < alpha else "❌ No"
        })
    st.dataframe(pd.DataFrame(correction_df), hide_index=True, use_container_width=True)
    st.caption(f"Bonferroni corrected α = {corrected_alpha:.4f} (original α = {alpha})")

elif run:
    st.error("⚠️ No data loaded. Please upload a CSV or use simulated data.")
else:
    st.info("👈 Configure your experiment in the sidebar and click **Run Analysis**!")
    st.markdown("""
    ### Features:
    - 📊 T-test, Z-test, Chi-square testing
    - 📏 Effect size (Cohen's d) & confidence intervals
    - ⚡ Power analysis & minimum sample size calculator
    - 🔍 Experiment diagnostics (SRM, novelty effect)
    - 🔧 Multiple testing corrections (Bonferroni)

    ### How to use:
    1. Choose data source — upload your own CSV or use simulated data
    2. Select metric type (continuous or binary)
    3. Adjust significance level
    4. Click Run Analysis
    """)