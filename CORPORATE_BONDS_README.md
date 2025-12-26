# Corporate Bonds Data Refresh

This directory contains scripts to update the corporate bond yield data from the Federal Reserve Economic Data (FRED) API.

## Setup

1. **Get a FRED API Key** (free):
   - Visit: https://fred.stlouisfed.org/docs/api/api_key.html
   - Sign up for a free account
   - Request an API key

2. **Configure the Script**:
   - Open `update_corporate_bonds.py`
   - Replace `YOUR_FRED_API_KEY_HERE` with your actual FRED API key

## Usage

### Option 1: Double-click (Mac)
Simply double-click `refresh_corporate_bonds.command` to run the update.

### Option 2: Command Line
```bash
cd /path/to/financial_dashboard_dist
python3 update_corporate_bonds.py
```

### Option 3: Automated Daily Updates
Set up a cron job to run daily:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 6 PM
0 18 * * * cd /Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist && python3 update_corporate_bonds.py
```

## What It Does

The script:
1. Fetches the latest corporate bond yield data from FRED for:
   - **AAA** Corporate Bonds (BAMLC0A1CAAAEY)
   - **BBB** Corporate Bonds (BAMLC0A4CBBBEY)
   - **CCC & Lower** High Yield Bonds (BAMLH0A3HYCEY)

2. Updates `corporate_bonds.html` with the new data

3. Updates the deployment version timestamp

## After Running

After updating the data:
1. Test locally by opening `corporate_bonds.html` in your browser
2. Commit and push to GitHub:
   ```bash
   git add corporate_bonds.html
   git commit -m "Update corporate bonds data - $(date +%Y-%m-%d)"
   git push origin main
   ```

3. GitHub Pages will automatically deploy the updated dashboard

## Data Sources

- **FRED Series Documentation**: https://fred.stlouisfed.org/
- **AAA Bonds**: ICE BofA AAA US Corporate Index Effective Yield
- **BBB Bonds**: ICE BofA BBB US Corporate Index Effective Yield
- **CCC Bonds**: ICE BofA CCC & Lower US High Yield Index Effective Yield

## Troubleshooting

**"FRED API key not set" error**:
- Make sure you've replaced `YOUR_FRED_API_KEY_HERE` in `update_corporate_bonds.py`

**"Error fetching data from FRED"**:
- Check your internet connection
- Verify your API key is valid
- Check if you've exceeded the API rate limit (120 requests/minute)

**"corporate_bonds.html not found"**:
- Make sure you're running the script from the `financial_dashboard_dist` directory
