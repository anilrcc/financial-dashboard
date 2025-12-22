#!/bin/bash

# Configuration
REPO_DIR="/Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist"

# Navigate to directory
cd "$REPO_DIR" || exit

# Run the Python update script
echo "Running Services ISM Update Script..."
python3 update_services_ism.py

# Check if python script succeeded
if [ $? -eq 0 ]; then
    echo "Update script finished successfully."
    
    # Git operations
    echo "Staging changes..."
    git add services_pmi.html services_comments.html index.html
    
    echo "Committing changes..."
    DATE=$(date +%Y-%m-%d)
    git commit -m "Auto-refresh Services ISM Data: $DATE"
    
    echo "Pushing to remote..."
    git push
    
    echo "Services PMI Refresh Complete!"
else
    echo "Update script failed. Aborting git operations."
    exit 1
fi
