# FRED API Setup for GDP Data Updates

## Getting Your Free FRED API Key

1. **Visit FRED API Key Request Page:**
   https://fred.stlouisfed.org/docs/api/api_key.html

2. **Sign up for a free account** (if you don't have one)

3. **Request an API key** - it's instant and free!

4. **Save your API key** in one of two ways:

   **Option A: Create a `.fred_api_key` file** (Recommended)
   ```bash
   echo "your_api_key_here" > .fred_api_key
   ```

   **Option B: Set environment variable**
   ```bash
   export FRED_API_KEY="your_api_key_here"
   ```

## What Gets Updated

The `update_gdp_data.py` script will:
- Fetch the latest **Real GDP Growth Rate** (% change, quarterly, SAAR)
- Update the macro chart in `industry_heatmap.html`
- Map quarterly data to monthly entries
- Update chart labels and axes to show growth rate instead of GDP level

## Data Source

- **Series:** A191RL1Q225SBEA (Real GDP Percent Change from Preceding Period)
- **Frequency:** Quarterly
- **Units:** Percent Change at Seasonally Adjusted Annual Rate
- **Source:** https://fred.stlouisfed.org/series/A191RL1Q225SBEA

## Running Manually

```bash
python3 update_gdp_data.py
```

## Automatic Updates

The script is integrated into `refresh_monthly_ism.command` and will run automatically when you refresh your ISM Manufacturing data.

**Note:** If no API key is found, the script will skip the GDP update gracefully without breaking the refresh workflow.
