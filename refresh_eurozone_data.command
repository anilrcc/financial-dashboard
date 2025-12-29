#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "   Eurozone PMI Data Refresh             "
echo "========================================="

echo "Updating Eurozone PMI data..."
python3 update_eurozone_data.py
python3 update_cards_dates.py euro

echo ""
echo "Pushing changes to GitHub..."
git add eurozone_pmi.html index.html
git commit -m "Auto-update Eurozone PMI data - $(date +'%Y-%m-%d')"
git push

echo ""
echo "========================================="
echo "        Update Complete! 🚀              "
echo "========================================="
