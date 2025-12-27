#!/usr/bin/env python3
"""
Update Money Supply (M2) data from FRED API
Fetches M2 Money Stock and Velocity data and updates money_supply.html
"""

import requests
import json
from datetime import datetime
import re
import os

# FRED API Configuration
FRED_API_KEY = "YOUR_FRED_API_KEY_HERE"  # User needs to get their own key from https://fred.stlouisfed.org/docs/api/api_key.html
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# FRED Series IDs
SERIES_IDS = {
    'm2': 'M2SL',    # M2 Money Stock, Seasonally Adjusted, Billions of Dollars
    'velocity': 'M2V' # Velocity of M2 Money Stock, Ratio
}

def fetch_fred_data(series_id, start_date='1959-01-01'):
    """Fetch data from FRED API for a given series"""
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start_date
    }
    
    response = requests.get(FRED_BASE_URL, params=params)
    response.raise_for_status()
    
    data = response.json()
    observations = data.get('observations', [])
    
    # Convert to our format: [{date: 'YYYY-MM-DD', value: X.XX}, ...]
    formatted_data = []
    for obs in observations:
        if obs['value'] != '.':  # Skip missing values
            formatted_data.append({
                'date': obs['date'],
                'value': float(obs['value'])
            })
    
    return formatted_data

def calculate_yoy_growth(data):
    """Calculate Year-over-Year growth percentage"""
    growth_data = []
    # Create a lookup map for faster access
    date_map = {item['date']: item['value'] for item in data}
    
    for item in data:
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
                
    return growth_data

def update_html_file(m2_data, growth_data, velocity_data):
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
    velocity_js = json.dumps(velocity_data, separators=(',', ': '))
    
    # Update M2 Data
    content = re.sub(
        r'const m2FullData = \[.*?\];',
        f'const m2FullData = {m2_js};',
        content,
        flags=re.DOTALL
    )
    
    # Update Growth Data
    content = re.sub(
        r'const growthFullData = \[.*?\];',
        f'const growthFullData = {growth_js};',
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
    content = re.sub(
        r'<div class="refresh-badge" id="last-updated">Last Updated: .*?</div>',
        f'<div class="refresh-badge" id="last-updated">Last Updated: {display_date}</div>',
        content
    )
    
    # Write the updated content back
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Main function to update money supply data"""
    print("Fetching Money Supply (M2) data from FRED...")
    
    # Check if API key is set
    if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
        print("\n⚠️  ERROR: FRED API key not set!")
        print("Please get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("Then update the FRED_API_KEY variable in this script.\n")
        return
    
    try:
        # Fetch data
        print("Fetching M2SL data...")
        m2_data = fetch_fred_data(SERIES_IDS['m2'])
        print(f"  ✓ Got {len(m2_data)} M2 observations")
        
        print("Calculating YoY Growth...")
        growth_data = calculate_yoy_growth(m2_data)
        print(f"  ✓ Calculated {len(growth_data)} growth points")
        
        # M2 data is in Billions, but for display we might want it in Trillions in the text, 
        # but for charts keeping it raw or consistent is fine. 
        # The HTML converts to Trillions for the KPI display.
        
        print("Fetching M2 Velocity data...")
        velocity_data = fetch_fred_data(SERIES_IDS['velocity'])
        print(f"  ✓ Got {len(velocity_data)} Velocity observations")
        
        # Update the HTML file
        print("\nUpdating money_supply.html...")
        if update_html_file(m2_data, growth_data, velocity_data):
            print("✓ Successfully updated money_supply.html")
            if m2_data:
                print(f"\nLatest data points:")
                print(f"  M2: ${m2_data[-1]['value']/1000:.2f}T on {m2_data[-1]['date']}")
            if growth_data:
                print(f"  Growth: {growth_data[-1]['value']}%")
            if velocity_data:
                print(f"  Velocity: {velocity_data[-1]['value']}")
        else:
            print("✗ Failed to update HTML file")
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error fetching data from FRED: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
