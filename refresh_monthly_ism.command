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

# 2. Regenerate Key Insights
echo ">> Regenerating Key Insights..."
python3 generate_key_insights.py

# 3. Update GDP Growth Rate Data
echo ">> Updating GDP Growth Rate data..."
python3 update_gdp_data.py

# 3b. Update Executive Summary
echo ">> Updating Executive Summary..."
python3 update_executive_summary.py

# 4. Git Commit and Push
echo ">> Pushing updates to GitHub..."
git add .
git commit -m "Monthly ISM update: $(date)"
git push

echo "==========================================="
echo "  SUCCESS! ISM Data updated."
echo "==========================================="
echo "Closing in 5 seconds..."
sleep 5
