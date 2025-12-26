#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  DAILY DASHBOARD UPDATE (Yields Only)"
echo "==========================================="

# 1. Run Python Update Script
echo ">> Running update_yields.py..."
python3 update_yields.py

# 1b. Update Executive Summary
echo ">> Updating Executive Summary..."
python3 update_executive_summary.py

# 2. Git Commit and Push
echo ">> Pushing updates to GitHub..."
git add .
git commit -m "Daily yield update: $(date)"
git push

echo "==========================================="
echo "  SUCCESS! Dashboard updated."
echo "==========================================="
echo "Closing in 5 seconds..."
sleep 5
