import numpy as np
from scipy import stats

class ABTester:
    """
    Core A/B testing class supporting:
    - t-test (continuous metrics e.g. revenue per user)
    - chi-square test (categorical metrics)
    - proportion z-test (binary metrics e.g. conversion rate)
    """

    def __init__(self, control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05):
        self.control = np.array(control)
        self.treatment = np.array(treatment)
        self.alpha = alpha  # significance level

    def t_test(self):
        """For continuous metrics — compares means of two groups."""
        t_stat, p_value = stats.ttest_ind(self.control, self.treatment)
        significant = p_value < self.alpha

        print("\n✅ T-Test Results:")
        print(f"  Control mean:   {self.control.mean():.4f}")
        print(f"  Treatment mean: {self.treatment.mean():.4f}")
        print(f"  T-statistic:    {t_stat:.4f}")
        print(f"  P-value:        {p_value:.4f}")
        print(f"  Significant:    {'✅ Yes' if significant else '❌ No'} (alpha={self.alpha})")

        return {"test": "t-test", "t_stat": t_stat, "p_value": p_value, "significant": significant}

    def chi_square_test(self, control_success: int, control_total: int,
                         treatment_success: int, treatment_total: int):
        """For categorical metrics — compares proportions using contingency table."""
        contingency_table = [
            [control_success, control_total - control_success],
            [treatment_success, treatment_total - treatment_success]
        ]
        chi2, p_value, dof, _ = stats.chi2_contingency(contingency_table)
        significant = p_value < self.alpha

        print("\n✅ Chi-Square Test Results:")
        print(f"  Control rate:   {control_success/control_total:.4f}")
        print(f"  Treatment rate: {treatment_success/treatment_total:.4f}")
        print(f"  Chi2-statistic: {chi2:.4f}")
        print(f"  P-value:        {p_value:.4f}")
        print(f"  Significant:    {'✅ Yes' if significant else '❌ No'} (alpha={self.alpha})")

        return {"test": "chi-square", "chi2": chi2, "p_value": p_value, "significant": significant}

    def proportion_z_test(self):
        """For binary metrics — compares conversion rates between two groups."""
        from statsmodels.stats.proportion import proportions_ztest

        count = np.array([self.treatment.sum(), self.control.sum()])
        nobs = np.array([len(self.treatment), len(self.control)])

        z_stat, p_value = proportions_ztest(count, nobs)
        significant = bool(p_value < self.alpha)

        print("\n✅ Proportion Z-Test Results:")
        print(f"  Control rate:   {self.control.mean():.4f}")
        print(f"  Treatment rate: {self.treatment.mean():.4f}")
        print(f"  Z-statistic:    {z_stat:.4f}")
        print(f"  P-value:        {p_value:.4f}")
        print(f"  Significant:    {'✅ Yes' if significant else '❌ No'} (alpha={self.alpha})")

        return {"test": "z-test", "z_stat": z_stat, "p_value": p_value, "significant": significant}
    def cohen_d(self) -> float:
        """
        Effect size — how meaningful is the difference, not just significant?
        Small: 0.2 | Medium: 0.5 | Large: 0.8
        """
        pooled_std = np.sqrt(
            (np.std(self.control, ddof=1)**2 + np.std(self.treatment, ddof=1)**2) / 2
        )
        d = (self.treatment.mean() - self.control.mean()) / pooled_std

        if abs(d) < 0.2:
            size = "Negligible"
        elif abs(d) < 0.5:
            size = "Small"
        elif abs(d) < 0.8:
            size = "Medium"
        else:
            size = "Large"

        print(f"\n✅ Effect Size (Cohen's d):")
        print(f"   Cohen's d:  {d:.4f} ({size})")
        return d

    def confidence_interval(self) -> tuple:
        """
        95% Confidence Interval for the difference in means.
        Tells you the range where the true difference likely lies.
        """
        diff = self.treatment.mean() - self.control.mean()
        se = np.sqrt(
            np.var(self.control, ddof=1)/len(self.control) +
            np.var(self.treatment, ddof=1)/len(self.treatment)
        )
        margin = 1.96 * se  # 1.96 = z-score for 95% confidence

        lower = diff - margin
        upper = diff + margin

        print(f"\n✅ 95% Confidence Interval for difference in means:")
        print(f"   Difference:  {diff:.4f}")
        print(f"   CI:          [{lower:.4f}, {upper:.4f}]")
        print(f"   Interpretation: The true difference is between {lower:.4f} and {upper:.4f} with 95% confidence")

        return lower, upper

if __name__ == "__main__":
    from simulator import simulate_ab_test

    print("=" * 40)
    print("TEST 1 — Continuous Metric (T-Test)")
    print("=" * 40)
    _, control, treatment = simulate_ab_test(metric_type="continuous")
    tester = ABTester(control, treatment)
    tester.t_test()
    tester.cohen_d()
    tester.confidence_interval()

    print("\n" + "=" * 40)
    print("TEST 2 — Binary Metric (Z-Test)")
    print("=" * 40)
    _, control, treatment = simulate_ab_test(metric_type="binary")
    tester2 = ABTester(control, treatment)
    tester2.proportion_z_test()
    tester2.cohen_d()
    tester2.confidence_interval()

    print("\n" + "=" * 40)
    print("TEST 3 — Chi-Square Test")
    print("=" * 40)
    tester2.chi_square_test(
        control_success=int(control.sum()), control_total=len(control),
        treatment_success=int(treatment.sum()), treatment_total=len(treatment)
    )