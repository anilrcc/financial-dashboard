import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LANDING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

print(f"Fetching {LANDING_URL}...")
try:
    response = requests.get(LANDING_URL, headers=headers, verify=False, timeout=30)
    response.raise_for_status()
    print("Success. Extracting links...")
    
    # Find all hrefs
    links = re.findall(r'href="([^"]+)"', response.text)
    
    print("\n--- Links found containing 'pmi' or 'rob' ---")
    relevant_links = [l for l in links if 'pmi' in l.lower() or 'rob' in l.lower()]
    for l in relevant_links:
        print(l)
        
    print("\n--- Links found containing 'december' ---")
    dec_links = [l for l in links if 'december' in l.lower()]
    for l in dec_links:
        print(l)
        
except Exception as e:
    print(f"Error: {e}")
