from kiro_credit_router.config import DEFAULT_POLICY
from kiro_credit_router.estimator import estimate_credits

def test_local_profile_costs_zero():
    assert estimate_credits(input_tokens=100000, output_tokens=10000, profile="local", policy=DEFAULT_POLICY) == 0.0

def test_medium_profile_estimates_positive_credits():
    assert estimate_credits(input_tokens=100000, output_tokens=10000, profile="medium", policy=DEFAULT_POLICY) > 0

def test_minimum_credit_applies():
    assert estimate_credits(input_tokens=1, output_tokens=1, profile="medium", policy=DEFAULT_POLICY) == DEFAULT_POLICY.estimator.minimum_credits_per_request
