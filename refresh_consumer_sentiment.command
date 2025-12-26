#!/bin/bash

# Configuration
PROJECT_DIR="/Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist"

cd "$PROJECT_DIR"

echo "------------------------------------------------"
echo "  Updating Consumer Sentiment Data"
echo "------------------------------------------------"

# Run the python script (fetches data automatically from UMich)
python3 update_consumer_sentiment.py

# Update Executive Summary on Index Page
echo "Updating Executive Summary..."
python3 update_executive_summary.py

# Check if script ran successfully
if [ $? -eq 0 ]; then
    echo "Update script finished successfully."
    
    # Git Operations
    echo "Staging changes..."
    git add consumer_sentiment.html index.html

    echo "Committing..."
    git commit -m "Update Consumer Sentiment data $(date +'%Y-%m-%d')"

    echo "Pushing to GitHub..."
    git push origin main

    echo "Done! Dashboard updated."
else
    echo "Python script encountered an error."
fi

