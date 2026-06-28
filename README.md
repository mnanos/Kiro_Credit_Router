# Kiro Credit Router Project

Kiro Credit Router is a Python CLI for choosing the most cost-effective path for AI-assisted development tasks when Kiro credits are limited.

It estimates credit usage from token counts, task complexity, model profile, tool calls, and RAG chunks, then recommends one of three routes:

- `local`: use local tools or a local LLM path.
- `kiro`: use the Kiro CLI path for high-value reasoning work.
- `hybrid`: prepare and validate locally, but use Kiro for the reasoning step.

The goal is to reserve premium Kiro usage for tasks where it is most useful while keeping simple or sensitive work local.

## How It Works

The CLI entrypoint is `ai-dev`, defined in `src/kiro_credit_router/cli.py`.

A routing request flows through these modules:

1. `config.py` loads `.ai-dev/policy.yaml` and `.ai-dev/budget.yaml`.
2. `classifier.py` classifies the task type, complexity, and data sensitivity from the task text.
3. `router.py` applies routing policy, budget thresholds, and sensitivity rules.
4. `estimator.py` estimates credit usage for non-local routes.
5. `cli.py` prints the final decision with Rich tables.

Sensitive data is handled conservatively. If a task mentions secrets, tokens, passwords, API keys, credentials, or private keys, the selected route is forced to `local` even when another route was requested.

## Project Layout

```text
.ai-dev/
  budget.yaml          Current estimated Kiro budget state
  policy.yaml          Routing, credit, model profile, and data policy settings
src/kiro_credit_router/
  classifier.py        Keyword-based task, complexity, and sensitivity detection
  cli.py               Typer CLI commands
  config.py            YAML loading and default policy values
  estimator.py         Credit estimation formula
  models.py            Pydantic models and enums
  router.py            Route selection logic
tests/
  test_estimator.py    Credit estimate tests
  test_router.py       Routing behavior tests
```

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or use the helper script:

```bash
bash create_venv_and_install.sh
```

## Usage

Show available commands:

```bash
ai-dev --help
```

Show the current budget:

```bash
ai-dev budget
```

Show the active routing policy:

```bash
ai-dev policy
```

Estimate credits for a task profile:

```bash
ai-dev estimate --input-tokens 45000 --output-tokens 7000 --profile strong
```

Route a simple explanation task:

```bash
ai-dev route "Explain this legacy C function" --input-tokens 12000 --output-tokens 1800
```

Route a migration review:

```bash
ai-dev route "Review migration risk for spi_clock_config" --input-tokens 45000 --output-tokens 7000 --profile strong
```

Route a complex implementation task with explicit metadata:

```bash
ai-dev route "Implement this complex spec" --task-type spec_implementation --complexity high --input-tokens 90000 --output-tokens 12000
```

By default, route commands are dry runs. They print the selected route and estimated cost, but do not execute local LLM or Kiro commands.

## Routing Rules

The default policy favors local execution for low-cost tasks:

- `explain_code`
- `search_codebase`
- `summarize_log`
- `test_plan`
- `documentation`
- `patch_validation`

Hybrid routing is preferred for tasks that benefit from local preparation plus stronger reasoning:

- `impact_analysis`
- `migration_review`
- `security_review`
- `spec_implementation`

Kiro is preferred for high-value complex refactors when budget is healthy:

- `complex_refactor`

Budget thresholds can downgrade non-local routes. When remaining credits are low, the router warns, prefers hybrid, or recommends local execution.

## Credit Formula

```text
Estimated Credits =
MAX(
  MinimumCreditsPerRequest,
  (
    ((InputTokens / InputTokensPerCredit) * InputWeight) +
    ((OutputTokens / OutputTokensPerCredit) * OutputWeight)
  ) * OverheadFactor * ComplexityMultiplier * (1 - PromptCacheDiscount)
)
```

The overhead factor increases with tool calls and RAG chunks. The `local` profile always costs `0.0` credits.

## Configuration

Tune routing behavior in `.ai-dev/policy.yaml`.

Important sections:

- `credits`: monthly limit, reserve amount, warning threshold, and block threshold.
- `estimator`: token-per-credit ratios, overhead factor, cache discount, and minimum request cost.
- `model_profiles`: profile-specific input/output weights and complexity multipliers.
- `task_routing`: task groups for local, hybrid, and Kiro-preferred routing.
- `data_policy`: sensitivity-related policy switches.

Update `.ai-dev/budget.yaml` as credit usage changes:

```yaml
monthly_limit: 1000
estimated_used: 0
reserved_for_high_value_tasks: 300
warn_below_remaining: 150
block_below_remaining: 50
```

## Tests

Run the test suite from the project root:

```bash
.venv/bin/pytest
```

Current coverage checks the estimator and core routing behavior, including the rule that restricted data is forced to the local route.
