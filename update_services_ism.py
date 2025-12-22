import requests
import re
import datetime
import os
import sys

# --- Configuration ---
HEATMAP_FILE = "services_pmi.html"
COMMENTS_FILE = "services_comments.html"
INDEX_FILE = "index.html"

# Base URLs
BASE_URL = "https://www.ismworld.org"
LANDING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/services/"

# Services Industries Map (18 Industries)
INDUSTRY_MAP = {
    "Accommodation & Food Services": "Accommodation & Food Services",
    "Accommodation & Food": "Accommodation & Food Services",
    "Agriculture, Forestry, Fishing & Hunting": "Agriculture, Forestry, Fishing & Hunting",
    "Ag, Forestry, Fishing & Hunting": "Agriculture, Forestry, Fishing & Hunting",
    "Arts, Entertainment & Recreation": "Arts, Entertainment & Recreation",
    "Arts, Entertainment & Rec": "Arts, Entertainment & Recreation",
    "Construction": "Construction",
    "Educational Services": "Educational Services",
    "Education": "Educational Services",
    "Finance & Insurance": "Finance & Insurance",
    "Health Care & Social Assistance": "Health Care & Social Assistance",
    "Health Care": "Health Care & Social Assistance",
    "Information": "Information",
    "Management of Companies & Support Services": "Management of Companies & Support Services",
    "Mgmt of Companies": "Management of Companies & Support Services",
    "Management of Companies": "Management of Companies & Support Services",
    "Mining": "Mining",
    "Other Services": "Other Services",
    "Professional, Scientific & Technical Services": "Professional, Scientific & Technical Services",
    "Prof, Sci & Tech Services": "Professional, Scientific & Technical Services",
    "Public Administration": "Public Administration",
    "Real Estate, Rental & Leasing": "Real Estate, Rental & Leasing",
    "Retail Trade": "Retail Trade",
    "Retail": "Retail Trade",
    "Transportation & Warehousing": "Transportation & Warehousing",
    "Transportation": "Transportation & Warehousing",
    "Utilities": "Utilities",
    "Wholesale Trade": "Wholesale Trade"
}

def get_target_month_name():
    """Calculates the previous month name relative to today."""
    today = datetime.date.today()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    return last_month.strftime("%B %Y")

