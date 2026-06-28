from kiro_credit_router.config import DEFAULT_POLICY
from kiro_credit_router.models import Budget, Route, Sensitivity
from kiro_credit_router.router import select_route

def test_explain_code_routes_local():
    d=select_route(task="Explain this legacy C function", policy=DEFAULT_POLICY, budget=Budget(monthly_limit=1000, estimated_used=0), input_tokens=1000, output_tokens=100)
    assert d.selected_route == Route.local

def test_migration_routes_hybrid():
    d=select_route(task="Review migration risk for spi_clock_config", policy=DEFAULT_POLICY, budget=Budget(monthly_limit=1000, estimated_used=0), input_tokens=1000, output_tokens=100)
    assert d.selected_route == Route.hybrid

def test_secret_overrides_to_local():
    d=select_route(task="Review this token and password in the production log", policy=DEFAULT_POLICY, budget=Budget(monthly_limit=1000, estimated_used=0), forced_route=Route.kiro, input_tokens=1000, output_tokens=100)
    assert d.sensitivity == Sensitivity.restricted
    assert d.selected_route == Route.local
