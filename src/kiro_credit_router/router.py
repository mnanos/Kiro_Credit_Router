from __future__ import annotations
from .classifier import classify_task, estimate_complexity, evaluate_sensitivity
from .estimator import estimate_credits
from .models import Budget, Complexity, Policy, Route, RouteDecision, Sensitivity, TaskType

def default_profile_for_route(route: Route, task_type: TaskType, complexity: Complexity) -> str:
    if route == Route.local: return "local"
    if route == Route.hybrid: return "hybrid-kiro-final"
    if task_type in {TaskType.complex_refactor, TaskType.security_review, TaskType.migration_review}: return "strong"
    if complexity == Complexity.critical: return "premium"
    return "medium"

def select_route(*, task: str, policy: Policy, budget: Budget, forced_route: Route | None = None, task_type: TaskType | None = None, complexity: Complexity | None = None, sensitivity: Sensitivity | None = None, profile: str | None = None, input_tokens: int = 0, output_tokens: int = 0, tool_calls: int = 0, rag_chunks: int = 0) -> RouteDecision:
    tt = task_type or classify_task(task)
    cx = complexity or estimate_complexity(tt, task)
    sens = sensitivity or evaluate_sensitivity(task)
    warnings=[]
    if forced_route:
        route = forced_route
        reason = f"User forced route: {forced_route.value}"
    else:
        route, reason = _select_route_by_policy(tt, cx, sens, budget, policy)
    if sens == Sensitivity.restricted and route != Route.local:
        warnings.append("Restricted data detected; overriding route to local.")
        route = Route.local
        reason = "Restricted data policy requires local execution."
    selected_profile = profile or default_profile_for_route(route, tt, cx)
    credits = estimate_credits(input_tokens=input_tokens, output_tokens=output_tokens, profile=selected_profile, policy=policy, tool_calls=tool_calls, rag_chunks=rag_chunks)
    remaining_before = budget.estimated_remaining
    remaining_after = max(0.0, remaining_before - credits)
    if route != Route.local:
        if remaining_before <= budget.block_below_remaining:
            warnings.append("Kiro budget below block threshold; route should be local unless critical override is approved.")
        elif remaining_before <= budget.warn_below_remaining:
            warnings.append("Kiro budget below warning threshold; reserve Kiro for high-value tasks.")
        elif remaining_after <= budget.reserved_for_high_value_tasks:
            warnings.append("This task uses reserved Kiro credits; consider hybrid/local first.")
    return RouteDecision(task=task, task_type=tt, complexity=cx, sensitivity=sens, selected_route=route, route_reason=reason, profile=selected_profile, input_tokens=input_tokens, output_tokens=output_tokens, estimated_credits=credits, budget_remaining_before=remaining_before, budget_remaining_after=remaining_after, warnings=warnings)

def _select_route_by_policy(task_type: TaskType, complexity: Complexity, sensitivity: Sensitivity, budget: Budget, policy: Policy) -> tuple[Route, str]:
    if sensitivity in {Sensitivity.confidential, Sensitivity.restricted}: return Route.local, "Private/confidential task defaults to local execution."
    local_first=set(policy.task_routing.get("local_first", [])); hybrid=set(policy.task_routing.get("hybrid", [])); kiro=set(policy.task_routing.get("kiro_preferred", []))
    if task_type.value in local_first: return Route.local, f"{task_type.value} is a local-first task."
    if task_type.value in hybrid:
        if budget.estimated_remaining <= budget.block_below_remaining: return Route.local, "Budget below block threshold; using local route."
        return Route.hybrid, f"{task_type.value} benefits from local preparation plus Kiro reasoning."
    if task_type.value in kiro:
        if budget.estimated_remaining <= budget.warn_below_remaining: return Route.hybrid, "Kiro budget is low; using hybrid to reduce credit spend."
        return Route.kiro, f"{task_type.value} may benefit from Kiro premium reasoning."
    if complexity in {Complexity.high, Complexity.critical} and budget.estimated_remaining > budget.warn_below_remaining: return Route.hybrid, "High-complexity unknown task; using hybrid route."
    return Route.local, "Default safe route is local."
