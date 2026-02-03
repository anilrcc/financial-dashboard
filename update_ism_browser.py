#!/usr/bin/env python3
"""
Automated ISM Manufacturing PMI Update using Browser Automation
This script uses Playwright to handle the disclaimer modal and extract data
"""

import re
import json
import datetime
import os
import sys

# --- Configuration ---
HEATMAP_FILE = "industry_heatmap.html"
COMMENTS_FILE = "industry_comments.html"
BASE_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/pmi/"

# Industry mapping
INDUSTRY_MAP = {
    "Food, Beverage & Tobacco Products": "Food, Beverage & Tobacco Products",
    "Textile Mills": "Textile Mills",
    "Apparel, Leather & Allied Products": "Apparel, Leather & Allied Products",
    "Wood Products": "Wood Products",
    "Paper Products": "Paper Products",
    "Printing & Related Support Activities": "Printing & Related Support Activities",
    "Petroleum & Coal Products": "Petroleum & Coal Products",
    "Chemical Products": "Chemical Products",
    "Plastics & Rubber Products": "Plastics & Rubber Products",
    "Nonmetallic Mineral Products": "Nonmetallic Mineral Products",
    "Primary Metals": "Primary Metals",
    "Fabricated Metal Products": "Fabricated Metal Products",
    "Machinery": "Machinery",
    "Computer & Electronic Products": "Computer & Electronic Products",
    "Electrical Equipment, Appliances & Components": "Electrical Equipment, Appliances & Comp",
    "Transportation Equipment": "Transportation Equipment",
    "Furniture & Related Products": "Furniture & Related Products",
    "Miscellaneous Manufacturing": "Miscellaneous Manufacturing",
}

def clean_name(name):
    """Normalize industry names"""
    return INDUSTRY_MAP.get(name, name)

def get_last_n_months(n=2):
    """Returns a list of datetime objects for the last n months (most recent first)."""
    dates = []
    today = datetime.date.today()
    curr = today.replace(day=1) - datetime.timedelta(days=1)
    for _ in range(n):
        dates.append(curr)
        curr = curr.replace(day=1) - datetime.timedelta(days=1)
    return dates

