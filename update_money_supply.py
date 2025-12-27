#!/usr/bin/env python3
"""
Update Money Supply (M2) data from FRED Website (CSV Download)
Fetches M2 Money Stock and Velocity data directly from FRED graphs and updates money_supply.html.
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
# These endpoints allow downloading the graph data as CSV without an API key.
CSV_URLS = {
    'm2': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2SL',    # M2 Money Stock, Seasonally Adjusted
    'velocity': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2V' # Velocity of M2 Money Stock
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

def calculate_yoy_growth(data):
    """Calculate Year-over-Year growth percentage"""
    growth_data = []
    # Create a lookup map for faster access
    date_map = {item['date']: item['value'] for item in data}
    
    for item in data:
        try:
            current_date = datetime.strptime(item['date'], '%Y-%m-%d')
            # Check for the same month in previous year
            prev_year_date = current_date.replace(year=current_date.year - 1).strftime('%Y-%m-%d')
            
            if prev_year_date in date_map:
                prev_val = date_map[prev_year_date]
                curr_val = item['value']
                if prev_val != 0:
                    growth = ((curr_val - prev_val) / prev_val) * 100
                    growth_data.append({
                        'date': item['date'],
                        'value': round(growth, 2)
                    })
        except ValueError:
            continue
                
    return growth_data

def calculate_mom_growth(data):
    """Calculate Month-over-Month growth percentage"""
    growth_data = []
    for i in range(1, len(data)):
        prev_val = data[i-1]['value']
        curr_val = data[i]['value']
        if prev_val != 0:
            growth = ((curr_val - prev_val) / prev_val) * 100
            growth_data.append({
                'date': data[i]['date'],
                'value': round(growth, 2)
            })
    return growth_data

def update_html_file(m2_data, growth_data, mom_data, velocity_data):
    """Update the money_supply.html file with new data"""
    html_file = 'money_supply.html'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False
    
    # Read the current HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert data to JavaScript format
    m2_js = json.dumps(m2_data, separators=(',', ': '))
    growth_js = json.dumps(growth_data, separators=(',', ': '))
    mom_js = json.dumps(mom_data, separators=(',', ': '))
    velocity_js = json.dumps(velocity_data, separators=(',', ': '))
    
    # Update M2 Data
    content = re.sub(
        r'const m2FullData = \[.*?\];',
        f'const m2FullData = {m2_js};',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'const growthFullData = \[.*?\];',
        f'const growthFullData = {growth_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update MoM Data
    content = re.sub(
        r'(const|let) momFullData = \[.*?\];',
        f'let momFullData = {mom_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update Velocity Data
    content = re.sub(
        r'const velocityFullData = \[.*?\];',
        f'const velocityFullData = {velocity_js};',
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
    
    # Update displayed Last Updated text
    display_date = datetime.now().strftime('%b %d, %Y')
    # Simple regex to update separate date badge if it exists
    if 'id="last-updated"' in content:
        content = re.sub(
            r'<div class="refresh-badge" id="last-updated">Last Updated: .*?</div>',
            f'<div class="refresh-badge" id="last-updated">Last Updated: {display_date}</div>',
            content
        )
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_index_page():
    """Update the date on the main index.html dashboard card"""
    index_file = 'index.html'
    if not os.path.exists(index_file): return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find the Money Supply card and its date
    # Pattern: href="money_supply.html" ... class="card-meta"><span>Macro Indicator • Dec 23, 2025</span>
    pattern = re.compile(r'(href="money_supply.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        today_str = datetime.now().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ Updated Index Page timestamp for Money Supply.")
    else:
        print("Warning: Could not find Money Supply card in index.html to update timestamp.")

def main():
    """Main function to update money supply data"""
    print("==================================================")
    print("   Fetching Money Supply (M2) Data directly from FRED")
    print("   (CSV Download Method - No API Key Required)")
    print("==================================================")
    
    m2_data = fetch_csv_data(CSV_URLS['m2'])
    velocity_data = fetch_csv_data(CSV_URLS['velocity'])
    
    if not m2_data:
        print("❌ Critical: Failed to download M2 data. Aborting update.")
        return

    print("Calculating YoY Growth...")
    growth_data = calculate_yoy_growth(m2_data)
    
    print("Calculating MoM Growth...")
    mom_data = calculate_mom_growth(m2_data)
    
    # Filter Velocity to align with M2 dates if needed, or just use as is
    # Velocity is quarterly usually, while M2 is monthly. 
    # The Chart.js adapter handles different frequencies gracefully.
    
    print("\nUpdating money_supply.html...")
    if update_html_file(m2_data, growth_data, mom_data, velocity_data):
        print("✓ Successfully updated money_supply.html")
        
        # Also update the index page card
        update_index_page()
        
        if m2_data:
            latest = m2_data[-1]
            print(f"\nLatest M2 Data: ${latest['value']/1000:.2f}T on {latest['date']}")
        if growth_data:
            print(f"Latest YoY Growth: {growth_data[-1]['value']}%")
    else:
        print("✗ Failed to update HTML file")

if __name__ == "__main__":
    main()
