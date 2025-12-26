#!/bin/bash
# Master Refresh Script for Financial Dashboard
# Runs all data update scripts in sequence and then regenerates the executive summary.

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "========================================="
echo "   Financial Dashboard - Data Refresh    "
echo "========================================="

echo ""
echo "[1/7] Refreshing ISM Manufacturing Data..."
python3 update_ism.py

echo ""
echo "[2/7] Refreshing ISM Services Data..."
python3 update_services_ism.py

echo ""
echo "[3/7] Refreshing Treasury Yields..."
python3 update_yields.py

echo ""
echo "[4/7] Refreshing Corporate Bond Spreads..."
python3 update_corporate_bonds.py

echo ""
echo "[5/7] Refreshing Consumer Sentiment..."
python3 update_consumer_sentiment.py

echo ""
echo "[6/7] Refreshing Building Permits..."
python3 update_building_permits.py

echo ""
echo "[7/7] Regenerating Executive Summary & Index..."
python3 update_executive_summary.py

echo ""
echo "========================================="
echo "        Refresh Complete! 🚀             "
echo "========================================="
echo "You can now push changes to GitHub."
