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
        significant = p_value < self.alpha

        print("\n✅ Proportion Z-Test Results:")
        print(f"  Control rate:   {self.control.mean():.4f}")
        print(f"  Treatment rate: {self.treatment.mean():.4f}")
        print(f"  Z-statistic:    {z_stat:.4f}")
        print(f"  P-value:        {p_value:.4f}")
        print(f"  Significant:    {'✅ Yes' if significant else '❌ No'} (alpha={self.alpha})")

        return {"test": "z-test", "z_stat": z_stat, "p_value": p_value, "significant": significant}


if __name__ == "__main__":
    from simulator import simulate_ab_test

    print("=" * 40)
    print("TEST 1 — Continuous Metric (T-Test)")
    print("=" * 40)
    _, control, treatment = simulate_ab_test(metric_type="continuous")
    tester = ABTester(control, treatment)
    tester.t_test()

    print("\n" + "=" * 40)
    print("TEST 2 — Binary Metric (Z-Test)")
    print("=" * 40)
    _, control, treatment = simulate_ab_test(metric_type="binary")
    tester2 = ABTester(control, treatment)
    tester2.proportion_z_test()

    print("\n" + "=" * 40)
    print("TEST 3 — Chi-Square Test")
    print("=" * 40)
    tester2.chi_square_test(
        control_success=int(control.sum()), control_total=len(control),
        treatment_success=int(treatment.sum()), treatment_total=len(treatment)
    )