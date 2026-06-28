# Kiro Credit Router Project

A venv-based Python CLI project for using a limited Kiro Pro plan efficiently.

The CLI estimates credit usage from input/output tokens and routes developer tasks to:

- `local` — local TUI/local LLM path
- `kiro` — Kiro CLI path
- `hybrid` — local preparation + Kiro reasoning + local validation

## Setup

```bash
cd kiro_credit_router_project
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
ai-dev --help
ai-dev budget
ai-dev policy
ai-dev estimate --input-tokens 45000 --output-tokens 7000 --profile strong
ai-dev route "Explain this legacy C function" --input-tokens 12000 --output-tokens 1800
ai-dev route "Review migration risk for spi_clock_config" --input-tokens 45000 --output-tokens 7000 --profile strong
ai-dev route "Implement this complex spec" --task-type spec_implementation --complexity high --input-tokens 90000 --output-tokens 12000
```

## Test

```bash
pytest
```

## Formula

```text
Estimated Credits =
MAX(
  MinimumCreditsPerRequest,
  (
    ((InputTokens / InputTokensPerCredit) × InputWeight) +
    ((OutputTokens / OutputTokensPerCredit) × OutputWeight)
  ) × OverheadFactor × ComplexityMultiplier × (1 - PromptCacheDiscount)
)
```

Tune `.ai-dev/policy.yaml` using observed Kiro credit usage.
