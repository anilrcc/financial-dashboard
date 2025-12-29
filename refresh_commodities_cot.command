#!/bin/bash
# Comprehensive Commodities & COT Refresh
cd "$(dirname "$0")"
python3 refresh_all_commodities.py

echo ""
echo "========================================="
echo "Pushing changes to GitHub..."
echo "========================================="
git add .
git commit -m "Automated commodities refresh - $(date +'%Y-%m-%d %H:%M')"
git push
echo "✓ Pushed to GitHub!"

echo ""
read -p "Press enter to close..."
