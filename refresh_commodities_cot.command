#!/bin/bash
# Comprehensive Commodities & COT Refresh
cd "$(dirname "$0")"
python3 refresh_all_commodities.py
read -p "Press enter to close..."
