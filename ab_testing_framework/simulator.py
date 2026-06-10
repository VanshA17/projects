import numpy as np
import pandas as pd

def simulate_ab_test(
    n_control: int = 5000,
    n_treatment: int = 5000,
    control_conversion: float = 0.042,
    treatment_conversion: float = 0.048,
    metric_type: str = "binary",  # "binary" or "continuous"
    seed: int = 42
):
    """
    Simulates A/B experiment data.
    - binary: conversion rate experiment (clicked / didn't click)
    - continuous: revenue per user, time on site, etc.
    """
    np.random.seed(seed)

    if metric_type == "binary":
        control = np.random.binomial(1, control_conversion, n_control)
        treatment = np.random.binomial(1, treatment_conversion, n_treatment)

    elif metric_type == "continuous":
        control = np.random.normal(loc=50, scale=10, size=n_control)
        treatment = np.random.normal(loc=52, scale=10, size=n_treatment)

    # Build dataframe
    df_control = pd.DataFrame({"group": "control", "value": control})
    df_treatment = pd.DataFrame({"group": "treatment", "value": treatment})
    df = pd.concat([df_control, df_treatment], ignore_index=True)

    print(f"\n✅ Simulated A/B Test Data ({metric_type} metric)")
    print(f"Control size: {n_control} | Treatment size: {n_treatment}")
    print(f"Control mean: {control.mean():.4f} | Treatment mean: {treatment.mean():.4f}")
    print(f"\nSample rows:\n{df.sample(6)}")

    return df, control, treatment


if __name__ == "__main__":
    print("--- Binary Metric Test ---")
    df1, c1, t1 = simulate_ab_test(metric_type="binary")

    print("\n--- Continuous Metric Test ---")
    df2, c2, t2 = simulate_ab_test(metric_type="continuous")