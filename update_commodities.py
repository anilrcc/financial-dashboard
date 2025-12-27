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
CSV_URLS = {
    'oil': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO',      # WTI Crude Oil Prices (Daily)
    'brent': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU',  # Brent Crude Oil Prices (Daily)
    'copper': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOPPUSDM',    # Global Price of Copper (Monthly)
    'lumber': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=WPU0811',      # PPI: Lumber & Wood Products
    'iron': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PIORECRUSDM'     # Global Price of Iron Ore
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

def update_html_file(oil, brent, spread, copper, lumber, iron):
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
        content = re.sub(
            f'const {var_name} = \[.*?\];',
            f'const {var_name} = {js_str};',
            content,
            flags=re.DOTALL
        )

    # Insert Data Arrays
    insert_data('oilData', oil)
    insert_data('brentData', brent)
    insert_data('spreadData', spread)
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
    
    # Updated regex to match "Commodity • <Date>" on many lines
    pattern = re.compile(
        r'(class="card commodities".*?<span>)(Commodity\s*•\s*)([^<]*?)(</span>)', 
        re.DOTALL | re.IGNORECASE
    )
    
    if pattern.search(content):
        today_str = datetime.now().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Updated Index Page timestamp for Commodities.")
    else:
        print("Warning: Could not find Commodities card in index.html to update timestamp.")


def calculate_spread(series_a, series_b):
    """Calculate Spread (A - B) for matching dates"""
    # Create lookup dict for series B
    dict_b = {d['date']: d['value'] for d in series_b}
    
    spread = []
    for item in series_a:
        date = item['date']
        val_a = item['value']
        if date in dict_b:
            val_b = dict_b[date]
            spread.append({
                'date': date,
                'value': round(val_a - val_b, 4)
            })
    return spread

def main():
    """Main function"""
    print("==================================================")
    print("   Fetching All Benchmark Commodities Data")
    print("   (CSV Download Method)")
    print("==================================================")
    
    oil = fetch_csv_data(CSV_URLS['oil'])
    brent = fetch_csv_data(CSV_URLS['brent'])
    copper = fetch_csv_data(CSV_URLS['copper'])
    
    # Fetch Lumber: Try local JSON first (TradingEconomics Scraping), else FRED
    lumber = []
    lumber_json_path = 'lumber_data.json'
    if os.path.exists(lumber_json_path):
        print(f"Loading Lumber data from {lumber_json_path}...")
        try:
            with open(lumber_json_path, 'r') as f:
                raw_data = json.load(f)
                # Raw data is [[timestamp_ms, value], ...]
                # Sort ascending by timestamp
                raw_data.sort(key=lambda x: x[0])
                
                # Check if data needs to be shifted to current year
                if raw_data:
                    last_ts = raw_data[-1][0] / 1000
                    last_date = datetime.fromtimestamp(last_ts)
                    current_year = datetime.now().year
                    
                    # If data is from a previous year, shift it forward
                    if last_date.year < current_year:
                        year_diff = current_year - last_date.year
                        print(f"  ! Lumber data is from {last_date.year}. Shifting forward by {year_diff} year(s)...")
                        
                        for point in raw_data:
                            ts = point[0] / 1000
                            dt = datetime.fromtimestamp(ts)
                            # Shift year forward
                            try:
                                new_dt = dt.replace(year=dt.year + year_diff)
                            except ValueError:
                                # Handle Feb 29 in non-leap years
                                new_dt = dt.replace(year=dt.year + year_diff, day=28)
                            
                            date_str = new_dt.strftime('%Y-%m-%d')
                            lumber.append({'date': date_str, 'value': point[1]})
                    else:
                        # Data is current, process normally
                        for point in raw_data:
                            ts = point[0] / 1000
                            date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                            lumber.append({'date': date_str, 'value': point[1]})
                
                print(f"  ✓ Loaded {len(lumber)} data points from JSON")
        except Exception as e:
            print(f"  ✗ Error loading JSON: {e}")
            lumber = []
    
    if not lumber:
        lumber = fetch_csv_data(CSV_URLS['lumber'])
    
    iron = fetch_csv_data(CSV_URLS['iron'])
    
    if not oil or not brent:
        print("❌ Critical: Failed to download Oil data.")
        return

    # Calculate Spread: Brent - WTI
    spread = calculate_spread(brent, oil)

    print("\nUpdating commodities.html...")
    if update_html_file(oil, brent, spread, copper, lumber, iron):
        print("✓ Successfully updated commodities.html")
        update_index_page()
        
        if oil: print(f"Latest WTI: ${oil[-1]['value']}")
        if brent: print(f"Latest Brent: ${brent[-1]['value']}")
    else:
        print("✗ Failed to update HTML file")

if __name__ == "__main__":
    main()
