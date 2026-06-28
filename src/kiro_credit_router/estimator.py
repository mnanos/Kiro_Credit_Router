from __future__ import annotations
from .models import Policy

def estimate_credits(*, input_tokens: int, output_tokens: int, profile: str, policy: Policy, tool_calls: int = 0, rag_chunks: int = 0, overhead_factor: float | None = None) -> float:
    estimator = policy.estimator
    model_profile = policy.model_profiles.get(profile) or policy.model_profiles.get("medium")
    if model_profile is None:
        raise ValueError("No model profile found")
    if profile == "local":
        return 0.0
    dynamic_overhead = overhead_factor if overhead_factor is not None else estimator.default_overhead_factor * (1 + 0.03 * tool_calls + 0.01 * rag_chunks)
    raw = (input_tokens / estimator.input_tokens_per_credit) * model_profile.input_weight + (output_tokens / estimator.output_tokens_per_credit) * model_profile.output_weight
    credits = raw * dynamic_overhead * model_profile.complexity_multiplier * (1 - estimator.prompt_cache_discount)
    return round(max(estimator.minimum_credits_per_request, credits), 4)
