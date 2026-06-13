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


if __name__ == "__main__":
    # Example 1 — small effect
    minimum_sample_size(effect_size=0.2, power=0.80)

    # Example 2 — medium effect
    minimum_sample_size(effect_size=0.5, power=0.80)

    # Example 3 — large effect
    minimum_sample_size(effect_size=0.8, power=0.80)

    # Full reference table
    power_table()