#!/usr/bin/env python3
"""
Fetch WTI Crude Oil data from Trading Economics using Selenium
Extracts historical chart data from the JavaScript on the page
Tries to get maximum historical data available
"""

import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def fetch_te_wti_data(timeframe='10y'):
    """
    Fetch WTI data from Trading Economics using Selenium
    
    Args:
        timeframe: '1y', '5y', '10y', or 'max' for different time ranges
    """
    # Trading Economics uses URL parameters for timeframe
    base_url = "https://tradingeconomics.com/commodity/crude-oil"
    
    print(f"Fetching WTI data from Trading Economics (timeframe: {timeframe})...")
    print(f"URL: {base_url}")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        # Initialize the Chrome driver with automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(base_url)
        
        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Try to click the timeframe button to get more historical data
        try:
            print(f"Attempting to select {timeframe} timeframe...")
            # Common selectors for timeframe buttons on Trading Economics
            timeframe_selectors = [
                f"//button[contains(text(), '{timeframe.upper()}')]",
                f"//a[contains(text(), '{timeframe.upper()}')]",
                f"//span[contains(text(), '{timeframe.upper()}')]",
                f"//button[@data-range='{timeframe}']",
            ]
            
            clicked = False
            for selector in timeframe_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    element.click()
                    print(f"✓ Clicked {timeframe} button")
                    time.sleep(3)  # Wait for chart to reload
                    clicked = True
                    break
                except:
                    continue
            
            if not clicked:
                print(f"  Could not find {timeframe} button, using default view")
        except Exception as e:
            print(f"  Could not change timeframe: {e}")
        
        # Get page source
        page_source = driver.page_source
        
        # Look for common patterns where TE stores chart data
        patterns = [
            r'var\s+historicalData\s*=\s*(\[.*?\]);',
            r'data:\s*(\[\[.*?\]\])',
            r'"historical":\s*(\[.*?\])',
            r'series:\s*\[\s*\{\s*data:\s*(\[.*?\])',
        ]
        
        data_found = None
        for pattern in patterns:
            match = re.search(pattern, page_source, re.DOTALL)
            if match:
                try:
                    data_str = match.group(1)
                    # Clean up the data string
                    data_str = re.sub(r'new Date\([^)]+\)', '0', data_str)  # Replace Date objects
                    data_found = json.loads(data_str)
                    print(f"✓ Found data using pattern: {pattern[:30]}...")
                    break
                except:
                    continue
        
        if not data_found:
            # Try to execute JavaScript to get the data
            print("Trying to extract data via JavaScript execution...")
            try:
                # Try to get Highcharts data if available
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
                
                if chart_data:
                    data_found = chart_data
                    print("✓ Extracted data from Highcharts")
            except Exception as e:
                print(f"JavaScript execution failed: {e}")
        
        if not data_found:
            print("❌ Could not find chart data on the page")
            return []
        
        # Convert to our format
        formatted_data = []
        for item in data_found:
            try:
                if isinstance(item, list) and len(item) >= 2:
                    # Format: [timestamp_ms, value]
                    timestamp = item[0]
                    value = item[1]
                    
                    # Convert timestamp to date
                    if timestamp > 10000000000:  # Milliseconds
                        dt = datetime.fromtimestamp(timestamp / 1000)
                    else:  # Seconds
                        dt = datetime.fromtimestamp(timestamp)
                    
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    if value is not None and date_str >= '1990-01-01':
                        formatted_data.append({
                            'date': date_str,
                            'value': float(value)
                        })
                elif isinstance(item, dict):
                    # Format: {x: timestamp, y: value} or {date: ..., value: ...}
                    if 'x' in item and 'y' in item:
                        timestamp = item['x']
                        value = item['y']
                    elif 'date' in item and 'value' in item:
                        date_str = item['date']
                        value = item['value']
                        formatted_data.append({
                            'date': date_str,
                            'value': float(value)
                        })
                        continue
                    else:
                        continue
                    
                    if timestamp > 10000000000:
                        dt = datetime.fromtimestamp(timestamp / 1000)
                    else:
                        dt = datetime.fromtimestamp(timestamp)
                    
                    date_str = dt.strftime('%Y-%m-%d')
                    
                    if value is not None and date_str >= '1990-01-01':
                        formatted_data.append({
                            'date': date_str,
                            'value': float(value)
                        })
            except Exception as e:
                continue
        
        # Sort by date
        formatted_data.sort(key=lambda x: x['date'])
        
        # Remove duplicates (keep last value for each date)
        seen_dates = {}
        for item in formatted_data:
            seen_dates[item['date']] = item['value']
        
        formatted_data = [{'date': k, 'value': v} for k, v in sorted(seen_dates.items())]
        
        print(f"✓ Extracted {len(formatted_data)} unique data points")
        if formatted_data:
            print(f"  Date range: {formatted_data[0]['date']} to {formatted_data[-1]['date']}")
            print(f"  Latest value: ${formatted_data[-1]['value']}")
        
        return formatted_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        if driver:
            driver.quit()

def save_to_json(data, filename='te_wti_data.json'):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved data to {filename}")

if __name__ == "__main__":
    print("=" * 60)
    print("  Trading Economics WTI Crude Oil Data Fetcher")
    print("=" * 60)
    
    # Try to get maximum historical data
    # Try different timeframes to get the most data
    all_data = []
    
    for timeframe in ['max', '10y', '5y']:
        print(f"\n--- Trying timeframe: {timeframe} ---")
        data = fetch_te_wti_data(timeframe)
        
        if data and len(data) > len(all_data):
            all_data = data
            print(f"✓ Got {len(data)} points with {timeframe}")
            
            # If we got data going back to 1990 or earlier, we're good
            if data[0]['date'] <= '1990-01-01':
                print("✓ Got sufficient historical data!")
                break
        
        time.sleep(2)  # Brief pause between attempts
    
    if all_data:
        save_to_json(all_data)
        print(f"\n✓ Success! Saved {len(all_data)} data points")
        print(f"  Coverage: {all_data[0]['date']} to {all_data[-1]['date']}")
    else:
        print("\n❌ Failed to fetch data. Check the output above for errors.")
