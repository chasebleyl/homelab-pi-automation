#!/usr/bin/env bash
# Wrapper script that activates venv and sources .env before running ansible commands
#
# Usage:
#   ./run-playbook.sh playbooks/site.yml          # Run a playbook
#   ./run-playbook.sh -m ping raspberry_pi        # Ad-hoc command (auto-detects)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$REPO_ROOT/.env"
VENV_DIR="$REPO_ROOT/.venv"

# Activate virtual environment
if [[ -f "$VENV_DIR/bin/activate" ]]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Run: python -m venv .venv && pip install -e '.[dev]'"
    exit 1
fi

# Check ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "Error: ansible not found in venv"
    echo "Run: pip install -e '.[dev]'"
    exit 1
fi

# Source .env if it exists
if [[ -f "$ENV_FILE" ]]; then
    echo "Loading environment from $ENV_FILE"
    set -a  # automatically export all variables
    source "$ENV_FILE"
    set +a
else
    echo "Warning: $ENV_FILE not found. Using defaults."
fi

# Run from the ansible directory
cd "$SCRIPT_DIR"

# Detect if this is an ad-hoc command (-m flag) or a playbook
if [[ "${1:-}" == "-m" ]] || [[ "${1:-}" == "--module-name" ]]; then
    # Ad-hoc command: use ansible
    exec ansible "$@"
else
    # Playbook: use ansible-playbook
    exec ansible-playbook "$@"
fi
