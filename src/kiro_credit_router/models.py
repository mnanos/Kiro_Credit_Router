from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class Route(str, Enum):
    local = "local"
    kiro = "kiro"
    hybrid = "hybrid"

class TaskType(str, Enum):
    explain_code = "explain_code"
    search_codebase = "search_codebase"
    summarize_log = "summarize_log"
    impact_analysis = "impact_analysis"
    test_plan = "test_plan"
    documentation = "documentation"
    migration_review = "migration_review"
    security_review = "security_review"
    spec_implementation = "spec_implementation"
    complex_refactor = "complex_refactor"
    patch_validation = "patch_validation"
    unknown = "unknown"

class Complexity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Sensitivity(str, Enum):
    public = "public"
    internal = "internal"
    confidential = "confidential"
    restricted = "restricted"

class ModelProfile(BaseModel):
    input_weight: float = 1.0
    output_weight: float = 1.0
    complexity_multiplier: float = 1.0

class EstimatorConfig(BaseModel):
    input_tokens_per_credit: float = 200_000
    output_tokens_per_credit: float = 50_000
    default_overhead_factor: float = 1.20
    prompt_cache_discount: float = 0.0
    minimum_credits_per_request: float = 0.01

class CreditsConfig(BaseModel):
    monthly_limit: int = 1000
    reserved_for_high_value_tasks: int = 300
    warn_below_remaining: int = 150
    block_below_remaining: int = 50

class Policy(BaseModel):
    routing: Dict[str, str] = Field(default_factory=lambda: {"default": "local"})
    credits: CreditsConfig = Field(default_factory=CreditsConfig)
    estimator: EstimatorConfig = Field(default_factory=EstimatorConfig)
    model_profiles: Dict[str, ModelProfile] = Field(default_factory=dict)
    task_routing: Dict[str, List[str]] = Field(default_factory=dict)
    data_policy: Dict[str, object] = Field(default_factory=dict)

class Budget(BaseModel):
    monthly_limit: int = 1000
    estimated_used: float = 0.0
    reserved_for_high_value_tasks: int = 300
    warn_below_remaining: int = 150
    block_below_remaining: int = 50
    @property
    def estimated_remaining(self) -> float:
        return max(0.0, float(self.monthly_limit) - float(self.estimated_used))

class RouteDecision(BaseModel):
    task: str
    task_type: TaskType
    complexity: Complexity
    sensitivity: Sensitivity
    selected_route: Route
    route_reason: str
    profile: str
    input_tokens: int
    output_tokens: int
    estimated_credits: float
    budget_remaining_before: float
    budget_remaining_after: float
    warnings: List[str] = Field(default_factory=list)
