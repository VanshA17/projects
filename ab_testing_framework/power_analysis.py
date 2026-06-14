import numpy as np
from statsmodels.stats.power import TTestIndPower, NormalIndPower

def minimum_sample_size(effect_size: float = 0.2, alpha: float = 0.05, power: float = 0.80, test_type: str = "t-test") -> int:
    """
    Calculates minimum sample size per group needed to detect an effect.

    Parameters:
    - effect_size: Cohen's d (0.2=small, 0.5=medium, 0.8=large)
    - alpha: significance level (default 0.05)
    - power: probability of detecting real effect (default 0.80 = 80%)
    - test_type: "t-test" or "z-test"
    """
    if test_type == "t-test":
        analysis = TTestIndPower()
    else:
        analysis = NormalIndPower()

    sample_size = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative="two-sided"
    )

    sample_size = int(np.ceil(sample_size))

    print(f"\n✅ Minimum Sample Size Calculator")
    print(f"   Effect Size:   {effect_size} ({'Small' if effect_size==0.2 else 'Medium' if effect_size==0.5 else 'Large'})")
    print(f"   Alpha:         {alpha} ({(1-alpha)*100:.0f}% confidence)")
    print(f"   Power:         {power} ({power*100:.0f}% chance of detecting real effect)")
    print(f"   Sample Size:   {sample_size} per group ({sample_size*2} total)")

    return sample_size


def power_table():
    """Prints a table of sample sizes for different effect sizes and power levels."""
    print("\n✅ Sample Size Reference Table (alpha=0.05):")
    print(f"{'Effect Size':<15} {'Power=70%':<15} {'Power=80%':<15} {'Power=90%':<15}")
    print("-" * 55)

    for effect, label in [(0.2, "Small"), (0.5, "Medium"), (0.8, "Large")]:
        row = f"{label} ({effect})     "
        for power in [0.70, 0.80, 0.90]:
            analysis = TTestIndPower()
            n = int(np.ceil(analysis.solve_power(effect_size=effect, alpha=0.05, power=power)))
            row += f"{n} per group    "
        print(row)

def post_hoc_power_check(control: np.ndarray,
                          treatment: np.ndarray,
                          alpha: float = 0.05) -> dict:
    """
    Checks if a completed experiment had enough power.
    Calculates achieved power given actual sample size and effect size.
    """
    from statsmodels.stats.power import TTestIndPower
    import numpy as np

    n = min(len(control), len(treatment))

    # Calculate actual effect size (Cohen's d)
    pooled_std = np.sqrt(
        (np.std(control, ddof=1)**2 + np.std(treatment, ddof=1)**2) / 2
    )
    effect_size = abs(treatment.mean() - control.mean()) / pooled_std

    # Calculate achieved power
    analysis = TTestIndPower()
    achieved_power = analysis.solve_power(
        effect_size=effect_size,
        nobs1=n,
        alpha=alpha,
        alternative="two-sided"
    )

    print(f"\n✅ Post-Hoc Power Analysis:")
    print(f"   Sample Size:       {n} per group ({n*2} total)")
    print(f"   Effect Size:       {effect_size:.4f}")
    print(f"   Achieved Power:    {achieved_power:.2%}")

    if achieved_power >= 0.80:
        print(f"   Verdict:           ✅ Well powered — results are reliable")
    elif achieved_power >= 0.60:
        print(f"   Verdict:           ⚠️ Borderline — interpret results with caution")
    else:
        print(f"   Verdict:           ❌ Underpowered — results may be unreliable")

    return {
        "sample_size": n,
        "effect_size": effect_size,
        "achieved_power": achieved_power
    }


def bonferroni_correction(p_values: list, alpha: float = 0.05) -> dict:
    """
    Bonferroni correction for multiple hypothesis testing.
    Adjusts significance threshold when testing multiple metrics simultaneously.
    """
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests

    print(f"\n✅ Bonferroni Correction:")
    print(f"   Number of tests:       {n_tests}")
    print(f"   Original alpha:        {alpha}")
    print(f"   Corrected alpha:       {corrected_alpha:.4f}")
    print(f"\n   Results:")
    print(f"   {'Metric':<12} {'P-Value':<12} {'Significant?'}")
    print(f"   {'-'*40}")

    results = []
    for i, p in enumerate(p_values):
        significant = p < corrected_alpha
        print(f"   Metric {i+1}     {p:<12.4f} {'✅ Yes' if significant else '❌ No'}")
        results.append({"metric": f"Metric {i+1}", "p_value": p, "significant": significant})

    return {"corrected_alpha": corrected_alpha, "results": results}


def benjamini_hochberg(p_values: list, alpha: float = 0.05) -> dict:
    """
    Benjamini-Hochberg correction — less strict than Bonferroni.
    Controls False Discovery Rate (FDR) instead of Family-wise Error Rate.
    """
    import numpy as np
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    print(f"\n✅ Benjamini-Hochberg (FDR) Correction:")
    print(f"   Number of tests:   {n}")
    print(f"   Alpha (FDR):       {alpha}")
    print(f"\n   {'Rank':<8} {'P-Value':<12} {'BH Threshold':<16} {'Significant?'}")
    print(f"   {'-'*50}")

    results = []
    significant_flags = []
    for rank, (idx, p) in enumerate(zip(sorted_indices, sorted_p), 1):
        bh_threshold = (rank / n) * alpha
        significant = p <= bh_threshold
        significant_flags.append(significant)
        print(f"   {rank:<8} {p:<12.4f} {bh_threshold:<16.4f} {'✅ Yes' if significant else '❌ No'}")
        results.append({"metric": f"Metric {idx+1}", "p_value": p, "significant": significant})

    return {"results": results}


if __name__ == "__main__":
    import numpy as np
    from simulator import simulate_ab_test

    # --- Sample size calculations ---
    minimum_sample_size(effect_size=0.2, power=0.80)
    minimum_sample_size(effect_size=0.5, power=0.80)
    minimum_sample_size(effect_size=0.8, power=0.80)
    power_table()

    # --- Post-hoc power check ---
    print("\n" + "="*40)
    print("POST-HOC POWER CHECK")
    print("="*40)
    _, control, treatment = simulate_ab_test(metric_type="continuous")
    post_hoc_power_check(control, treatment)

    # --- Bonferroni correction ---
    print("\n" + "="*40)
    print("MULTIPLE TESTING CORRECTIONS")
    print("="*40)
    # Simulate 3 metrics being tested simultaneously
    p_values = [0.03, 0.04, 0.001]
    bonferroni_correction(p_values)

    # --- Benjamini-Hochberg ---
    benjamini_hochberg(p_values)