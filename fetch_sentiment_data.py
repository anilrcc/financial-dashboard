#!/usr/bin/env python3
"""
Fetch University of Michigan Consumer Sentiment Index data from FRED
"""

import requests
import json

# FRED API Configuration
FRED_API_KEY = "YOUR_FRED_API_KEY_HERE"  # User needs to add their key
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
SERIES_ID = "UMCSENT"  # University of Michigan Consumer Sentiment Index

def fetch_sentiment_data():
    """Fetch consumer sentiment data from FRED"""
    params = {
        'series_id': SERIES_ID,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': '1978-01-01'  # Data starts from Jan 1978
    }
    
    response = requests.get(FRED_BASE_URL, params=params)
    response.raise_for_status()
    
    data = response.json()
    observations = data.get('observations', [])
    
    # Convert to our format
    formatted_data = []
    for obs in observations:
        if obs['value'] != '.':  # Skip missing values
            # Convert date from YYYY-MM-DD to "Mon YYYY" format
            date_parts = obs['date'].split('-')
            year = date_parts[0]
            month_num = int(date_parts[1])
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month = month_names[month_num - 1]
            
            formatted_data.append({
                'month': f'{month} {year}',
                'index': float(obs['value'])
            })
    
    return formatted_data

def main():
    """Main function"""
    print("Fetching University of Michigan Consumer Sentiment Index data from FRED...")
    
    # Check if API key is set
    if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
        print("\n⚠️  ERROR: FRED API key not set!")
        print("Please get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("Then update the FRED_API_KEY variable in this script.\n")
        return
    
    try:
        data = fetch_sentiment_data()
        print(f"✓ Fetched {len(data)} observations from {data[0]['month']} to {data[-1]['month']}")
        
        # Save to JSON file
        with open('sentiment_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("✓ Data saved to sentiment_data.json")
        print(f"\nLatest reading: {data[-1]['index']} ({data[-1]['month']})")
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Error fetching data from FRED: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
