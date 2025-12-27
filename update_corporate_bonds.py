#!/usr/bin/env python3
"""
Update Corporate Bonds data from FRED Website (CSV)
Fetches AAA, BBB, and CCC corporate bond yield data via direct CSV download and updates corporate_bonds.html
"""

import requests
import json
from datetime import datetime
import re
import os
import csv
import io

# FRED Series IDs for corporate bond yields
SERIES_IDS = {
    'aaa': 'BAMLC0A1CAAAEY',  # ICE BofA AAA US Corporate Index Effective Yield
    'bbb': 'BAMLC0A4CBBBEY',  # ICE BofA BBB US Corporate Index Effective Yield  
    'ccc': 'BAMLH0A3HYCEY'    # ICE BofA CCC & Lower US High Yield Index Effective Yield
}

def fetch_fred_data(series_id):
    """Fetch data from FRED Website (CSV) for a given series"""
    # Direct CSV download URL
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    
    print(f"  Fetching CSV from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Parse CSV content
    formatted_data = []
    
    # Use io.StringIO to treat the string as a file for the csv module
    csv_file = io.StringIO(response.text)
    reader = csv.reader(csv_file)
    
    # Skip header
    next(reader, None)
    
    for row in reader:
        if len(row) >= 2:
            date_str = row[0]
            val_str = row[1]
            
            # Skip invalid or missing values
            if val_str == '.' or not val_str.strip():
                continue
                
            try:
                val = float(val_str)
                formatted_data.append({
                    'date': date_str,
                    'value': val
                })
            except ValueError:
                continue
    
    return formatted_data

def update_html_file(aaa_data, bbb_data, ccc_data):
    """Update the corporate_bonds.html file with new data"""
    html_file = 'corporate_bonds.html'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False
    
    # Read the current HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert data to JavaScript format
    aaa_js = json.dumps(aaa_data, separators=(',', ': '))
    bbb_js = json.dumps(bbb_data, separators=(',', ': '))
    ccc_js = json.dumps(ccc_data, separators=(',', ': '))
    
    # Update AAA data
    content = re.sub(
        r'const aaaFullData = \[.*?\];',
        f'const aaaFullData = {aaa_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update BBB data
    content = re.sub(
        r'const bbbFullData = \[.*?\];',
        f'const bbbFullData = {bbb_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update CCC data
    content = re.sub(
        r'const cccFullData = \[.*?\];',
        f'const cccFullData = {ccc_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update the deployment version timestamp
    today = datetime.now().strftime('%Y-%m-%d-%H%M')
    content = re.sub(
        r'<meta name="deployment-version" content="auto-updated-.*?">',
        f'<meta name="deployment-version" content="auto-updated-{today}">',
        content
    )
    
    # Write the updated content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function to update corporate bonds data"""
    print("Fetching corporate bond yield data from FRED...")
    
    try:
        # Fetch data for all three series
        print("Fetching AAA data...")
        aaa_data = fetch_fred_data(SERIES_IDS['aaa'])
        print(f"  ✓ Got {len(aaa_data)} AAA observations")
        
        print("Fetching BBB data...")
        bbb_data = fetch_fred_data(SERIES_IDS['bbb'])
        print(f"  ✓ Got {len(bbb_data)} BBB observations")
        
        print("Fetching CCC data...")
        ccc_data = fetch_fred_data(SERIES_IDS['ccc'])
        print(f"  ✓ Got {len(ccc_data)} CCC observations")
        
        # Update the HTML file (only if we got data)
        if aaa_data and bbb_data and ccc_data:
            print("\nUpdating corporate_bonds.html...")
            if update_html_file(aaa_data, bbb_data, ccc_data):
                print("✓ Successfully updated corporate_bonds.html")
                print(f"\nLatest data points:")
                print(f"  AAA: {aaa_data[-1]['value']}% on {aaa_data[-1]['date']}")
                print(f"  BBB: {bbb_data[-1]['value']}% on {bbb_data[-1]['date']}")
                print(f"  CCC: {ccc_data[-1]['value']}% on {ccc_data[-1]['date']}")
            else:
                print("✗ Failed to update HTML file")
        else:
            print("✗ Failed to fetch complete data for all series.")
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error fetching data from FRED: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
