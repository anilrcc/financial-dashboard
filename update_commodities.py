#!/usr/bin/env python3
"""
Hybrid Commodities Update Script
- Uses FRED for historical data (1990-present)
- Uses Trading Economics for latest updates on ALL commodities
- Merges data intelligently, preferring TE for recent dates
"""

import requests
import json
from datetime import datetime, timedelta
import re
import os
import csv
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# FRED Direct CSV URLs
CSV_URLS = {
    'oil': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO',      # WTI Crude Oil
    'brent': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU',  # Brent Crude Oil
    'copper': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOPPUSDM',    # Copper
    'lumber': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=WPU0811',      # Lumber
    'iron': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PIORECRUSDM'     # Iron Ore
}

# Trading Economics URLs
TE_URLS = {
    'oil': 'https://tradingeconomics.com/commodity/crude-oil',
    'brent': 'https://tradingeconomics.com/commodity/brent-crude-oil',
    'copper': 'https://tradingeconomics.com/commodity/copper',
    'lumber': 'https://tradingeconomics.com/commodity/lumber',
    'iron': 'https://tradingeconomics.com/commodity/iron-ore'
}

def fetch_csv_data(url, name):
    """Fetch and parse CSV data from FRED website"""
    print(f"  FRED {name}: ", end='')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        csv_text = response.text
        f = io.StringIO(csv_text)
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        
        formatted_data = []
        for row in reader:
            if len(row) >= 2 and row[1] and row[1] != '.':
                try:
                    val = float(row[1])
                    if row[0] >= '1990-01-01':
                        formatted_data.append({'date': row[0], 'value': val})
                except ValueError:
                    continue
                    
        print(f"{len(formatted_data)} points ✓")
        return formatted_data

    except Exception as e:
        print(f"Error: {e}")
        return []

def fetch_te_commodity(url, name):
    """Fetch latest commodity data from Trading Economics"""
    print(f"  TE {name}: ", end='', flush=True)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for page load
        
        # Extract Highcharts data
        chart_data = driver.execute_script("""
            if (typeof Highcharts !== 'undefined' && Highcharts.charts) {
                for (let chart of Highcharts.charts) {
                    if (chart && chart.series && chart.series[0]) {
                        return chart.series[0].data.map(point => [point.x, point.y]);
                    }
                }
            }
            return null;
        """)
        
        if not chart_data:
            print("No data found")
            return []
        
        # Convert to our format
        formatted_data = []
        for item in chart_data:
            if isinstance(item, list) and len(item) >= 2:
                timestamp, value = item[0], item[1]
                if value is not None:
                    if timestamp > 10000000000:
                        dt = datetime.fromtimestamp(timestamp / 1000)
                    else:
                        dt = datetime.fromtimestamp(timestamp)
                    
                    formatted_data.append({
                        'date': dt.strftime('%Y-%m-%d'),
                        'value': float(value)
                    })
        
        formatted_data.sort(key=lambda x: x['date'])
        
        if formatted_data:
            print(f"{len(formatted_data)} points | Latest: ${formatted_data[-1]['value']:.2f} ✓")
        else:
            print("No valid data")
        
        return formatted_data
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if driver:
            driver.quit()

def merge_data(fred_data, te_data, name):
    """
    Merge FRED historical data with Trading Economics latest data
    TE data takes precedence for overlapping dates
    """
    if not te_data:
        return fred_data
    
    # Create dict from FRED data
    merged = {item['date']: item['value'] for item in fred_data}
    
    # Overlay TE data (overwrites FRED for same dates)
    te_count = 0
    for item in te_data:
        if item['date'] not in merged or merged[item['date']] != item['value']:
            te_count += 1
        merged[item['date']] = item['value']
    
    # Convert back to list and sort
    result = [{'date': k, 'value': v} for k, v in sorted(merged.items())]
    
    if te_count > 0:
        print(f"  → Merged {name}: {len(result)} total ({te_count} from TE)")
    
    return result

def calculate_spread(series_a, series_b):
    """Calculate Spread (A - B) for matching dates"""
    dict_b = {d['date']: d['value'] for d in series_b}
    spread = []
    for item in series_a:
        date = item['date']
        val_a = item['value']
        if date in dict_b:
            spread.append({
                'date': date,
                'value': round(val_a - dict_b[date], 4)
            })
    return spread

