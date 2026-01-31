import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Guessing the URL pattern based on previous knowledge
# "december-2025-manufacturing-pmi" and "november-2025-manufacturing-pmi"
TARGET_URLS = [
    "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/december-2025-manufacturing-pmi/",
    "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/november-2025-manufacturing-pmi/",
    "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/december-2025-services-pmi/"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.ismworld.org/'
}

for url in TARGET_URLS:
    print(f"\nFetching {url}...")
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if "captcha" in response.text.lower():
            print("⚠ BLOCKED BY CAPTCHA")
        else:
            print("✓ Seems valid (or at least not captcha form)")
            print(response.text[:500])
            
    except Exception as e:
        print(f"Error: {e}")
