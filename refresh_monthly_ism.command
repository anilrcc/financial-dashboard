#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  MONTHLY ISM UPDATE"
echo "==========================================="

# 1. Run Python Update Script
echo ">> Running update_ism.py..."
python3 update_ism.py

# 2. Git Commit and Push
echo ">> Pushing updates to GitHub..."
git add .
git commit -m "Monthly ISM update: $(date)"
git push

echo "==========================================="
echo "  SUCCESS! ISM Data updated."
echo "==========================================="
echo "Closing in 5 seconds..."
sleep 5