def check_playwright():
    """Check if playwright is installed and browsers are available"""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("\n⚠️  Playwright not installed!")
        print("To enable automated browser-based updates, install playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

def fetch_report_with_browser(target_date):
    """Fetch ISM report using browser automation to handle disclaimer"""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("Playwright not available, skipping browser fetch")
        return None
    
    month_name = target_date.strftime("%B %Y")
    month_slug = target_date.strftime("%B").lower()
    url = f"{BASE_URL}{month_slug}/"
    
    print(f"\n🌐 Fetching {month_name} report via browser...")
    print(f"   URL: {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to the report page
            print("   ⏳ Loading page...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait a moment for any modals to appear
            page.wait_for_timeout(2000)
            
            # Try to find and click the disclaimer "Agree" button
            try:
                # Look for button with "Agree" or "Accept" text
                agree_button = page.locator("button:has-text('Agree'), button:has-text('Accept'), a:has-text('Agree'), a:has-text('Accept')").first
                if agree_button.is_visible(timeout=3000):
                    print("   ✓ Found disclaimer, accepting...")
                    agree_button.click()
                    page.wait_for_timeout(1000)
            except:
                # No disclaimer or already accepted
                pass
            
            # Extract the full page text
            print("   ✓ Extracting data...")
            text = page.content()
            
            browser.close()
            
            # Parse the data
            return parse_report_content(text, month_name)
            
    except PlaywrightTimeout:
        print(f"   ✗ Timeout loading {url}")
        return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def parse_report_content(text, month_name):
    """Parse ISM report HTML content"""
    try:
        # Extract Main PMI Industries
        growth_list = []
        contraction_list = []
        
        main_growth_re = re.search(r"industries reporting growth in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if main_growth_re:
            growth_list = parse_ism_list(main_growth_re.group(1))
        
        main_cont_re = re.search(r"industries reporting contraction in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if main_cont_re:
            contraction_list = parse_ism_list(main_cont_re.group(1))
        
        # Extract New Orders Industries
        no_growth_list = []
        no_decline_list = []
        
        no_growth_re = re.search(r"industries that reported growth in new orders in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if no_growth_re:
            no_growth_list = parse_ism_list(no_growth_re.group(1))
        
        no_decline_re = re.search(r"industries reporting a (?:decrease|decline|contraction) in new orders in .*? are:? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if no_decline_re:
            no_decline_list = parse_ism_list(no_decline_re.group(1))
        
        # Extract PMI Indices
        def get_index(label):
            pat = re.compile(f"{label}.*?registered\\s+([\\d\\.]+)\\s+percent", re.IGNORECASE | re.DOTALL)
            m = pat.search(text)
            if m: return float(m.group(1))
            return 0.0
        
        pmi_data = {
            "pmi": get_index("Manufacturing PMI"),
            "newOrders": get_index("New Orders Index"),
            "production": get_index("Production Index"),
            "employment": get_index("Employment Index"),
            "supplierDel": get_index("Supplier Deliveries Index"),
            "inv": get_index("Inventories Index"),
            "custInv": get_index("Customers' Inventories Index"),
            "prices": get_index("Prices Index"),
            "backlog": get_index("Backlog of Orders Index"),
            "export": get_index("New Export Orders Index"),
            "imports": get_index("Imports Index")
        }
        pmi_data["trend"] = "Expansion" if pmi_data["pmi"] > 50 else "Contraction"
        
        # Extract Comments
        comments_list = []
        start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
        
        if start_comments != -1:
            end_comments = text.find("Manufacturing PMI", start_comments)
            if end_comments == -1: end_comments = len(text)
            
            section = text[start_comments:end_comments]
            list_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
            
            for item in list_items[:10]:  # Limit to 10 comments
                clean_item = re.sub(r'<[^>]+>', '', item).strip()
                if ":" in clean_item:
                    parts = clean_item.split(":", 1)
                    ind = clean_name(parts[0].strip())
                    quote = parts[1].strip().strip('"')[:200]  # Limit quote length
                    comments_list.append((ind, quote))
        
        print(f"   ✓ Extracted: PMI={pmi_data['pmi']}, Growth={len(growth_list)}, Contraction={len(contraction_list)}")
        
        return {
            "month_name": month_name,
            "growth": growth_list,
            "contraction": contraction_list,
            "no_growth": no_growth_list,
            "no_decline": no_decline_list,
            "pmi_data": pmi_data,
            "comments": comments_list
        }
        
    except Exception as e:
        print(f"   ✗ Error parsing content: {e}")
        return None

def parse_ism_list(raw_text):
    """Parse ISM industry lists"""
    text = raw_text.replace('\n', ' ').replace('&amp;', '&')
    if ';' in text: 
        tokens = text.split(';')
    else: 
        tokens = text.split(',')
    
    clean_items = []
    for t in tokens:
        t = t.strip()
        if t.lower().startswith('and '): 
            t = t[4:]
        if t.endswith('.'): 
            t = t[:-1]
        if t: 
            clean_items.append(t)
    return clean_items

def update_html_files(all_updates):
    """Update HTML files with new data (reusing logic from manual script)"""
    if not os.path.exists(HEATMAP_FILE):
        print(f"Error: {HEATMAP_FILE} not found")
        return False
    
    with open(HEATMAP_FILE, 'r') as f:
        content = f.read()
    
    # Parse existing months
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match:
        print("Error: Could not find 'months' array")
        return False
    
    current_months = json.loads(months_match.group(1))
    
    # Parse existing data
    data_match = re.search(r'const data = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match:
        print("Error: Could not find 'data' object")
        return False
    
    current_data = {}
    data_block = data_match.group(1)
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        ind = match.group(1)
        arr_str = match.group(2)
        current_data[ind] = json.loads(arr_str)
    
    # Sort updates by date
    sorted_updates = sorted(all_updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y"))
    
    for update in sorted_updates:
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:]
        
        # Check if already exists
        if short_month in current_months:
            print(f"  ℹ  {short_month} already exists, skipping...")
            continue
        
        print(f"  ➕ Adding {short_month}...")
        
        # Add to months
        current_months.append(short_month)
        idx = current_months.index(short_month)
        
        # Calculate ranks
        rank_map = {}
        growth = update['growth']
        contraction = update['contraction']
        
        num_growth = len(growth)
        for i, raw_name in enumerate(growth):
            rank_map[clean_name(raw_name)] = num_growth - i
        
        num_cont = len(contraction)
        for i, raw_name in enumerate(contraction):
            rank_map[clean_name(raw_name)] = -(num_cont - i)
        
        # Update data arrays
        for ind in current_data:
            while len(current_data[ind]) <= idx:
                current_data[ind].append(0)
            
            if ind in rank_map:
                current_data[ind][idx] = rank_map[ind]
            else:
                current_data[ind][idx] = 0
        
        # Update PMI data
        pd = update['pmi_data']
        pmi_obj_str = f'{{ date: "{short_month}", pmi: {pd["pmi"]}, newOrders: {pd["newOrders"]}, production: {pd["production"]}, employment: {pd["employment"]}, supplierDel: {pd["supplierDel"]}, inv: {pd["inv"]}, custInv: {pd["custInv"]}, prices: {pd["prices"]}, backlog: {pd["backlog"]}, export: {pd["export"]}, imports: {pd["imports"]}, trend: "{pd["trend"]}" }}'
        
        content = content.replace("const rawPmiData = [", "const rawPmiData = [\n            " + pmi_obj_str + ",", 1)
        
        # Update ranklists
        no_growth = update['no_growth']
        no_decline = update['no_decline']
        js_growth = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_growth]) + "]"
        js_decline = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_decline]) + "]"
        rank_entry = f'\n            "{short_month}": {{\n                growth: {js_growth},\n                decline: {js_decline}\n            }},'
        
        content = content.replace("const ranklists = {", "const ranklists = {" + rank_entry, 1)
    
    # Write back updated structures
    new_months_js = "const months = " + json.dumps(current_months) + ";"
    content = re.sub(r'const months = \[.*?\];', new_months_js, content, flags=re.DOTALL)
    
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const data = {\n" + ",\n".join(data_lines) + "\n        };"
    content = re.sub(r'const data = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)
    
    content = content.replace(",,", ",")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    if 'name="deployment-version"' in content:
        content = re.sub(r'<meta name="deployment-version" content=".*?">', 
                         f'<meta name="deployment-version" content="auto-browser-{timestamp}">', 
                         content)
    
    with open(HEATMAP_FILE, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Updated {HEATMAP_FILE}")
    
    # Update comments
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, 'r') as f:
            comments_content = f.read()
        
        for update in sorted_updates:
            m_name = update['month_name']
            short_month = m_name[:3] + " " + m_name[-4:]
            comments = update['comments']
            
            if not comments:
                continue
            
            # Check if already exists
            if f"## {short_month}" in comments_content:
                continue
            
            block_lines = [f"## {short_month}"]
            for ind, quote in comments:
                block_lines.append(f'- **{clean_name(ind)}**: "{quote}"')
            new_block_str = "\n".join(block_lines) + "\n"
            
            comments_content = comments_content.replace("const rawComments = `", "const rawComments = `" + new_block_str)
        
        with open(COMMENTS_FILE, 'w') as f:
            f.write(comments_content)
        
        print(f"  ✓ Updated {COMMENTS_FILE}")
    
    return True

def main():
    print("\n" + "="*60)
    print("ISM Manufacturing PMI Automated Browser Update")
    print("="*60 + "\n")
    
    # Check for playwright
    if not check_playwright():
        print("\n💡 Falling back to manual update process...")
        print("   Run: python3 manual_update_january_2026.py")
        return 1
    
    dates = get_last_n_months(2)
    all_updates = {}
    failed_months = []
    
    for d in dates:
        data = fetch_report_with_browser(d)
        if data:
            all_updates[d.strftime("%Y-%m")] = data
            print(f"   ✓ Successfully processed {d.strftime('%B %Y')}\n")
        else:
            failed_months.append(d.strftime('%B %Y'))
            print(f"   ✗ Failed to process {d.strftime('%B %Y')}\n")
    
    if all_updates:
        print(f"\n{'='*60}")
        print(f"Updating HTML files with {len(all_updates)} month(s) of data...")
        print(f"{'='*60}\n")
        
        if update_html_files(all_updates):
            print(f"\n✅ Update Complete!")
        else:
            print(f"\n✗ Update failed")
            return 1
    else:
        print("\n⚠️  WARNING: No data was fetched. HTML files were not updated.")
        return 1
    
    if failed_months:
        print(f"\n⚠️  Failed to fetch data for: {', '.join(failed_months)}")
    
    print(f"\n{'='*60}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
