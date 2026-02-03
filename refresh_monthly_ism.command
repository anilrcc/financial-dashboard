#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "==========================================="
echo "  MONTHLY ISM UPDATE"
echo "==========================================="

# 1. Run Python Update Script (Browser-based with fallback)
echo ">> Running ISM update..."

# Try browser-based update first
if python3 -c "import playwright" 2>/dev/null; then
    echo "   Using browser automation (Playwright)"
    python3 update_ism_browser.py
    UPDATE_STATUS=$?
else
    echo "   Playwright not available, using standard HTTP method"
    echo "   (To enable browser automation, run: bash setup_ism_automation.sh)"
    python3 update_ism.py
    UPDATE_STATUS=$?
fi

if [ $UPDATE_STATUS -ne 0 ]; then
    echo "⚠️  Update failed. You may need to run the manual update script."
    echo "   python3 manual_update_january_2026.py"
fi

# 2. Regenerate Key Insights
echo ">> Regenerating Key Insights..."
python3 generate_key_insights.py



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
