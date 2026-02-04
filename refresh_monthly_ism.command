#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  MONTHLY ISM UPDATE"
echo "==========================================="

# 1. Run Manufacturing Update
echo ">> Running Manufacturing ISM update..."
if python3 -c "import playwright" 2>/dev/null; then
    python3 update_ism_browser.py
else
    python3 update_ism.py
fi

# 2. Run Services Update
echo ">> Running Services ISM update..."
if python3 -c "import playwright" 2>/dev/null; then
    python3 update_services_ism_browser.py
else
    python3 update_services_ism.py
fi

# 3. Regenerate Key Insights
echo ">> Regenerating Key Insights..."
python3 generate_key_insights.py
python3 generate_services_key_insights.py



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
