from __future__ import annotations
from .models import Complexity, Sensitivity, TaskType

def classify_task(text: str) -> TaskType:
    q = text.lower()
    if any(x in q for x in ["explain", "what does", "understand function", "describe function"]): return TaskType.explain_code
    if any(x in q for x in ["where is used", "call site", "grep", "symbol", "search"]): return TaskType.search_codebase
    if any(x in q for x in ["build error", "compiler error", "log", "failure", "failed"]): return TaskType.summarize_log
    if "impact" in q: return TaskType.impact_analysis
    if any(x in q for x in ["test plan", "test checklist", "regression"]): return TaskType.test_plan
    if any(x in q for x in ["document", "readme", "release notes"]): return TaskType.documentation
    if any(x in q for x in ["migration", "migrate", "port from", "porting"]): return TaskType.migration_review
    if any(x in q for x in ["security", "vulnerability", "secret", "password", "token"]): return TaskType.security_review
    if any(x in q for x in ["implement spec", "from spec", "sdd", "requirements.md", "tasks.md"]): return TaskType.spec_implementation
    if any(x in q for x in ["refactor", "rewrite module", "large change", "production change"]): return TaskType.complex_refactor
    if any(x in q for x in ["validate patch", "review diff", "check patch"]): return TaskType.patch_validation
    return TaskType.unknown

def estimate_complexity(task_type: TaskType, text: str) -> Complexity:
    q = text.lower()
    if any(x in q for x in ["production", "critical", "security-sensitive", "customer-impacting"]): return Complexity.critical
    if task_type in {TaskType.complex_refactor, TaskType.security_review, TaskType.migration_review, TaskType.spec_implementation}: return Complexity.high
    if task_type in {TaskType.impact_analysis, TaskType.summarize_log, TaskType.patch_validation}: return Complexity.medium
    return Complexity.low

def evaluate_sensitivity(text: str) -> Sensitivity:
    q = text.lower()
    if any(x in q for x in ["password", "api key", "apikey", "secret", "token", "private key", "credential"]): return Sensitivity.restricted
    if any(x in q for x in ["confidential", "customer", "internal-only", "proprietary", "production log"]): return Sensitivity.confidential
    if "internal" in q or "company" in q: return Sensitivity.internal
    return Sensitivity.public
