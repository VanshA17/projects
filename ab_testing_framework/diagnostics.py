import numpy as np
import pandas as pd

def check_sample_ratio_mismatch(n_control: int,
                                 n_treatment: int,
                                 expected_ratio: float = 0.5) -> bool:
    """
    Sample Ratio Mismatch (SRM) — checks if traffic was split correctly.
    If you intended 50/50 split but got 60/40, something went wrong in assignment.
    """
    total = n_control + n_treatment
    actual_ratio = n_control / total
    deviation = abs(actual_ratio - expected_ratio)

    print(f"\n✅ Sample Ratio Mismatch Check:")
    print(f"   Control:        {n_control} ({actual_ratio:.1%})")
    print(f"   Treatment:      {n_treatment} ({1-actual_ratio:.1%})")
    print(f"   Expected Split: {expected_ratio:.0%}/{1-expected_ratio:.0%}")
    print(f"   Deviation:      {deviation:.1%}")

    if deviation > 0.01:
        print(f"   Verdict: ⚠️ SRM detected! Traffic split is off — results may be unreliable")
        return True
    else:
        print(f"   Verdict: ✅ Traffic split looks correct")
        return False


def check_novelty_effect(early_data: np.ndarray,
                          late_data: np.ndarray) -> bool:
    """
    Novelty effect — users behave differently at the start of an experiment
    just because something is new. Check if early conversion >> late conversion.
    """
    early_mean = early_data.mean()
    late_mean = late_data.mean()
    drop = (early_mean - late_mean) / early_mean * 100

    print(f"\n✅ Novelty Effect Check:")
    print(f"   Early period mean:  {early_mean:.4f}")
    print(f"   Late period mean:   {late_mean:.4f}")
    print(f"   Drop:               {drop:.1f}%")

    if drop > 20:
        print(f"   Verdict: ⚠️ Novelty effect likely! Early enthusiasm fading — run test longer")
        return True
    else:
        print(f"   Verdict: ✅ No significant novelty effect detected")
        return False


def check_peeking(p_values_over_time: list, alpha: float = 0.05) -> bool:
    """
    Peeking — stopping an experiment early when p-value crosses 0.05.
    This massively inflates false positive rate.
    """
    early_significant = [p for p in p_values_over_time[:len(p_values_over_time)//2] if p < alpha]

    print(f"\n✅ Peeking Risk Check:")
    print(f"   Total checkpoints:     {len(p_values_over_time)}")
    print(f"   Early significants:    {len(early_significant)}")

    if len(early_significant) > 0:
        print(f"   Verdict: ⚠️ Peeking risk! Significant results detected early — don't stop yet")
        print(f"   Tip: Use sequential testing or pre-commit to a fixed sample size")
        return True
    else:
        print(f"   Verdict: ✅ No peeking issues detected")
        return False


def full_diagnostic_report(n_control: int,
                            n_treatment: int,
                            treatment_data: np.ndarray) -> dict:
    """Runs all diagnostic checks and prints a full report."""
    print(f"\n{'='*50}")
    print(f"  EXPERIMENT DIAGNOSTIC REPORT")
    print(f"{'='*50}")

    srm = check_sample_ratio_mismatch(n_control, n_treatment)

    # Simulate early vs late data for novelty check
    mid = len(treatment_data) // 2
    novelty = check_novelty_effect(treatment_data[:mid], treatment_data[mid:])

    # Simulate p-values over time for peeking check
    simulated_p_values = [0.03, 0.06, 0.04, 0.07, 0.08, 0.05, 0.06, 0.07]
    peeking = check_peeking(simulated_p_values)

    print(f"\n{'='*50}")
    print(f"  SUMMARY")
    print(f"{'='*50}")
    print(f"  SRM Issue:       {'⚠️ Yes' if srm else '✅ No'}")
    print(f"  Novelty Effect:  {'⚠️ Yes' if novelty else '✅ No'}")
    print(f"  Peeking Risk:    {'⚠️ Yes' if peeking else '✅ No'}")

    overall = "⚠️ Issues detected — interpret results carefully" if any([srm, novelty, peeking]) else "✅ Experiment looks clean!"
    print(f"  Overall:         {overall}")
    print(f"{'='*50}")

    return {"srm": srm, "novelty": novelty, "peeking": peeking}


if __name__ == "__main__":
    from simulator import simulate_ab_test

    _, control, treatment = simulate_ab_test(metric_type="continuous")

    # Run full diagnostic
    full_diagnostic_report(
        n_control=len(control),
        n_treatment=len(treatment),
        treatment_data=treatment
    )

    # Test SRM with a bad split
    print("\n--- Testing SRM with bad split ---")
    check_sample_ratio_mismatch(n_control=6000, n_treatment=4000)