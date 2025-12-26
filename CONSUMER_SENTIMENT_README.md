# Consumer Sentiment Data Refresh

This directory contains scripts to update the consumer sentiment data from the University of Michigan Surveys of Consumers.

## Files

- **`update_consumer_sentiment.py`** - Python script that fetches data from UMich and updates the HTML file
- **`refresh_consumer_sentiment.command`** - Double-clickable Mac command to run the update and push to GitHub

## Usage

### Option 1: Double-click (Mac)
Simply double-click `refresh_consumer_sentiment.command` to:
1. Fetch the latest consumer sentiment data from UMich
2. Update `consumer_sentiment.html` with the new data
3. Update the timestamp on `index.html`
4. Commit and push changes to GitHub

### Option 2: Command Line
```bash
cd /path/to/financial_dashboard_dist
python3 update_consumer_sentiment.py
```

### Option 3: Automated Monthly Updates
Set up a cron job to run on the first day of each month:
```bash
# Edit crontab
crontab -e

# Add this line to run on the 1st of each month at 9 AM
0 9 1 * * cd /Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist && ./refresh_consumer_sentiment.command
```

## What It Does

The script:
1. Fetches the latest consumer sentiment data from University of Michigan (https://www.sca.isr.umich.edu/files/tbmics.csv)
2. Parses the CSV data and formats it for the dashboard
3. Updates `consumer_sentiment.html` with:
   - Complete historical dataset (all available data from UMich)
   - Current reading summary
   - Last updated timestamp
4. Updates the "Last Updated" date on the main `index.html` dashboard

## Data Source

- **Source**: University of Michigan Surveys of Consumers
- **URL**: https://www.sca.isr.umich.edu/files/tbmics.csv
- **Frequency**: Monthly (typically released mid-month)
- **Historical Coverage**: The script maintains complete historical data going back to 1978

## After Running

After the script completes:
1. The changes are automatically committed to git
2. The changes are automatically pushed to GitHub
3. GitHub Pages will deploy the updated dashboard within 1-2 minutes

## Features

The dashboard now includes:
- **Complete historical data** from 1978 to present (576+ data points)
- **Multiple time periods**: 3M, 6M, 1Y, 3Y, 5Y, 10Y, and All
- **Color-coded zones**:
  - Red: Below 70 (low sentiment)
  - Yellow: 70-80 (neutral)
  - Green: 80+ (high sentiment)
- **Interactive chart** with hover tooltips
- **Data table** with MoM and YoY changes

## Troubleshooting

**"Error fetching data"**:
- Check your internet connection
- Verify the UMich data URL is still accessible
- The script will not update the HTML if data fetch fails

**"Could not find Consumer Sentiment timestamp in index.html"**:
- This is a warning, not an error
- The consumer_sentiment.html file will still be updated
- Only the index.html timestamp update failed