def update_html_file(oil, brent, spread, copper, lumber, iron):
    """Update the commodities.html file with new data"""
    html_file = 'commodities.html'
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    def insert_data(var_name, data_list):
        js_str = json.dumps(data_list, separators=(',', ': '))
        nonlocal content
        content = re.sub(
            f'const {var_name} = \\[.*?\\];',
            f'const {var_name} = {js_str};',
            content,
            flags=re.DOTALL
        )

    insert_data('oilData', oil)
    insert_data('brentData', brent)
    insert_data('spreadData', spread)
    insert_data('copperData', copper)
    insert_data('lumberData', lumber)
    insert_data('ironData', iron)
    
    # Update timestamps
    today = datetime.now().strftime('%Y-%m-%d-%H%M')
    content = re.sub(
        r'<meta name="deployment-version" content="auto-updated-.*?">',
        f'<meta name="deployment-version" content="auto-updated-{today}">',
        content
    )
    
    display_date = datetime.now().strftime('%b %d, %Y')
    if 'id="last-updated"' in content:
        content = re.sub(
            r'(id="last-updated">Last Updated:\s*)(.*?)(</div>)',
            f'\\g<1>{display_date}\\g<3>',
            content
        )
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_index_page():
    """Update the date on the main index.html dashboard card"""
    index_file = 'index.html'
    if not os.path.exists(index_file): 
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match commodity cards (Oil, Copper, Lumber, Iron Ore)
    # These cards have dates directly in the card-meta div without "Market Data •" prefix
    pattern = re.compile(
        r'(href="commodities\.html\?view=(?:oil|copper|lumber|iron)".*?<div class="card-meta">.*?<span>)([^<]+)(</span>)', 
        re.DOTALL | re.IGNORECASE
    )
    
    today_str = datetime.now().strftime("%b %d, %Y")
    
    def repl_func(m):
        # Replace the date, keeping the rest of the structure
        return f"{m.group(1)}{today_str}{m.group(3)}"
    
    matches = pattern.findall(content)
    if matches:
        new_content = pattern.sub(repl_func, content)
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ Updated {len(matches)} commodity card timestamp(s) on Index Page")
    else:
        print("⚠ Warning: Could not find commodity cards to update in index.html")

def main():
    """Main function"""
    print("=" * 70)
    print("   Hybrid Commodities Update")
    print("   FRED (Historical) + Trading Economics (Latest)")
    print("=" * 70)
    
    # Step 1: Fetch FRED historical data
    print("\n[1/3] Fetching FRED Historical Data")
    print("-" * 70)
    fred_oil = fetch_csv_data(CSV_URLS['oil'], 'WTI Oil')
    fred_brent = fetch_csv_data(CSV_URLS['brent'], 'Brent Oil')
    fred_copper = fetch_csv_data(CSV_URLS['copper'], 'Copper')
    fred_lumber = fetch_csv_data(CSV_URLS['lumber'], 'Lumber')
    fred_iron = fetch_csv_data(CSV_URLS['iron'], 'Iron Ore')
    
    # Step 2: Fetch Trading Economics latest data
    print("\n[2/3] Fetching Trading Economics Latest Data")
    print("-" * 70)
    te_oil = fetch_te_commodity(TE_URLS['oil'], 'WTI Oil')
    time.sleep(2)  # Brief pause between requests
    te_brent = fetch_te_commodity(TE_URLS['brent'], 'Brent Oil')
    time.sleep(2)
    te_copper = fetch_te_commodity(TE_URLS['copper'], 'Copper')
    time.sleep(2)
    te_lumber = fetch_te_commodity(TE_URLS['lumber'], 'Lumber')
    time.sleep(2)
    te_iron = fetch_te_commodity(TE_URLS['iron'], 'Iron Ore')
    
    # Step 3: Merge data
    print("\n[3/3] Merging Data")
    print("-" * 70)
    oil = merge_data(fred_oil, te_oil, 'WTI')
    brent = merge_data(fred_brent, te_brent, 'Brent')
    copper = merge_data(fred_copper, te_copper, 'Copper')
    lumber = merge_data(fred_lumber, te_lumber, 'Lumber')
    iron = merge_data(fred_iron, te_iron, 'Iron Ore')
    
    if not oil or not brent:
        print("\n❌ Critical: Failed to get oil data")
        return

    # Calculate spread
    spread = calculate_spread(brent, oil)

    # Update HTML files
    print("\n[4/4] Updating HTML Files")
    print("-" * 70)
    if update_html_file(oil, brent, spread, copper, lumber, iron):
        print("✓ Successfully updated commodities.html")
        update_index_page()
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"WTI Oil:    {len(oil):,} points | Latest: ${oil[-1]['value']:.2f}")
        print(f"Brent Oil:  {len(brent):,} points | Latest: ${brent[-1]['value']:.2f}")
        print(f"Copper:     {len(copper):,} points | Latest: ${copper[-1]['value']:.2f}")
        print(f"Lumber:     {len(lumber):,} points | Latest: ${lumber[-1]['value']:.2f}")
        print(f"Iron Ore:   {len(iron):,} points | Latest: ${iron[-1]['value']:.2f}")
        print("=" * 70)
    else:
        print("✗ Failed to update HTML file")

if __name__ == "__main__":
    main()
