
import requests
import re
from update_ism import fetch_url, parse_ism_list, clean_name, BASE_URL, LANDING_URL

def debug_fetch(month_name):
    print(f"--- Debugging {month_name} ---")
    month_slug = month_name.split()[0].lower()
    
    landing_html = fetch_url(LANDING_URL)
    if not landing_html: return

    link_pattern = re.compile(r'href="([^"]*?/pmi/' + month_slug + r'/?)"', re.IGNORECASE)
    match = link_pattern.search(landing_html)
    
    if not match: return

    report_url = match.group(1)
    if not report_url.startswith("http"):
        report_url = BASE_URL + report_url
    
    text = fetch_url(report_url)
    if not text: return

    # --- New Orders Section ---
    print("\n[New Orders Analysis]")
    
    # 1. Regex used in production
    no_growth_re = re.search(r"industries that reported growth in new orders in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_growth_re:
        print(f"✅ Growth Match: {no_growth_re.group(1)[:50]}...")
    else:
        print("❌ Growth Regex Failed")

    no_decline_re = re.search(r"industries reporting a decrease in new orders in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_decline_re:
        print(f"✅ Decline Match: {no_decline_re.group(1)[:50]}...")
    else:
        print("❌ Decline Regex (Standard) Failed")

    # 2. Dump text around "New Orders" to see actual phrasing
    # Find "New Orders Index" and print next 500 chars
    start_no = text.find("New Orders Index")
    if start_no != -1:
        snippet = text[start_no:start_no+1500]
        # remove html tags for readability
        snippet_clean = re.sub(r'<[^>]+>', ' ', snippet)
        snippet_clean = re.sub(r'\s+', ' ', snippet_clean)
        print(f"\nContext Snippet:\n{snippet_clean}...")
    else:
        print("Could not find 'New Orders Index' section")

if __name__ == "__main__":
    debug_fetch("December 2025")
    print("\n" + "="*50 + "\n")
    debug_fetch("November 2025")
