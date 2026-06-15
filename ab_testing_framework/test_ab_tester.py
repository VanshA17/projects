import numpy as np
import pytest
from ab_tester import ABTester
from power_analysis import minimum_sample_size, post_hoc_power_check
from simulator import simulate_ab_test

# ── Fixtures ──────────────────────────────────────────────
@pytest.fixture
def continuous_data():
    _, control, treatment = simulate_ab_test(metric_type="continuous")
    return control, treatment

@pytest.fixture
def binary_data():
    _, control, treatment = simulate_ab_test(metric_type="binary")
    return control, treatment

# ── T-Test ────────────────────────────────────────────────
def test_t_test_returns_significant(continuous_data):
    control, treatment = continuous_data
    tester = ABTester(control, treatment)
    result = tester.t_test()
    assert result["significant"] == True
    assert result["p_value"] < 0.05

def test_t_test_structure(continuous_data):
    control, treatment = continuous_data
    tester = ABTester(control, treatment)
    result = tester.t_test()
    assert "t_stat" in result
    assert "p_value" in result
    assert "significant" in result

# ── Z-Test ────────────────────────────────────────────────
def test_z_test_returns_result(binary_data):
    control, treatment = binary_data
    tester = ABTester(control, treatment)
    result = tester.proportion_z_test()
    assert "z_stat" in result
    assert "p_value" in result
    assert isinstance(result["significant"], bool)

# ── Chi-Square ────────────────────────────────────────────
def test_chi_square_returns_result(binary_data):
    control, treatment = binary_data
    tester = ABTester(control, treatment)
    result = tester.chi_square_test(
        control_success=int(control.sum()),
        control_total=len(control),
        treatment_success=int(treatment.sum()),
        treatment_total=len(treatment)
    )
    assert result["chi2"] >= 0
    assert 0 <= result["p_value"] <= 1

# ── Cohen's d ─────────────────────────────────────────────
def test_cohen_d_positive_when_treatment_higher(continuous_data):
    control, treatment = continuous_data
    tester = ABTester(control, treatment)
    d = tester.cohen_d()
    assert d > 0  # treatment mean > control mean

# ── Confidence Interval ───────────────────────────────────
def test_confidence_interval_order(continuous_data):
    control, treatment = continuous_data
    tester = ABTester(control, treatment)
    lower, upper = tester.confidence_interval()
    assert lower < upper

# ── Power Analysis ────────────────────────────────────────
def test_sample_size_increases_with_smaller_effect():
    n_small = minimum_sample_size(effect_size=0.2, power=0.80)
    n_large = minimum_sample_size(effect_size=0.8, power=0.80)
    assert n_small > n_large

def test_sample_size_increases_with_higher_power():
    n_low = minimum_sample_size(effect_size=0.5, power=0.70)
    n_high = minimum_sample_size(effect_size=0.5, power=0.90)
    assert n_high > n_low

# ── Identical Groups ──────────────────────────────────────
def test_identical_groups_not_significant():
    data = np.random.normal(50, 10, 1000)
    tester = ABTester(data, data.copy())
    result = tester.t_test()
    assert result["significant"] == False