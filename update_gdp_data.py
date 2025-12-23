#!/usr/bin/env python3
"""
Update GDP Growth Rate data in industry_heatmap.html from FRED API
Fetches the latest quarterly GDP growth rate (% change) and updates the gdpMap in the HTML file
"""

import requests
import re
import os
from datetime import datetime

HEATMAP_FILE = "industry_heatmap.html"
FRED_API_KEY = "YOUR_API_KEY_HERE"  # You'll need to get a free API key from FRED
FRED_GDP_URL = "https://api.stlouisfed.org/fred/series/observations"

def get_fred_api_key():
    """Try to get API key from environment variable or file"""
    # Check environment variable first
    api_key = os.environ.get('FRED_API_KEY')
    
    # If not in environment, try to read from a config file
    if not api_key and os.path.exists('.fred_api_key'):
        with open('.fred_api_key', 'r') as f:
            api_key = f.read().strip()
    
    return api_key


def fetch_gdp_growth_data():
    """Fetch GDP growth rate data from FRED API"""
    api_key = get_fred_api_key()
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("⚠️  FRED API key not found!")
        print("To enable automatic GDP updates:")
        print("1. Get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("2. Save it to .fred_api_key file in this directory, OR")
        print("3. Set FRED_API_KEY environment variable")
        print("\nSkipping GDP update for now...")
        return None
    
    # Use Real GDP Percent Change (Quarterly, SAAR)
    params = {
        'series_id': 'A191RL1Q225SBEA',  # Real GDP % change from preceding period
        'api_key': api_key,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 20  # Get last 20 quarters (5 years)
    }
    
    try:
        print("Fetching GDP growth rate data from FRED...")
        response = requests.get(FRED_GDP_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'observations' not in data:
            print("Error: Unexpected response format from FRED API")
            return None
        
        # Parse the observations
        gdp_data = {}
        for obs in data['observations']:
            date = obs['date']  # Format: YYYY-MM-DD (quarterly, last day of quarter)
            value = obs['value']
            
            if value == '.':  # Missing data
                continue
            
            # Value is already in percent
            gdp_growth = float(value)
            
            # Parse the date to determine quarter
            year, month, day = date.split('-')
            year = int(year)
            month = int(month)
            
            # Determine quarter based on month
            if month in [1, 2, 3]:
                quarter = 'Q1'
            elif month in [4, 5, 6]:
                quarter = 'Q2'
            elif month in [7, 8, 9]:
                quarter = 'Q3'
            else:
                quarter = 'Q4'
            
            gdp_data[f"{quarter} {year}"] = gdp_growth
        
        print(f"✓ Fetched {len(gdp_data)} quarters of GDP growth rate data")
        return gdp_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GDP data: {e}")
        return None


def map_gdp_to_months(gdp_data):
    """Map quarterly GDP growth rate data to monthly entries"""
    if not gdp_data:
        return None
    
    # Create a mapping from month to GDP growth rate
    month_map = {}
    
    # Define quarters
    quarters = {
        'Q1': ['Jan', 'Feb', 'Mar'],
        'Q2': ['Apr', 'May', 'Jun'],
        'Q3': ['Jul', 'Aug', 'Sep'],
        'Q4': ['Oct', 'Nov', 'Dec']
    }
    
    # Map each quarter's value to its months
    for quarter_year, value in gdp_data.items():
        quarter, year = quarter_year.split()
        
        if quarter in quarters:
            for month in quarters[quarter]:
                month_key = f"{month} {year}"
                month_map[month_key] = value
    
    return month_map


def update_gdp_in_html(month_gdp_map):
    """Update the gdpMap in the HTML file and update chart labels"""
    if not month_gdp_map:
        print("No GDP data to update")
        return False
    
    if not os.path.exists(HEATMAP_FILE):
        print(f"Error: {HEATMAP_FILE} not found")
        return False
    
    print(f"Reading {HEATMAP_FILE}...")
    with open(HEATMAP_FILE, 'r') as f:
        content = f.read()
    
    # Find the gdpMap section
    gdp_map_pattern = r'const gdpMap = \{([^}]+)\};'
    match = re.search(gdp_map_pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not find gdpMap in HTML file")
        return False
    
    # Build new gdpMap content
    print("Building updated GDP growth rate map...")
    new_entries = []
    
    # Extract existing months from the HTML to maintain the same structure
    existing_content = match.group(1)
    month_pattern = r'"([^"]+)":\s*(?:null|[\d.\-]+)'
    existing_months = re.findall(month_pattern, existing_content)
    
    # Build new map with updated values
    for month in existing_months:
        if month in month_gdp_map:
            value = month_gdp_map[month]
            new_entries.append(f'"{month}": {value:.2f}')
        else:
            # Keep as null if we don't have data
            new_entries.append(f'"{month}": null')
    
    # Group by quarters for better formatting (3 months per line)
    formatted_lines = []
    for i in range(0, len(new_entries), 3):
        chunk = new_entries[i:i+3]
        if i == 0:
            formatted_lines.append('\n            ' + ', '.join(chunk) + ',')
        else:
            formatted_lines.append('            ' + ', '.join(chunk) + (',' if i + 3 < len(new_entries) else ''))
    
    new_gdp_map = 'const gdpMap = {' + ''.join(formatted_lines) + '\n        };'
    
    # Replace in content
    content = re.sub(gdp_map_pattern, new_gdp_map, content, flags=re.DOTALL)
    
    # Update the comment with latest data info
    current_date = datetime.now().strftime("%Y-%m-%d")
    comment_pattern = r'// Map available GDP Data.*?(?=\n\s*const gdpMap)'
    
    # Get the latest quarter we have data for
    latest_quarters = sorted([k for k in month_gdp_map.keys() if month_gdp_map[k] is not None], 
                            key=lambda x: (x.split()[1], ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x.split()[0])),
                            reverse=True)
    
    if latest_quarters:
        latest = latest_quarters[0]
        new_comment = f'''// Map available GDP Growth Rate Data (Quarterly, % Change SAAR)
        // Source: https://fred.stlouisfed.org/series/A191RL1Q225SBEA
        // Last updated: {current_date}
        // Latest data: {latest}
'''
        content = re.sub(comment_pattern, new_comment, content, flags=re.DOTALL)
    
    # Update chart labels and titles to reflect GDP Growth Rate
    # Update the dataset label
    content = re.sub(
        r'label: [\'"]US Nominal GDP \(\$ Trillions\)[\'"]',
        'label: "Real GDP Growth Rate (% SAAR)"',
        content
    )
    
    # Update the y-axis title
    content = re.sub(
        r'title: \{ display: true, text: [\'"]GDP \(\$ Trillions\)[\'"] \}',
        'title: { display: true, text: "GDP Growth Rate (%)" }',
        content
    )
    
    # Update the chart title
    content = re.sub(
        r'title: \{ display: true, text: [\'"]Macro Context: US GDP Level vs Manufacturing Activity[\'"] \}',
        'title: { display: true, text: "Macro Context: GDP Growth Rate vs Manufacturing PMI" }',
        content
    )
    
    # Update tooltip callback to show percentage
    content = re.sub(
        r'if \(context\.datasetIndex === 0\) return label \+ \'\$\' \+ context\.parsed\.y \+ \'T\';',
        'if (context.datasetIndex === 0) return label + context.parsed.y + "%";',
        content
    )
    
    # Update y-axis scale to be appropriate for percentage values (-10 to 10 range typically)
    content = re.sub(
        r'(y1: \{[^}]*min: )\d+,([^}]*max: )\d+',
        r'\1-5,\2 10',
        content
    )
    
    # Write back
    print("Writing updated file...")
    with open(HEATMAP_FILE, 'w') as f:
        f.write(content)
    
    print("✓ GDP growth rate data updated successfully!")
    return True


def main():
    """Main function"""
    print("=" * 50)
    print("GDP Growth Rate Data Update Script")
    print("=" * 50)
    
    # Fetch GDP growth rate data from FRED
    gdp_data = fetch_gdp_growth_data()
    
    if not gdp_data:
        print("\n⚠️  GDP update skipped (no API key or fetch failed)")
        print("The script will continue without updating GDP data.")
        return True  # Don't fail the whole refresh process
    
    # Map to months
    month_gdp_map = map_gdp_to_months(gdp_data)
    
    # Update HTML
    success = update_gdp_in_html(month_gdp_map)
    
    if success:
        print("\n✓ GDP growth rate data successfully updated in industry_heatmap.html")
    
    return success


if __name__ == "__main__":
    success = main()
    if not success:
        # Don't exit with error code - we don't want to break the refresh workflow
        # if GDP update fails
        print("\nNote: GDP update had issues but continuing...")
        exit(0)
