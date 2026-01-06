import requests
import re
import datetime
import os
import ssl
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- Configuration ---
HEATMAP_FILE = "industry_heatmap.html"
COMMENTS_FILE = "industry_comments.html"
INDEX_FILE = "index.html"
# ISM Base URLs
BASE_URL = "https://www.ismworld.org"
LANDING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/"

# Mapping ISM Report Names to Our Keys
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
    "Electrical Equip, Appliances & Components": "Electrical Equipment, Appliances & Comp",
    "Transportation Equipment": "Transportation Equipment",
    "Furniture & Related Products": "Furniture & Related Products",
    "Miscellaneous Manufacturing": "Miscellaneous Manufacturing",
    # Abbreviations sometimes used
    "Food, Bev & Tobacco": "Food, Beverage & Tobacco Products",
    "Apparel, Leather & Allied": "Apparel, Leather & Allied Products",
    "Petroleum & Coal": "Petroleum & Coal Products",
    "Plastics & Rubber": "Plastics & Rubber Products",
    "Computer & Electronic": "Computer & Electronic Products",
    "Electrical Equip": "Electrical Equipment, Appliances & Comp",
    "Furniture & Related": "Furniture & Related Products",
    "Misc Mfg": "Miscellaneous Manufacturing"
}

def get_last_n_months(n=6):
    """Returns a list of datetime objects for the last n months (most recent first)."""
    dates = []
    today = datetime.date.today()
    # Start from previous month
    curr = today.replace(day=1) - datetime.timedelta(days=1)
    for _ in range(n):
        dates.append(curr)
        # Go back one month
        curr = curr.replace(day=1) - datetime.timedelta(days=1)
    return dates

