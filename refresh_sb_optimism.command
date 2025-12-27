#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  SMALL BUSINESS OPTIMISM UPDATE"
echo "==========================================="

# 1. Run Python Update Script
echo ">> Running update_small_business_optimism.py..."
python3 update_small_business_optimism.py

# 2. Update Executive Summary
echo ">> Updating Executive Summary..."
python3 update_executive_summary.py

# 3. Git Commit and Push
echo ">> Pushing updates to GitHub..."
git add .
git commit -m "Small Business Optimism update: $(date)"
git push

echo "==========================================="
echo "  SUCCESS! Optimism Data updated."
echo "==========================================="
echo "Closing in 5 seconds..."
sleep 5
