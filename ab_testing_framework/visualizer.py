import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import scipy.stats as stats

plt.style.use("seaborn-v0_8-darkgrid")
COLORS = {"control": "#2196F3", "treatment": "#FF9800", "significant": "#4CAF50", "not_significant": "#F44336"}


def plot_distributions(control: np.ndarray,
                        treatment: np.ndarray,
                        metric_name: str = "Metric",
                        ticker: str = "experiment"):
    """
    KDE distribution plot comparing control vs treatment.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    sns.kdeplot(control, ax=ax, color=COLORS["control"],
                linewidth=2.5, label=f"Control (mean={control.mean():.3f})", fill=True, alpha=0.3)
    sns.kdeplot(treatment, ax=ax, color=COLORS["treatment"],
                linewidth=2.5, label=f"Treatment (mean={treatment.mean():.3f})", fill=True, alpha=0.3)

    # Mean lines
    ax.axvline(control.mean(), color=COLORS["control"], linestyle="--", linewidth=1.5)
    ax.axvline(treatment.mean(), color=COLORS["treatment"], linestyle="--", linewidth=1.5)

    # Difference annotation
    diff = treatment.mean() - control.mean()
    ax.annotate(f"Δ = {diff:.3f}", xy=(treatment.mean(), ax.get_ylim()[1] * 0.8),
                fontsize=11, color="black", fontweight="bold")

    ax.set_title(f"A/B Test — {metric_name} Distribution", fontsize=13, fontweight="bold")
    ax.set_xlabel(metric_name, fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(f"{ticker}_distribution.png", dpi=150)
    plt.show()
    print(f"✅ Distribution plot saved as {ticker}_distribution.png")


def plot_confidence_intervals(results: list, metric_names: list = None):
    """
    Plots confidence intervals for multiple metrics side by side.
    results = list of (diff, lower, upper, significant) tuples
    """
    if metric_names is None:
        metric_names = [f"Metric {i+1}" for i in range(len(results))]

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, (diff, lower, upper, significant) in enumerate(results):
        color = COLORS["significant"] if significant else COLORS["not_significant"]

        # CI line
        ax.plot([lower, upper], [i, i], color=color, linewidth=3, alpha=0.8)

        # Center point
        ax.scatter([diff], [i], color=color, s=100, zorder=5)

        # Value labels
        ax.text(upper + 0.001, i, f"{diff:+.4f} [{lower:.4f}, {upper:.4f}]",
                va="center", fontsize=9)

    # Zero line
    ax.axvline(x=0, color="black", linestyle="--", linewidth=1.5, alpha=0.7, label="No effect (0)")

    ax.set_yticks(range(len(results)))
    ax.set_yticklabels(metric_names, fontsize=10)
    ax.set_xlabel("Difference (Treatment - Control)", fontsize=11)
    ax.set_title("95% Confidence Intervals by Metric", fontsize=13, fontweight="bold")

    sig_patch = plt.Line2D([0], [0], color=COLORS["significant"], linewidth=3, label="Significant ✅")
    not_sig_patch = plt.Line2D([0], [0], color=COLORS["not_significant"], linewidth=3, label="Not Significant ❌")
    ax.legend(handles=[sig_patch, not_sig_patch], fontsize=10)

    plt.tight_layout()
    plt.savefig("confidence_intervals.png", dpi=150)
    plt.show()
    print("✅ CI plot saved as confidence_intervals.png")


def plot_pvalue_over_time(p_values: list, alpha: float = 0.05):
    """
    Plots p-value trajectory over time — shows peeking risk visually.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    x = list(range(1, len(p_values) + 1))
    ax.plot(x, p_values, color="#2196F3", linewidth=2.5, marker="o", markersize=7, label="P-value")

    # Significance threshold
    ax.axhline(y=alpha, color="#F44336", linestyle="--", linewidth=2,
               label=f"α = {alpha} (significance threshold)")

    # Shade significant region
    ax.fill_between(x, p_values, alpha,
                    where=[p < alpha for p in p_values],
                    color="#4CAF50", alpha=0.2, label="Significant region")

    ax.set_title("P-value Over Time — Peeking Risk Visualization", fontsize=13, fontweight="bold")
    ax.set_xlabel("Checkpoint (Day / Week)", fontsize=11)
    ax.set_ylabel("P-value", fontsize=11)
    ax.set_ylim(0, max(p_values) * 1.2)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig("pvalue_over_time.png", dpi=150)
    plt.show()
    print("✅ P-value trajectory saved as pvalue_over_time.png")


def plot_sample_size_curves():
    """
    Plots sample size curves for different effect sizes and power levels.
    """
    from statsmodels.stats.power import TTestIndPower

    fig, ax = plt.subplots(figsize=(12, 6))
    analysis = TTestIndPower()
    effect_sizes = [0.2, 0.5, 0.8]
    power_range = np.arange(0.5, 0.99, 0.01)
    colors = ["#F44336", "#FF9800", "#4CAF50"]
    labels = ["Small (d=0.2)", "Medium (d=0.5)", "Large (d=0.8)"]

    for effect, color, label in zip(effect_sizes, colors, labels):
        sample_sizes = [
            analysis.solve_power(effect_size=effect, alpha=0.05, power=p)
            for p in power_range
        ]
        ax.plot(power_range * 100, sample_sizes, color=color, linewidth=2.5, label=label)

    ax.axvline(x=80, color="black", linestyle="--", linewidth=1.5, alpha=0.7, label="80% power (standard)")
    ax.set_title("Sample Size Required by Effect Size & Power", fontsize=13, fontweight="bold")
    ax.set_xlabel("Statistical Power (%)", fontsize=11)
    ax.set_ylabel("Sample Size per Group", fontsize=11)
    ax.set_yscale("log")
    ax.legend(fontsize=10)
    ax.set_ylim(10, 10000)
    plt.tight_layout()
    plt.savefig("sample_size_curves.png", dpi=150)
    plt.show()
    print("✅ Sample size curves saved as sample_size_curves.png")


if __name__ == "__main__":
    from simulator import simulate_ab_test
    from ab_tester import ABTester

    # Plot 1 — Distribution plot
    _, control, treatment = simulate_ab_test(metric_type="continuous")
    plot_distributions(control, treatment, metric_name="Revenue per User", ticker="ecommerce")

    # Plot 2 — Confidence intervals for 3 metrics
    tester = ABTester(control, treatment)
    tester.t_test()
    lower, upper = tester.confidence_interval()
    diff = treatment.mean() - control.mean()

    results = [
        (diff, lower, upper, True),
        (0.002, -0.001, 0.005, False),
        (0.015, 0.008, 0.022, True),
    ]
    plot_confidence_intervals(results, metric_names=["Revenue/User", "Click Rate", "Conversion Rate"])

    # Plot 3 — P-value over time
    p_values = [0.12, 0.08, 0.04, 0.06, 0.03, 0.07, 0.04, 0.03, 0.02, 0.01]
    plot_pvalue_over_time(p_values)

    # Plot 4 — Sample size curves
    plot_sample_size_curves()