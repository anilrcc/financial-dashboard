#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  DAILY DASHBOARD UPDATE (Yields Only)"
echo "==========================================="

# 1. Run Python Update Scripts
echo ">> Running update_yields.py..."
python3 update_yields.py

echo ">> Running update_corporate_bonds.py..."
python3 update_corporate_bonds.py

# 1b. Update Executive Summary
echo ">> Updating Executive Summary..."
python3 update_executive_summary.py

# 2. Git Commit and Push
echo ">> Pushing updates to GitHub..."
git add .
git commit -m "Daily macro data update (Yields & Bonds): $(date)"
git push

echo "==========================================="
echo "  SUCCESS! Dashboard updated."
echo "==========================================="
echo "Closing in 5 seconds..."
sleep 5
