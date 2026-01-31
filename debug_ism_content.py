import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LANDING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

print(f"Fetching {LANDING_URL}...")
try:
    response = requests.get(LANDING_URL, headers=headers, verify=False, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("--- Page Preview (First 1000 chars) ---")
    print(response.text[:1000])
    
    print("\n--- Page Preview (Middle) ---")
    print(response.text[5000:6000])

except Exception as e:
    print(f"Error: {e}")
