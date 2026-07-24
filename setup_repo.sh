#!/usr/bin/env bash
set -euo pipefail

# Lightweight repo setup for development and paper trading (safe defaults).
# - Creates a Python venv in .venv
# - Installs requirements.txt into the venv if present
# - Writes a .env.example with Alpaca PAPER keys placeholders
# Usage: ./setup_repo.sh

REPO_URL="https://github.com/chrisumoh/daytrade_options.git"
VENV_DIR=".venv"
PYTHON=${PYTHON:-python3}

echo "Setting up repository: $REPO_URL"

# Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR using $PYTHON"
  $PYTHON -m venv "$VENV_DIR"
else
  echo "Virtual environment $VENV_DIR already exists"
fi

# Ensure pip is up to date and install requirements if available
if [ -x "$VENV_DIR/bin/pip" ]; then
  echo "Upgrading pip and installing requirements (if present)"
  "$VENV_DIR/bin/pip" install --upgrade pip
  if [ -f requirements.txt ]; then
    "$VENV_DIR/bin/pip" install -r requirements.txt
  else
    echo "requirements.txt not found, skipping pip install"
  fi
else
  echo "Warning: $VENV_DIR/bin/pip not found — activate your Python environment manually and run 'pip install -r requirements.txt'"
fi

# Create .env.example for users to copy into .env
if [ ! -f .env.example ]; then
  cat > .env.example <<EOF
# Copy this file to .env and fill in your Alpaca paper-trading keys
# Get free paper keys at: https://app.alpaca.markets (Paper Trading tab)
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
# Set to False only after you've reviewed config.py and are ready to trade live
ALPACA_PAPER=True
EOF
  echo "Wrote .env.example"
else
  echo ".env.example already exists"
fi

cat <<EOF
Setup complete.

Next steps:
  1) Activate the venv: source $VENV_DIR/bin/activate
  2) Copy .env.example to .env and fill in ALPACA_API_KEY and ALPACA_SECRET_KEY
  3) Run scans: python main.py
  4) To place paper trades (requires keys): python main.py --trade

Notes:
  - This script does not modify config.py. ALPACA_PAPER in config.py must remain True until you review the code and are ready for live trading.
  - If you want the script to be executable locally after cloning, run: chmod +x setup_repo.sh
EOF
