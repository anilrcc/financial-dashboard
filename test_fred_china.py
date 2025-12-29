
import os
try:
    from fredapi import Fred
    print("fredapi module found")
except ImportError:
    print("fredapi module NOT found")

# Try to find API key
api_key = os.environ.get('FRED_API_KEY')
if not api_key:
    try:
        with open('.fred_api_key', 'r') as f:
            api_key = f.read().strip()
    except:
        pass

if api_key:
    print("Found API Key.")
    try:
        fred = Fred(api_key=api_key)
        # Search for China PMI
        print("Searching for China PMI series...")
        search_results = fred.search('China Manufacturing PMI')
        print(search_results[['id', 'title', 'frequency']].head(10))
        
        print("\nSearching for Caixin China PMI...")
        caixin_results = fred.search('Caixin China Manufacturing PMI')
        print(caixin_results[['id', 'title', 'frequency']].head(10))
        
    except Exception as e:
        print(f"Error querying FRED: {e}")
else:
    print("No API Key found. Skipping FRED check.")
