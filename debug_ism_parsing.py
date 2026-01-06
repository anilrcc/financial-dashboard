
import requests
import re
from update_ism import fetch_url, parse_ism_list, clean_name, BASE_URL, LANDING_URL

def debug_fetch(month_name):
    print(f"--- Debugging {month_name} ---")
    month_slug = month_name.split()[0].lower()
    
    # Try direct URL construction first as per update_ism.py logic (though update_ism uses landing page finding mostly)
    # Actually update_ism logic:
    # 1. Landing URL
    # 2. Find link
    # 3. Fetch link
    
    landing_html = fetch_url(LANDING_URL)
    if not landing_html:
        print("Failed to fetch landing page")
        return

    link_pattern = re.compile(r'href="([^"]*?/pmi/' + month_slug + r'/?)"', re.IGNORECASE)
    match = link_pattern.search(landing_html)
    
    if not match:
        print(f"Could not find link for {month_slug}")
        return

    report_url = match.group(1)
    if not report_url.startswith("http"):
        report_url = BASE_URL + report_url
    
    print(f"Report URL: {report_url}")
    text = fetch_url(report_url)
    if not text:
        print("Failed to fetch report")
        return

    print(f"Report length: {len(text)}")
    
    # Extract lists
    main_growth_re = re.search(r"industries reporting growth in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_growth_re:
        raw = main_growth_re.group(1)
        print(f"Raw Growth String: {raw[:100]}...")
        growth = parse_ism_list(raw)
        print("Growth List:", growth)
    else:
        print("Growth Regex Failed")

    main_cont_re = re.search(r"industries reporting contraction in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_cont_re:
        raw = main_cont_re.group(1)
        print(f"Raw Contraction String: {raw[:100]}...")
        contraction = parse_ism_list(raw)
        print("Contraction List:", contraction)
    else:
        print("Contraction Regex Failed")

if __name__ == "__main__":
    debug_fetch("December 2025")
    print("\n")
    debug_fetch("November 2025")
