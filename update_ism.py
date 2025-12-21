import requests
import re
import datetime
import os
import ssl
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- Configuration ---
HEATMAP_FILE = "industry_heatmap.html"
COMMENTS_FILE = "industry_comments.html"
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

def get_previous_month_name():
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    return last_month.strftime("%B %Y")

def fetch_url(url):
    print(f"Fetching: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        raise e

def fetch_report_data():
    target_month = get_previous_month_name()
    print(f"Targeting Report: {target_month}")
    
    try:
        # 1. Get Landing Page
        landing_html = fetch_url(LANDING_URL)
        
        # 2. Find Link to Report
        # New structure: href="/supply-management-news-and-reports/reports/ism-pmi-reports/pmi/november/"
        month_slug = target_month.split()[0].lower() # "November 2025" -> "november"
        
        # Regex to find link with /pmi/monthname/
        # We look for href containing /pmi/november/ 
        link_pattern = re.compile(r'href="([^"]*?/pmi/' + month_slug + r'/?)"', re.IGNORECASE)
        match = link_pattern.search(landing_html)
        
        if not match:
            print(f"Could not find link for {month_slug} report.")
            return None, None, None, None, None, None, None, None

        report_url = match.group(1)
        if not report_url.startswith("http"):
            report_url = BASE_URL + report_url
            
        # 3. Fetch Report
        text = fetch_url(report_url)
        
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
            summary_text = f"The Manufacturing PMI registered {pmi_data['pmi']} percent in {target_month}."

        # --- Extract Comments ---
        # Look for "WHAT RESPONDENTS ARE SAYING"
        # Then capture <li> items until the next header or end of section.
        # Format: <li>"Quote" [Industry]</li> or <li>"Quote" ([Industry])</li>
        # Sometimes: <li>[Industry]: "Quote"</li>
        
        start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
        comments_list = []
        
        if start_comments != -1:
            # Narrow text to this section
            # Assume it ends before "Manufacturing PMI" table/header
            end_comments = text.find("Manufacturing PMI", start_comments)
            if end_comments == -1: end_comments = len(text)
            
            section = text[start_comments:end_comments]
            # Simple list item scraper
            list_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
            
            for item in list_items:
                # Remove HTML tags
                clean_item = re.sub(r'<[^>]+>', '', item).strip()
                # Parse "Industry" and "Quote"
                # Heuristic: Look for colon? "Industry: Quote"
                if ":" in clean_item:
                    parts = clean_item.split(":", 1)
                    ind = clean_name(parts[0].strip())
                    quote = parts[1].strip().strip('"')
                    comments_list.append((ind, quote))
                # Heuristic: Look for parentheses? "Quote" (Industry)
                elif "(" in clean_item and ")" in clean_item:
                     # "Quote" (Industry)
                     parts = clean_item.rsplit("(", 1)
                     quote = parts[0].strip().strip('"')
                     ind = clean_name(parts[1].replace(")", "").strip())
                     comments_list.append((ind, quote))
        
        return target_month, growth_list, contraction_list, no_growth_list, no_decline_list, pmi_data, summary_text, comments_list

    except Exception as e:
        print(f"Error scraping: {e}")
        return None, None, None, None, None, None, None, None

def parse_ism_list(raw_text):
    text = raw_text.replace('\n', ' ')
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
    # Strip common variations
    name = name.strip()
    return name

def update_heatmap(month_str, growth, contraction, no_growth, no_decline, pmi_data, summary):
    if not os.path.exists(HEATMAP_FILE): return

    with open(HEATMAP_FILE, 'r') as f: content = f.read()
    
    print(f"Updating Heatmap for {month_str}")
    short_month = month_str[:3] + " " + month_str[-4:] # "Nov 2025"

    # Check if month already exists to avoid duplication
    if short_month in content:
        print(f"Month {short_month} already in heatmap. Skipping update.")
        return

    # 1. Update Months
    content = re.sub(r'(const months = \[\s*[\s\S]*?)(\s*\];)', f'\\1, "{short_month}"\\2', content)

    # 2. Update Main Scores
    rank_map = {} 
    num_growth = len(growth)
    for i, raw_name in enumerate(growth):
        our_key = INDUSTRY_MAP.get(raw_name, raw_name)
        rank_map[our_key] = num_growth - i 
    num_cont = len(contraction)
    for i, raw_name in enumerate(contraction):
        our_key = INDUSTRY_MAP.get(raw_name, raw_name)
        rank_map[our_key] = -(num_cont - i)

    for key in INDUSTRY_MAP.values():
        if key not in content: continue 
        new_val = rank_map.get(key, 0)
        esc_key = re.escape(key)
        # Search for: "Key": [ ... ]
        # We need to ensure we are appending to the array, not replacing.
        # Look for the closing bracket `]` of the specific array.
        # This regex must match specifically the data object.
        # Usually: "Industry": [1, 2, 3]
        pattern = f'("{esc_key}":\\s*\\[.*?)(\\])'
        content = re.sub(pattern, f'\\1, {new_val}\\2', content)

    # 3. Update New Orders Ranklists
    if f'"{short_month}":' not in content:
        js_growth = "[" + ", ".join([f'"{x}"' for x in no_growth]) + "]"
        js_decline = "[" + ", ".join([f'"{x}"' for x in no_decline]) + "]"
        new_entry = f'\n            "{short_month}": {{\n                growth: {js_growth},\n                decline: {js_decline}\n            }},'
        content = content.replace("const ranklists = {", "const ranklists = {" + new_entry)

    # 4. Update PMI Data
    if f'date: "{short_month}"' not in content:
        new_pmi_obj = f'''
    {{ 
        date: "{short_month}", 
        pmi: {pmi_data['pmi']}, 
        newOrders: {pmi_data['newOrders']}, 
        production: {pmi_data['production']}, 
        employment: {pmi_data['employment']}, 
        supplierDel: {pmi_data['supplierDel']}, 
        inv: {pmi_data['inv']}, 
        custInv: {pmi_data['custInv']}, 
        prices: {pmi_data['prices']}, 
        backlog: {pmi_data['backlog']}, 
        export: {pmi_data['export']}, 
        imports: {pmi_data['imports']}, 
        trend: "{pmi_data['trend']}" 
    }},'''
        content = content.replace("const rawPmiData = [", "const rawPmiData = [" + new_pmi_obj)

    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("Updated Heatmap HTML.")

def update_comments(month_str, comments):
    if not os.path.exists(COMMENTS_FILE): return
    if not comments: return

    with open(COMMENTS_FILE, 'r') as f: content = f.read()

    short_month = month_str[:3] + " " + month_str[-4:] # "Nov 2025"
    
    # Check if already present
    if f"## {short_month}" in content:
        print("Comments for this month already exist.")
        return

    print(f"Adding {len(comments)} comments for {short_month}")
    
    # Format new block
    # ## Nov 2025
    # - **Industry**: "Quote"
    
    block_lines = [f"\n## {short_month}"]
    for ind, quote in comments:
        # Map industry name if possible
        norm_ind = INDUSTRY_MAP.get(ind, ind)
        block_lines.append(f'- **{norm_ind}**: "{quote}"')
    
    new_block = "\n".join(block_lines) + "\n"
    
    # Prepend to `const rawComments = \``
    # We want it at the TOP of the string (newest first).
    # Regex: const rawComments = `
    content = content.replace("const rawComments = `", "const rawComments = `" + new_block)

    with open(COMMENTS_FILE, 'w') as f: f.write(content)
    print("Updated Comments HTML.")

if __name__ == "__main__":
    m, g, c, ng, nd, pmi, summ, comms = fetch_report_data()
    if m:
        update_heatmap(m, g, c, ng, nd, pmi, summ)
        update_comments(m, comms)
        print("Done.")
    else:
        print("Script finished without update.")

