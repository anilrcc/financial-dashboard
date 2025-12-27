#!/usr/bin/env python3
"""
Update Cyclical Commodities data from FRED Website (CSV Download)
Fetches WTI Oil, Global Copper, Lumber PPI, and Iron Ore data directly from FRED and updates commodities.html.
No API Key required.
"""

import requests
import json
from datetime import datetime
import re
import os
import csv
import io

# FRED Direct CSV URLs
# Using Global Price Index for Copper/Iron/Oil if available, or Spot Prices
CSV_URLS = {
    'oil': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO',      # WTI Crude Oil Prices (Daily, auto-aggregated by FRED if needed)
    'copper': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOPPUSDM',    # Global Price of Copper (Monthly)
    'lumber': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=WPU0811',      # PPI: Lumber & Wood Products (Monthly) - Proxy for Lumber
    'iron': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PIORECRUSDM'     # Global Price of Iron Ore (Monthly)
}

def fetch_csv_data(url):
    """Fetch and parse CSV data from FRED website"""
    print(f"Downloading data from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse CSV content
        csv_text = response.text
        f = io.StringIO(csv_text)
        reader = csv.reader(f)
        
        # Skip header
        header = next(reader, None)
        
        formatted_data = []
        for row in reader:
            if len(row) >= 2:
                date_str = row[0]
                val_str = row[1]
                
                # Validation
                if val_str and val_str != '.':
                    try:
                        val = float(val_str)
                        # Filter out very old data to keep file size small (e.g. from 2000)
                        if date_str >= '1990-01-01':
                            formatted_data.append({
                                'date': date_str,
                                'value': val
                            })
                    except ValueError:
                        continue
                        
        print(f"  ✓ Parsed {len(formatted_data)} data points")
        return formatted_data

    except Exception as e:
        print(f"  ✗ Error fetching CSV: {e}")
        return []

def update_html_file(oil, copper, lumber, iron):
    """Update the commodities.html file with new data"""
    html_file = 'commodities.html'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False
    
    # Read the current HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Helper to clean/insert data
    def insert_data(var_name, data_list):
        js_str = json.dumps(data_list, separators=(',', ': '))
        nonlocal content
        # Pattern: const oilData = []; or const oilData = [...];
        content = re.sub(
            f'const {var_name} = \[.*?\];',
            f'const {var_name} = {js_str};',
            content,
            flags=re.DOTALL
        )

    # Insert Data Arrays
    insert_data('oilData', oil)
    insert_data('copperData', copper)
    insert_data('lumberData', lumber)
    insert_data('ironData', iron)
    
    # Update the deployment version timestamp
    today = datetime.now().strftime('%Y-%m-%d-%H%M')
    content = re.sub(
        r'<meta name="deployment-version" content="auto-updated-.*?">',
        f'<meta name="deployment-version" content="auto-updated-{today}">',
        content
    )
    
    # Update displayed Last Updated text
    display_date = datetime.now().strftime('%b %d, %Y')
    if 'id="last-updated"' in content:
        content = re.sub(
            r'id="last-updated">Last Updated: .*?</div>',
            f'id="last-updated">Last Updated: {display_date}</div>',
            content
        )
    
    # Write the updated content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_index_page():
    """Update the date on the main index.html dashboard card"""
    index_file = 'index.html'
    if not os.path.exists(index_file): return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find the Commodities card and its date
    # href="commodities.html" ... class="card-meta"><span>Macro Indicator • Dec 23, 2025</span>
    pattern = re.compile(r'(href="commodities.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        today_str = datetime.now().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Updated Index Page timestamp for Commodities.")
    else:
        print("Warning: Could not find Commodities card in index.html to update timestamp.")


def main():
    """Main function"""
    print("==================================================")
    print("   Fetching Commodities Data directly from FRED")
    print("   (CSV Download Method)")
    print("==================================================")
    
    oil = fetch_csv_data(CSV_URLS['oil'])
    copper = fetch_csv_data(CSV_URLS['copper'])
    lumber = fetch_csv_data(CSV_URLS['lumber'])
    iron = fetch_csv_data(CSV_URLS['iron'])
    
    if not oil and not copper:
        print("❌ Critical: Failed to download adequate data.")
        return

    print("\nUpdating commodities.html...")
    if update_html_file(oil, copper, lumber, iron):
        print("✓ Successfully updated commodities.html")
        update_index_page()
        
        if oil: print(f"Latest Oil: ${oil[-1]['value']}")
        if copper: print(f"Latest Copper: ${copper[-1]['value']}")
    else:
        print("✗ Failed to update HTML file")

if __name__ == "__main__":
    main()
