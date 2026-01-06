
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
    if not no_decline_re:
            print("Standard regex failed, trying variant...")
            no_decline_re = re.search(r"industries reporting a decrease in new orders in .*? are:? (.*?)\.", text, re.IGNORECASE | re.DOTALL)

    if no_decline_re:
        print(f"✅ Decline Match: {no_decline_re.group(1)[:100]}...")
        print(f"Full List: {parse_ism_list(no_decline_re.group(1))}")
    else:
        print("❌ Decline Regex (ALL) Failed")

    # Debugging: Look after growth match
    if no_growth_re:
        end_growth = no_growth_re.end()
        print(f"\n--- Text following Growth List (start at {end_growth}) ---")
        print(text[end_growth:end_growth+500])
    
    # Also search for just "industries reporting" to see all variants
    print("\n--- All 'industries reporting' occurrences ---")
    for m in re.finditer(r"industries reporting", text, re.IGNORECASE):
        start = m.start()
        print(f"Match at {start}: {text[start:start+100]}...")

if __name__ == "__main__":
    debug_fetch("December 2025")
    print("\n" + "="*50 + "\n")
    debug_fetch("November 2025")