def fetch_url(url, max_retries=3):
    """Fetch URL with retry logic and exponential backoff."""
    import time
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Fetching: {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            print(f"✓ Successfully fetched {url}")
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"⚠ Server unavailable (503). Waiting {wait_time}s before retry...")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed to fetch {url} after {max_retries} attempts: {e}")
                    return None
            else:
                print(f"✗ HTTP Error {e.response.status_code}: {e}")
                return None
        except requests.exceptions.Timeout:
            print(f"⚠ Request timeout. Retrying...")
            if attempt == max_retries - 1:
                print(f"✗ Failed to fetch {url}: Timeout after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"✗ Failed to fetch {url}: {e}")
            return None
    
    return None

def fetch_report_data(target_date):
    month_name = target_date.strftime("%B %Y")
    print(f"Targeting Report: {month_name}")
    
    try:
        # 1. Get Landing Page
        landing_html = fetch_url(LANDING_URL)
        if not landing_html: return None
        
        # 2. Find Link to Report
        month_slug = month_name.split()[0].lower() # "november"
        
        # Regex to find link with /pmi/monthname/
        link_pattern = re.compile(r'href="([^"]*?/pmi/' + month_slug + r'/?)"', re.IGNORECASE)
        match = link_pattern.search(landing_html)
        
        if not match:
            print(f"Could not find link for {month_slug} report.")
            return None

        report_url = match.group(1)
        if not report_url.startswith("http"):
            report_url = BASE_URL + report_url
            
        # 3. Fetch Report
        text = fetch_url(report_url)
        if not text: return None
        
        # --- Extract Main PMI Industries ---
        growth_list = []
        contraction_list = []
        
        main_growth_re = re.search(r"industries reporting growth in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if main_growth_re:
            growth_list = parse_ism_list(main_growth_re.group(1))

        main_cont_re = re.search(r"industries reporting contraction in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if main_cont_re:
            contraction_list = parse_ism_list(main_cont_re.group(1))

        # --- Extract New Orders Industries ---
        no_growth_list = []
        no_decline_list = []

        no_growth_re = re.search(r"industries that reported growth in new orders in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if no_growth_re:
            no_growth_list = parse_ism_list(no_growth_re.group(1))

        no_decline_re = re.search(r"industries reporting a decrease in new orders in .*? are: (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        if not no_decline_re:
             # Try variant: "The X industries reporting a decrease in new orders in [Month] are: ..."
             no_decline_re = re.search(r"industries reporting a decrease in new orders in .*? are:? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
        
        if no_decline_re:
            no_decline_list = parse_ism_list(no_decline_re.group(1))
            
        # --- Extract PMI Indices ---
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
        
        # --- Extract Summary ---
        summary_text = ""
        summ_match = re.search(r"(Economic activity in the manufacturing sector.*?)(?=\n|<br>)", text, re.IGNORECASE)
        if summ_match:
            summary_text = summ_match.group(1)
        else:
            summary_text = f"The Manufacturing PMI registered {pmi_data['pmi']} percent in {month_name}."

        # --- Extract Comments ---
        start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
        comments_list = []
        
        if start_comments != -1:
            end_comments = text.find("Manufacturing PMI", start_comments)
            if end_comments == -1: end_comments = len(text)
            
            section = text[start_comments:end_comments]
            list_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
            
            for item in list_items:
                clean_item = re.sub(r'<[^>]+>', '', item).strip()
                if ":" in clean_item:
                    parts = clean_item.split(":", 1)
                    ind = clean_name(parts[0].strip())
                    quote = parts[1].strip().strip('"')
                    comments_list.append((ind, quote))
                elif "(" in clean_item and ")" in clean_item:
                     parts = clean_item.rsplit("(", 1)
                     quote = parts[0].strip().strip('"')
                     ind = clean_name(parts[1].replace(")", "").strip())
                     comments_list.append((ind, quote))
        
        return {
            "month_name": month_name,
            "growth": growth_list,
            "contraction": contraction_list,
            "no_growth": no_growth_list,
            "no_decline": no_decline_list,
            "pmi_data": pmi_data,
            "summary": summary_text,
            "comments": comments_list
        }

    except Exception as e:
        print(f"Error scraping {month_name}: {e}")
        return None

def parse_ism_list(raw_text):
    text = raw_text.replace('\n', ' ').replace('&amp;', '&')
    if ';' in text: tokens = text.split(';')
    else: tokens = text.split(',')
    clean_items = []
    for t in tokens:
        t = t.strip()
        if t.lower().startswith('and '): t = t[4:]
        if t.endswith('.'): t = t[:-1]
        if t: clean_items.append(t)
    return clean_items

def clean_name(name):
    name = name.strip()
    return INDUSTRY_MAP.get(name, name)

def update_html_with_revisions(updates):
    if not os.path.exists(HEATMAP_FILE): return

    with open(HEATMAP_FILE, 'r') as f: content = f.read()
    
    # 1. Parse 'months' array
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match:
        print("Could not find 'months' array.")
        return
    
    try:
        # Use simple eval for list of strings (safe enough here) or json.loads if valid json
        # JS format: ["Nov 2024", "Dec 2024"] - valid JSON
        current_months = json.loads(months_match.group(1))
    except:
        print("Error parsing months array.")
        return

    # 2. Parse 'data' object
    data_match = re.search(r'const data = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match:
        print("Could not find 'data' object.")
        return
    
    # JS object keys might be quoted or not, but in this file they are quoted.
    # However, values are arrays.
    # We'll use a regex to extract Industry -> Array mapping
    current_data = {}
    data_block = data_match.group(1)
    # Match "Industry Name": [1, 2, 3]
    # Assuming quoted keys
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        ind = match.group(1)
        arr_str = match.group(2)
        current_data[ind] = json.loads(arr_str)

    # 3. Parse 'ranklists' object
    # const ranklists = { "Month": { growth: [...], decline: [...] }, ... };
    ranklists_match = re.search(r'const ranklists = ({[\s\S]*?});', content, re.DOTALL)
    current_ranklists = {}
    if ranklists_match:
        # This is harder to regex parse cleanly due to nesting
        # But we only need to update specific months.
        # We can reconstruct it if we map the structure.
        # Check if we can parse it as strict JSON? Prob not (keys unquoted inside?)
        # Keys in HTML: "Nov 2024": { growth: [...], decline: [...] }
        # Field keys `growth`, `decline` are unquoted.
        pass

    # 4. Parse 'rawPmiData' array (Array of Objects)
    # const rawPmiData = [ { date: "...", ... }, ... ];
    # keys unquoted.
    pmi_match = re.search(r'const rawPmiData = (\[[\s\S]*?\]);', content)
    current_pmi_data = [] # We will rebuild this
    
    # --- processing updates ---
    
    # Sort updates by date (oldest to newest)
    sorted_updates = sorted(updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y"))
    
    for update in sorted_updates:
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:] # "Nov 2025"
        
        # A. Update Months List
        if short_month not in current_months:
            current_months.append(short_month)
        
        idx = current_months.index(short_month)
        
        # B. Update Main Data Scores
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
            
        # Update current_data arrays
        for ind in current_data:
            # ensure array is long enough
            while len(current_data[ind]) <= idx:
                current_data[ind].append(0)
            
            # Update value
            if ind in rank_map:
                current_data[ind][idx] = rank_map[ind]
            else:
                current_data[ind][idx] = 0
                
        # C. Update Pmi Data
        # We need to construct the PMI object string for this month
        # { date: "Nov 2025", pmi: 48.4, ... }
        pd = update['pmi_data']
        pmi_obj_str = f'{{ date: "{short_month}", pmi: {pd["pmi"]}, newOrders: {pd["newOrders"]}, production: {pd["production"]}, employment: {pd["employment"]}, supplierDel: {pd["supplierDel"]}, inv: {pd["inv"]}, custInv: {pd["custInv"]}, prices: {pd["prices"]}, backlog: {pd["backlog"]}, export: {pd["export"]}, imports: {pd["imports"]}, trend: "{pd["trend"]}" }}'
        
        # We need to insert/update this in rawPmiData string block
        # Approach: Read rawPmiData block. If date exists, replace object. Else prepend (since it's descending order in file usually).
        # Actually the file has: const rawPmiData = [ ... ];
        # We can rely on regex replacement of the whole block if we knew the others.
        # But we only fetched last 6 months.
        # Best approach: Use regex to find if this date exists in rawPmiData.
        # Pattern: { date: "Nov 2025", pmi: ... }
        # Note: keys unquoted.
        
        # We will use regex substitution on the 'content' string for PMI data
        # Search for `{ date: "Nov 2025", .*? }` and replace it.
        # If not found, insert at start of array (after `const rawPmiData = [`)
        
        pmi_pattern = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
        if pmi_pattern.search(content):
            # Replace existing
            content = pmi_pattern.sub(pmi_obj_str + ",", content) # Add comma to be safe, might result in double comma which JS tolerates or we clean
        else:
            # Insert new
            content = content.replace("const rawPmiData = [", "const rawPmiData = [\n            " + pmi_obj_str + ",", 1)

        # D. Update Ranklists
        # Same approach: regex replace or insert
        # const ranklists = {
        #    "Nov 2025": { ... },
        # }
        no_growth = update['no_growth']
        no_decline = update['no_decline']
        js_growth = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_growth]) + "]"
        js_decline = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_decline]) + "]"
        rank_entry = f'\n            "{short_month}": {{\n                growth: {js_growth},\n                decline: {js_decline}\n            }},'
        
        rank_pattern = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
        if rank_pattern.search(content):
            content = rank_pattern.sub(f'"{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', content)
        else:
             content = content.replace("const ranklists = {", "const ranklists = {" + rank_entry, 1)

    # --- Write Back Main Data Structures ---
    
    # 1. Months
    new_months_js = "const months = " + json.dumps(current_months) + ";"
    content = re.sub(r'const months = \[.*?\];', new_months_js, content, flags=re.DOTALL)
    
    # 2. Data
    # Manually build JS object string to preserve formatting
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const data = {\n" + ",\n".join(data_lines) + "\n        };"
    content = re.sub(r'const data = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)
    
    # Cleanup any double commas from regex insertions
    content = content.replace(",,", ",")
    
    # Update Meta Version
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    if 'name="deployment-version"' in content:
        content = re.sub(r'<meta name="deployment-version" content=".*?">', 
                         f'<meta name="deployment-version" content="auto-updated-{timestamp}">', 
                         content)
                         
    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("HTML Updated.")

def update_comments_block(updates):
    if not os.path.exists(COMMENTS_FILE): return
    with open(COMMENTS_FILE, 'r') as f: content = f.read()
    
    # We want to check revisions for comments too.
    # Approach: For each month, check if header exists. If so, replace the block.
    # Block format:
    # ## Nov 2025
    # - ...
    # (Ends at next ## or end)
    
    sorted_updates = sorted(updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y"), reverse=True)
    
    for update in sorted_updates:
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:]
        comments = update['comments']
        if not comments: continue
        
        # Build new block
        block_lines = [f"## {short_month}"]
        for ind, quote in comments:
            block_lines.append(f'- **{clean_name(ind)}**: "{quote}"')
        new_block_str = "\n".join(block_lines) + "\n"
        
        # Regex to find existing block
        # Look for ## Month ... until next ## or ` (end of string)
        # We need to be careful with regex boundaries.
        pattern = re.compile(r'(## ' + short_month + r'.*?)(\n## |$)', re.DOTALL)
        
        match = pattern.search(content)
        if match:
            # Replace existing
            # We must preserve the group(2) (the next header or end)
            content = content.replace(match.group(1), new_block_str.strip() + "\n")
            print(f"Updated comments for {short_month}")
        else:
            # Prepend (which is what we typically do for new)
            # Find start of string
            content = content.replace("const rawComments = `", "const rawComments = `" + new_block_str)
            print(f"Added comments for {short_month}")
            
    with open(COMMENTS_FILE, 'w') as f: f.write(content)

def main():
    print("\n" + "="*60)
    print("ISM Manufacturing PMI Data Update")
    print("="*60 + "\n")
    
    dates = get_last_n_months(2)
    all_updates = {}
    failed_months = []
    
    for d in dates:
        data = fetch_report_data(d)
        if data:
            all_updates[d.strftime("%Y-%m")] = data
            print(f"✓ Successfully processed {d.strftime('%B %Y')}\n")
        else:
            failed_months.append(d.strftime('%B %Y'))
            print(f"✗ Failed to process {d.strftime('%B %Y')}\n")
    
    if all_updates:
        print(f"\n{'='*60}")
        print(f"Updating HTML files with {len(all_updates)} month(s) of data...")
        print(f"{'='*60}\n")
        
        update_html_with_revisions(all_updates)
        update_comments_block(all_updates)
        
        print(f"✓ HTML files updated successfully!")
    else:
        print("\n⚠ WARNING: No data was fetched. HTML files were not updated.")
        print("This could be due to:")
        print("  - ISM website is temporarily down")
        print("  - Network connectivity issues")
        print("  - The website structure has changed")
        print("\nPlease try again later or check the ISM website manually:")
        print("  https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/")
    
    if failed_months:
        print(f"\n⚠ Failed to fetch data for: {', '.join(failed_months)}")
    
    print(f"\n{'='*60}")
    print("ISM Update Complete")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
