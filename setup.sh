#!/usr/bin/env bash
# setup.sh - Setup development environment for Kiro Credit Router

set -euo pipefail

echo "========================================"
echo "Setting up Kiro Credit Router Dev Env"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Detected Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "Virtual environment .venv already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install project dependencies
echo "Installing project in editable mode with development dependencies..."
pip install -e ".[dev]"

# Run tests to verify setup
echo "Running test suite to verify installation..."
pytest

echo "========================================"
echo "Setup complete! To start using the tool:"
echo "  1. Activate the environment: source .venv/bin/activate"
echo "  2. Run the CLI: ai-dev --help"
echo "========================================"
