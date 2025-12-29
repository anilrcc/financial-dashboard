#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "   Global PMI Data Refresh               "
echo "========================================="

echo "Updating Global PMI data..."
python3 update_global_pmi.py
python3 update_cards_dates.py global

echo ""
echo "Pushing changes to GitHub..."
git add global_pmi.html index.html
git commit -m "Auto-update Global PMI data - $(date +'%Y-%m-%d')"
git push

echo ""
echo "========================================="
echo "        Update Complete! 🚀              "
echo "========================================="
