from __future__ import annotations
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from .config import load_budget, load_policy
from .estimator import estimate_credits
from .models import Complexity, Route, Sensitivity, TaskType
from .router import select_route

app = typer.Typer(help="AI Dev router for efficient Kiro credit usage.")
console = Console()

@app.command()
def estimate(input_tokens: int = typer.Option(...), output_tokens: int = typer.Option(...), profile: str = typer.Option("medium"), tool_calls: int = 0, rag_chunks: int = 0):
    policy = load_policy(Path.cwd())
    credits = estimate_credits(input_tokens=input_tokens, output_tokens=output_tokens, profile=profile, policy=policy, tool_calls=tool_calls, rag_chunks=rag_chunks)
    console.print(Panel.fit(f"Estimated credits: [bold cyan]{credits:.4f}[/bold cyan]", title="Credit Estimate"))

@app.command()
def route(task: str = typer.Argument(...), forced_route: Optional[Route] = typer.Option(None, "--route"), task_type: Optional[TaskType] = typer.Option(None), complexity: Optional[Complexity] = typer.Option(None), sensitivity: Optional[Sensitivity] = typer.Option(None), profile: Optional[str] = typer.Option(None), input_tokens: int = 0, output_tokens: int = 0, tool_calls: int = 0, rag_chunks: int = 0, dry_run: bool = True):
    policy = load_policy(Path.cwd())
    budget_data = load_budget(Path.cwd(), policy)
    decision = select_route(task=task, policy=policy, budget=budget_data, forced_route=forced_route, task_type=task_type, complexity=complexity, sensitivity=sensitivity, profile=profile, input_tokens=input_tokens, output_tokens=output_tokens, tool_calls=tool_calls, rag_chunks=rag_chunks)
    _print_decision(decision, dry_run=dry_run)

@app.command("budget")
def budget_cmd():
    policy = load_policy(Path.cwd()); b = load_budget(Path.cwd(), policy)
    table = Table(title="Kiro Budget", box=box.SIMPLE_HEAVY); table.add_column("Metric", style="bold"); table.add_column("Value", justify="right")
    table.add_row("Monthly limit", str(b.monthly_limit)); table.add_row("Estimated used", f"{b.estimated_used:.2f}"); table.add_row("Estimated remaining", f"{b.estimated_remaining:.2f}"); table.add_row("Reserved for high-value tasks", str(b.reserved_for_high_value_tasks)); table.add_row("Warning threshold", str(b.warn_below_remaining)); table.add_row("Block threshold", str(b.block_below_remaining))
    console.print(table)

@app.command("policy")
def policy_cmd():
    policy = load_policy(Path.cwd())
    table = Table(title="Routing Policy Summary", box=box.SIMPLE_HEAVY); table.add_column("Area", style="bold"); table.add_column("Value")
    table.add_row("Default route", str(policy.routing.get("default", "local"))); table.add_row("Local-first tasks", ", ".join(policy.task_routing.get("local_first", []))); table.add_row("Hybrid tasks", ", ".join(policy.task_routing.get("hybrid", []))); table.add_row("Kiro-preferred tasks", ", ".join(policy.task_routing.get("kiro_preferred", []))); table.add_row("Profiles", ", ".join(policy.model_profiles.keys()))
    console.print(table)

def _print_decision(decision, dry_run: bool) -> None:
    table = Table(title="AI Dev Routing Decision", box=box.SIMPLE_HEAVY); table.add_column("Field", style="bold"); table.add_column("Value")
    for k,v in [("Task",decision.task),("Task type",decision.task_type.value),("Complexity",decision.complexity.value),("Sensitivity",decision.sensitivity.value),("Selected route",f"[bold cyan]{decision.selected_route.value}[/bold cyan]"),("Reason",decision.route_reason),("Profile",decision.profile),("Input tokens",str(decision.input_tokens)),("Output tokens",str(decision.output_tokens)),("Estimated credits",f"{decision.estimated_credits:.4f}"),("Budget before",f"{decision.budget_remaining_before:.2f}"),("Budget after",f"{decision.budget_remaining_after:.2f}"),("Mode","dry-run" if dry_run else "execute")]: table.add_row(k,v)
    console.print(table)
    for w in decision.warnings: console.print(f"[yellow]Warning:[/yellow] {w}")
    if dry_run: console.print("[dim]Dry-run only: no local LLM or Kiro CLI execution was performed.[/dim]")

if __name__ == "__main__": app()
