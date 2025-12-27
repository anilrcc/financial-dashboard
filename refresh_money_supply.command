#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "=================================================="
echo "   Refreshing Money Supply (M2) Data"
echo "=================================================="
echo "Date: $(date)"
echo "--------------------------------------------------"

# 2. Run the update script
echo "Running Python update script..."
python3 update_money_supply.py

# 3. Check if update was successful
if [ $? -eq 0 ]; then
    echo "--------------------------------------------------"
    echo "✅ Update script completed successfully."
    
    # Update Executive Summary (Index Page)
    echo "Updating Executive Summary..."
    python3 update_executive_summary.py

    # 4. Git operations
    echo "Staging changes..."
    git add money_supply.html index.html
    
    echo "Committing changes..."
    git commit -m "Auto-update Money Supply data: $(date +'%Y-%m-%d')"
    
    echo "Pushing to GitHub..."
    git push
    
    if [ $? -eq 0 ]; then
        echo "✅ Changes pushed to GitHub successfully."
    else
        echo "⚠️  Git push failed. Please check your connection."
    fi
else
    echo "❌ Python script failed. Please check the errors above."
fi

echo "=================================================="
echo "   Done"
echo "==================================================" 
read -p "Press Enter to close..."
