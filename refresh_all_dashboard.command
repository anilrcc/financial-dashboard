#!/bin/bash
# Master Refresh Script for Financial Dashboard
# Runs all data update scripts in sequence and then regenerates the executive summary.

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "========================================="
echo "   Financial Dashboard - Data Refresh    "
echo "========================================="

echo ""
echo "[1/9] Refreshing ISM Manufacturing Data..."
python3 update_ism.py

echo ""
echo "[2/9] Refreshing ISM Services Data..."
python3 update_services_ism.py

echo ""
echo "[3/9] Refreshing Treasury Yields..."
python3 update_yields.py

echo ""
echo "[4/9] Refreshing Corporate Bond Spreads..."
python3 update_corporate_bonds.py

echo ""
echo "[5/9] Refreshing Consumer Sentiment..."
python3 update_consumer_sentiment.py

echo ""
echo "[6/9] Refreshing Building Permits..."
python3 update_building_permits.py

echo ""
echo "[7/9] Refreshing Small Business Optimism..."
python3 update_small_business_optimism.py

echo ""
echo ""
echo "[8/9] Refreshing Money Supply (M2)..."
python3 update_money_supply.py

echo ""
echo ""
echo "[9/11] Refreshing Commodities and COT Reports..."
python3 refresh_all_commodities.py

echo ""
echo "[10/12] Refreshing China PMI Data..."
python3 update_china_data.py

echo ""
echo "[11/12] Refreshing Eurozone PMI Data..."
python3 update_eurozone_data.py

echo ""
echo "[12/12] Regenerating Executive Summary & Index..."
python3 update_executive_summary.py

echo ""
echo "========================================="
echo "        Refresh Complete! 🚀             "
echo "========================================="
echo "Pushing changes to GitHub..."
git add .
git commit -m "Automated dashboard refresh - $(date +'%Y-%m-%d')"
git push
echo "Done!"

echo ""
echo "========================================="
echo "        Refresh Complete! 🚀             "
echo "========================================="
echo "You can now push changes to GitHub."
