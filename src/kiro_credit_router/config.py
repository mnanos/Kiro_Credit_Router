from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml
from .models import Budget, Policy

DEFAULT_POLICY = Policy(
    model_profiles={
        "local": {"input_weight": 0.0, "output_weight": 0.0, "complexity_multiplier": 0.0},
        "efficient": {"input_weight": 0.7, "output_weight": 0.7, "complexity_multiplier": 0.8},
        "medium": {"input_weight": 1.0, "output_weight": 1.0, "complexity_multiplier": 1.0},
        "strong": {"input_weight": 1.3, "output_weight": 1.3, "complexity_multiplier": 1.3},
        "premium": {"input_weight": 1.8, "output_weight": 1.8, "complexity_multiplier": 1.8},
        "hybrid-kiro-final": {"input_weight": 0.9, "output_weight": 0.9, "complexity_multiplier": 0.9},
    },
    task_routing={
        "local_first": ["explain_code", "search_codebase", "summarize_log", "test_plan", "documentation", "patch_validation"],
        "hybrid": ["impact_analysis", "migration_review", "security_review", "spec_implementation"],
        "kiro_preferred": ["complex_refactor"],
    },
)

def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def _deep_update(dst: dict[str, Any], src: dict[str, Any]) -> None:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _deep_update(dst[key], value)
        else:
            dst[key] = value

def load_policy(project_root: Path | None = None) -> Policy:
    root = project_root or Path.cwd()
    data = _read_yaml(root / ".ai-dev" / "policy.yaml")
    if not data:
        return DEFAULT_POLICY
    merged = DEFAULT_POLICY.model_dump()
    _deep_update(merged, data)
    return Policy.model_validate(merged)

def load_budget(project_root: Path | None = None, policy: Policy | None = None) -> Budget:
    root = project_root or Path.cwd()
    data = _read_yaml(root / ".ai-dev" / "budget.yaml")
    if data:
        return Budget.model_validate(data)
    p = policy or load_policy(root)
    return Budget(monthly_limit=p.credits.monthly_limit, reserved_for_high_value_tasks=p.credits.reserved_for_high_value_tasks, warn_below_remaining=p.credits.warn_below_remaining, block_below_remaining=p.credits.block_below_remaining)