def fetch_url(url):
    print(f"Fetching: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def fetch_report_data():
    target_month = get_target_month_name()
    print(f"Targeting Report: {target_month}")
    
    # 1. Strategy A: Direct URL Construction (User Request)
    month_slug = target_month.split()[0].lower()
    # Format: .../services/month/ (e.g. services/november/)
    direct_url = f"{BASE_URL}/supply-management-news-and-reports/reports/ism-pmi-reports/services/{month_slug}/"
    
    print(f"Attempting Direct URL: {direct_url}")
    text = fetch_url(direct_url)
    
    # 2. Strategy B: Landing Page Scrape (Fallback)
    if not text:
        print("Direct URL failed. Falling back to Landing Page scrape.")
        landing_html = fetch_url(LANDING_URL)
        if landing_html:
            # Pattern: href=".../services/monthname.../"
            link_pattern = re.compile(r'href="([^"]*?/services/' + month_slug + r'[^"]*?)"', re.IGNORECASE)
            match = link_pattern.search(landing_html)
            
            if match:
                report_url = match.group(1)
                if not report_url.startswith("http"):
                    report_url = BASE_URL + report_url
                text = fetch_url(report_url)
            else:
                 print(f"Could not find link for {month_slug} report on ISM Landing Page.")

    if not text: 
        return None
        
    # 3. Fetch Report

    
    # Clean text to remove HTML tags for easier regex? 
    # Or just use regex on HTML. Using simplified regex on HTML/Text mixed is usually fine for these patterns.
    
    # --- Extract Main Services PMI Industries ---
    growth_list = []
    contraction_list = []
    
    # Pattern: "The [number] industries reporting growth in [Month] are: [List]."
    main_growth_re = re.search(r"industries reporting growth in .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_growth_re:
        growth_list = parse_ism_list(main_growth_re.group(1))

    main_cont_re = re.search(r"industries reporting (?:contraction|a decrease) in .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_cont_re:
        contraction_list = parse_ism_list(main_cont_re.group(1))

    # --- Extract New Orders Industries ---
    no_growth_list = []
    no_decline_list = []

    no_growth_re = re.search(r"industries reporting (?:growth|an increase) in New Orders .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_growth_re:
        no_growth_list = parse_ism_list(no_growth_re.group(1))

    no_decline_re = re.search(r"industries reporting (?:contraction|a decrease) in New Orders .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_decline_re:
        no_decline_list = parse_ism_list(no_decline_re.group(1))
        
    # --- Extract PMI Indices ---
    def get_index(label):
        # "Services PMI® registered 52.6 percent"
        # "Business Activity Index registered 57.1 percent"
        pat = re.compile(f"{label}.*?registered\\s+([\\d\\.]+)\\s+percent", re.IGNORECASE | re.DOTALL)
        m = pat.search(text)
        if m: return float(m.group(1))
        return 0.0

    pmi_data = {
        "pmi": get_index("Services PMI"), # Usually just "Services PMI" or "Services PMI®"
        "businessActivity": get_index("Business Activity Index"), # This is Production equiv
        "newOrders": get_index("New Orders Index"),
        "employment": get_index("Employment Index"),
        "supplierDel": get_index("Supplier Deliveries Index"),
        "inv": get_index("Inventories Index"),
        "prices": get_index("Prices Index"),
        "backlog": get_index("Backlog of Orders Index"),
        "export": get_index("New Export Orders Index"),
        "imports": get_index("Imports Index"),
        "invSentiment": get_index("Inventory Sentiment Index") 
    }
    # Note: Services has slightly different fields than Mfg (Business Activity instead of Production)
    # But in our heatmap HTML we mapped:
    # { key: 'production', label: 'Business Activity' } for compatibility or changed label?
    # Let's check HTML. 
    # HTML has: { key: 'production', label: 'Business Activity' }, { key: 'custInv', label: 'Inventory Sentiment' }
    
    data_mapped = {
        "pmi": pmi_data["pmi"],
        "newOrders": pmi_data["newOrders"],
        "production": pmi_data["businessActivity"], 
        "employment": pmi_data["employment"],
        "supplierDel": pmi_data["supplierDel"],
        "inv": pmi_data["inv"],
        "custInv": pmi_data["invSentiment"],
        "prices": pmi_data["prices"],
        "backlog": pmi_data["backlog"],
        "export": pmi_data["export"],
        "imports": pmi_data["imports"],
        "trend": "Expansion" if pmi_data["pmi"] > 50 else "Contraction"
    }

    # --- Extract Summary ---
    # Look for the first paragraph generally describing the sector
    summary_text = ""
    # "Economic activity in the services sector expanded in..."
    summ_match = re.search(r"(Economic activity in the services sector.*?)(?=\n|<br>)", text, re.IGNORECASE)
    if summ_match:
        summary_text = summ_match.group(1).strip()
    else:
        summary_text = f"The Services PMI registered {data_mapped['pmi']} percent in {target_month}."

    # --- Extract New Orders Summary (Optional) ---
    # "New Orders grew in [Month]..."
    # Keep it simple for now.
    
    # --- Extract Comments ---
    start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
    comments_list = []
    
    if start_comments != -1:
        # Find end - usually "Services PMI®" table header or similar
        end_comments = text.find("Services PMI", start_comments + 30) # Skip header itself
        if end_comments == -1: end_comments = len(text)
        
        section = text[start_comments:end_comments]
        # Regex for list items
        # Format usually: <li>[Industry]: "[Comment]"</li>
        list_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
        
        for item in list_items:
            clean_item = re.sub(r'<[^>]+>', '', item).strip().replace('&amp;', '&')
            
            ind = ""
            quote = ""
            
            if ":" in clean_item:
                parts = clean_item.split(":", 1)
                ind = clean_name(parts[0].strip())
                quote = parts[1].strip().strip('"')
                comments_list.append((ind, quote))
    
    # If using PR Newswire/Plain text, the structure might be bullets
    if not comments_list and "WHAT RESPONDENTS ARE SAYING" in text:
        # Fallback text parsing
        section = text[start_comments:end_comments]
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if ":" in line and (line.startswith("-") or line.startswith("\u2022")): # bullet
                parts = line.replace("-", "").replace("\u2022", "").strip().split(":", 1)
                if len(parts) == 2:
                    ind = clean_name(parts[0].strip())
                    quote = parts[1].strip().strip('"')
                    comments_list.append((ind, quote))

    return target_month, growth_list, contraction_list, no_growth_list, no_decline_list, data_mapped, summary_text, comments_list

def parse_ism_list(raw_text):
    text = raw_text.replace('\n', ' ').replace('&amp;', '&')
    # ISM lists are separated by semicolons usually, or commas if simple
    tokens = []
    if ';' in text:
        tokens = text.split(';')
    else:
        tokens = text.split(',')
        
    clean_items = []
    for t in tokens:
        t = t.strip()
        # Remove "and " if it's the last item
        if t.lower().startswith('and '): t = t[4:]
        if t.endswith('.'): t = t[:-1]
        if t: clean_items.append(t)
    return clean_items

def clean_name(name):
    name = name.strip()
    # Map to our standard keys
    return INDUSTRY_MAP.get(name, name) # specific overrides, else default

def update_heatmap_file(month_str, growth, contraction, no_growth, no_decline, pmi_data, summary):
    if not os.path.exists(HEATMAP_FILE):
        print(f"Error: {HEATMAP_FILE} not found.")
        return

    with open(HEATMAP_FILE, 'r') as f: content = f.read()
    
    print(f"Updating Services Heatmap for {month_str}")
    short_month = month_str[:3] + " " + month_str[-4:] # "Nov 2025" for display

    # Check if month is already explicitly in the months array (quoted)
    month_exists = f'"{short_month}"' in content

    if month_exists:
        print(f"Month {short_month} already present in data. Skipping heatmap updates.")
    
    # 1. Update Months Array
    # const months = [ ... ];
    if not month_exists:
        content = re.sub(r'(const months = \[\s*[\s\S]*?)(\s*\];)', f'\\1, "{short_month}"\\2', content)

    # 2. Update Main Heatmap Scores
    # Calculate scores from list position
    rank_map = {} 
    num_growth = len(growth)
    for i, raw_name in enumerate(growth):
        our_key = clean_name(raw_name)
        rank_map[our_key] = num_growth - i 
        
    num_cont = len(contraction)
    for i, raw_name in enumerate(contraction):
        our_key = clean_name(raw_name)
        rank_map[our_key] = -(num_cont - i)

    # Regex update: "Industry": [ ..., new_val ]
    # ONLY append if the month didn't exist before this run
    if not month_exists:
        for key in set(INDUSTRY_MAP.values()):
            if f'"{key}"' not in content: continue
            
            new_val = rank_map.get(key, 0)
            esc_key = re.escape(key)
            pattern = f'("{esc_key}":\\s*\\[.*?)(\\])'
            # This regex grabs everything until the closing bracket.
            content = re.sub(pattern, f'\\1, {new_val}\\2', content)

    # 3. Update New Orders Ranklists
    # const ranklists = { ... }
    # Add new month key
    if not month_exists:
        js_growth = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_growth]) + "]"
        js_decline = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_decline]) + "]"
        
        # Insert at top of ranklists object? or bottom? 
        # Insert after `const ranklists = {`
        new_entry = f'\n            "{short_month}": {{\n                growth: {js_growth},\n                decline: {js_decline}\n            }},'
        content = content.replace("const ranklists = {", "const ranklists = {" + new_entry)

    # 4. Update PMI Data
    # const sortedPmiData = [ ... ] or "rawPmiData"
    # Note: In services_pmi.html, we might not have a full PMI table defined efficiently as a list of objects yet?
    # I built it as: const servicesData = { ... } and separate `ranklists`.
    # Wait, I did NOT add a PMI trend table to services_pmi.html in previous steps! I only added the heatmap and rank table.
    # checking file... 
    # Actually, I see `New Orders Services Growth Rank` but I don't see a `rawPmiData` array for a bottom table like Mfg has.
    # If it's missing, I skip this step.
    
    # 5. Update Key Insights
    # Search for the first summary box content
    # <div class="summary-box"> ... The <strong>Services PMI</strong> ... </div>
    # Regex replacement for the content between summary-title and /div
    # Assuming the first one is the main summary.
    
    if summary:
        # Construct new HTML for summary
        new_summary_html = f'''
        <span class="summary-title"
            style="text-transform: uppercase; font-size: 0.8em; letter-spacing: 0.5px; color: #d35400;">Key
            Insights ({short_month})</span><br>
        {summary}
        '''
        # Regex to replace the *first* summary box content
        # Matches: <div class="summary-box"> (content) </div>
        # Be careful not to replace all of them.
        
        # Find start of first summary box
        start_idx = content.find('<div class="summary-box">')
        if start_idx != -1:
            end_idx = content.find('</div>', start_idx)
            if end_idx != -1:
                # Replace content
                content = content[:start_idx] + '<div class="summary-box">' + new_summary_html + content[end_idx:]

    # 6. Update Meta Version
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    if 'name="deployment-version"' in content:
        content = re.sub(r'<meta name="deployment-version" content=".*?">', 
                         f'<meta name="deployment-version" content="auto-updated-{timestamp}">', 
                         content)

    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("Updated Services Heatmap HTML.")

def update_comments_file(month_str, comments):
    if not os.path.exists(COMMENTS_FILE): return
    if not comments: return

    with open(COMMENTS_FILE, 'r') as f: content = f.read()

    short_month = month_str[:3] + " " + month_str[-4:] 
    
    if f"## {short_month}" in content:
        print("Comments for this month already exist.")
        return

    print(f"Adding {len(comments)} comments for {short_month}")
    
    block_lines = [f"\n## {short_month}"]
    for ind, quote in comments:
        block_lines.append(f'- **{ind}**: "{quote}"')
    
    new_block = "\n".join(block_lines) + "\n"
    
    # Prepend to rawComments variable
    content = content.replace("const rawComments = `", "const rawComments = `" + new_block)

    with open(COMMENTS_FILE, 'w') as f: f.write(content)
    print("Updated Services Comments HTML.")

def update_index_page(month_str):
    if not os.path.exists(INDEX_FILE): return
    
    with open(INDEX_FILE, 'r') as f: content = f.read()
    
    # Look for Services PMI entry and update "Last updated"
    # Heuristic: Find "Services PMI" and then the next "Last updated: ..."
    # This might need adjustment based on index.html structure.
    # Assuming standard format: <small>Last updated: Nov 2025</small>
    
    # We'll just replace the FIRST occurrence associated with Services? 
    # Or strict regex lookaround?
    # Let's try to match the specific card.
    
    # Regex: Look for the Services card data
    # <a href="services_pmi.html"                <span>Macro Indicator • Dec 22, 2025</span>
    # We want to replace the text after the bullet.
    
    # Pattern to find the Services card block start, then the meta span
    # We'll use a slightly broader match
    # Match: (href="services_pmi.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)
    pattern = re.compile(r'(href="services_pmi.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        # Update to current date Month DD, YYYY
        today_str = datetime.date.today().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        
        with open(INDEX_FILE, 'w') as f: f.write(content)
        print("Updated Index Page timestamp.")
    else:
        print("Could not find Services PMI timestamp in index.html")

if __name__ == "__main__":
    # Fetch data
    res = fetch_report_data()
    if res:
        m, g, c, ng, nd, pmi, summ, comms = res
        print(f"Successfully fetched data for {m}")
        print(f"Growth: {len(g)}, Contraction: {len(c)}")
        print(f"New Orders Growth: {len(ng)}, Decline: {len(nd)}")
        print(f"Comments: {len(comms)}")
        
        update_heatmap_file(m, g, c, ng, nd, pmi, summ)
        update_comments_file(m, comms)
        update_index_page(m)
    else:
        print("Failed to fetch report data.")
        sys.exit(1)
