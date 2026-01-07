import requests
import re
import datetime
import os
import ssl
import json
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- Configuration ---
HEATMAP_FILE = "services_pmi.html"
COMMENTS_FILE = "services_comments.html"
INDEX_FILE = "index.html"
BASE_URL = "https://www.ismworld.org"
LANDING_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/services/"

# Services Industries Map
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

def get_last_n_months(n=6):
    dates = []
    today = datetime.date.today()
    curr = today.replace(day=1) - datetime.timedelta(days=1)
    for _ in range(n):
        dates.append(curr)
        curr = curr.replace(day=1) - datetime.timedelta(days=1)
    return dates

def fetch_url(url, max_retries=3):
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
            return response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:
                wait_time = 2 ** attempt
                print(f"⚠ Server unavailable (503). Waiting {wait_time}s before retry...")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed to fetch {url} after {max_retries} attempts: {e}")
                    return None
            else:
                print(f"✗ HTTP Error {e.response.status_code}: {e}")
                return None
        except Exception as e:
            print(f"✗ Failed to fetch {url}: {e}")
            return None
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

def fetch_report_data(target_date):
    month_name = target_date.strftime("%B %Y")
    print(f"Targeting Report: {month_name}")
    month_slug = month_name.split()[0].lower()
    
    # Strategy A: Direct URL
    direct_url = f"{BASE_URL}/supply-management-news-and-reports/reports/ism-pmi-reports/services/{month_slug}/"
    text = fetch_url(direct_url)
    
    # Strategy B: Landing Page
    if not text:
        landing_html = fetch_url(LANDING_URL)
        if landing_html:
            link_pattern = re.compile(r'href="([^"]*?/services/' + month_slug + r'[^"]*?)"', re.IGNORECASE)
            match = link_pattern.search(landing_html)
            if match:
                report_url = match.group(1)
                if not report_url.startswith("http"):
                    report_url = BASE_URL + report_url
                text = fetch_url(report_url)
    
    if not text: return None

    # --- Extract Data ---
    growth_list = []
    contraction_list = []
    main_growth_re = re.search(r"industries reporting growth in .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_growth_re: growth_list = parse_ism_list(main_growth_re.group(1))

    main_cont_re = re.search(r"industries reporting (?:contraction|a decrease) in .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if main_cont_re: contraction_list = parse_ism_list(main_cont_re.group(1))

    no_growth_list = []
    no_decline_list = []
    no_growth_re = re.search(r"industries reporting (?:growth|an increase) in New Orders .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_growth_re: no_growth_list = parse_ism_list(no_growth_re.group(1))

    no_decline_re = re.search(r"industries reporting (?:contraction|a decrease|a decline) in New Orders .*?(?:are|include):? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if not no_decline_re:
        # Fallback for "The X industries reporting..." phrasing
         no_decline_re = re.search(r"industries reporting a (?:decrease|decline|contraction) in new orders .*? are:? (.*?)\.", text, re.IGNORECASE | re.DOTALL)
    if no_decline_re: no_decline_list = parse_ism_list(no_decline_re.group(1))

    # --- Indices ---
    def get_index(label):
        pat = re.compile(f"{label}.*?registered\\s+([\\d\\.]+)\\s+percent", re.IGNORECASE | re.DOTALL)
        m = pat.search(text)
        if m: return float(m.group(1))
        return 0.0

    pmi_data = {
        "pmi": get_index("Services PMI"),
        "businessActivity": get_index("Business Activity Index"),
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

    data_mapped = {
        "servicesPmi": pmi_data["pmi"], # Note key change for HTML
        "businessActivity": pmi_data["businessActivity"], 
        "newOrders": pmi_data["newOrders"],
        "employment": pmi_data["employment"],
        "supplierDeliveries": pmi_data["supplierDel"], # HTML key
        "inventories": pmi_data["inv"], # HTML key
        "inventorySentiment": pmi_data["invSentiment"], # HTML key
        "prices": pmi_data["prices"],
        "backlogOrders": pmi_data["backlog"], # HTML key
        "newExportOrders": pmi_data["export"], # HTML key
        "imports": pmi_data["imports"],
    }

    # --- Summary ---
    summary_text = ""
    summ_match = re.search(r"(Economic activity in the services sector.*?)(?=\n|<br>)", text, re.IGNORECASE)
    if summ_match: summary_text = summ_match.group(1).strip()
    else: summary_text = f"The Services PMI registered {pmi_data['pmi']} percent in {month_name}."

    # --- New Orders Summary ---
    no_val = pmi_data["newOrders"]
    no_trend = "grew" if no_val > 50 else "contracted"
    if no_val == 50: no_trend = "remained unchanged"
    no_summary = f"The New Orders Index registered {no_val} percent in {month_name}. New orders {no_trend} for the month."

    # --- Comments ---
    comments_list = []
    start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
    if start_comments != -1:
        end_comments = text.find("Services PMI", start_comments + 30)
        if end_comments == -1: end_comments = len(text)
        section = text[start_comments:end_comments]
        list_items = re.findall(r"<li>(.*?)</li>", section, re.DOTALL)
        for item in list_items:
            clean_item = re.sub(r'<[^>]+>', '', item).strip().replace('&amp;', '&')
            # Format A: Industry: "Quote"
            if ":" in clean_item:
                parts = clean_item.split(":", 1)
                ind = clean_name(parts[0].strip())
                quote = parts[1].strip().strip('"')
                comments_list.append((ind, quote))
            # Format B: "Quote" (Industry) or "Quote" [Industry]
            else:
                m = re.search(r'[\(\[]\s*(.*?)\s*[\)\]]\s*$', clean_item)
                if m:
                    potential_ind = m.group(1)
                    quote = clean_item[:m.start()].strip().strip('"')
                    ind = clean_name(potential_ind)
                    comments_list.append((ind, quote))

    return {
        "month_name": month_name,
        "growth": growth_list,
        "contraction": contraction_list,
        "no_growth": no_growth_list,
        "no_decline": no_decline_list,
        "pmi_data": data_mapped,
        "summary": summary_text,
        "no_summary": no_summary,
        "comments": comments_list
    }

def update_html_with_revisions(updates):
    if not os.path.exists(HEATMAP_FILE): return
    with open(HEATMAP_FILE, 'r') as f: content = f.read()

    # 1. Parse months
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match: return
    try: current_months = json.loads(months_match.group(1))
    except: return

    # 2. Parse data
    data_match = re.search(r'const servicesData = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match: return
    current_data = {}
    data_block = data_match.group(1)
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        ind = match.group(1)
        current_data[ind] = json.loads(match.group(2))

    sorted_updates = sorted(updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y"))

    for update in sorted_updates:
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:]

        if short_month not in current_months: current_months.append(short_month)
        idx = current_months.index(short_month)

        # Update Ranks in data
        rank_map = {}
        growth = update['growth']
        contraction = update['contraction']
        num_growth = len(growth)
        for i, raw_name in enumerate(growth): rank_map[clean_name(raw_name)] = num_growth - i
        num_cont = len(contraction)
        for i, raw_name in enumerate(contraction): rank_map[clean_name(raw_name)] = -(num_cont - i)

        for ind in current_data:
            while len(current_data[ind]) <= idx: current_data[ind].append(0)
            if ind in rank_map: current_data[ind][idx] = rank_map[ind]
            else: current_data[ind][idx] = 0

        # Update PMI Data
        pd = update['pmi_data']
        # { date: "Nov 2025", servicesPmi: ..., ... }
        pmi_obj_str = f'{{ date: "{short_month}", servicesPmi: {pd["servicesPmi"]}, businessActivity: {pd["businessActivity"]}, newOrders: {pd["newOrders"]}, employment: {pd["employment"]}, supplierDeliveries: {pd["supplierDeliveries"]}, inventories: {pd["inventories"]}, prices: {pd["prices"]}, backlogOrders: {pd["backlogOrders"]}, newExportOrders: {pd["newExportOrders"]}, imports: {pd["imports"]}, inventorySentiment: {pd["inventorySentiment"]} }}'
        
        # Regex replacement in rawServicesPmiData
        pmi_pattern = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
        if pmi_pattern.search(content):
            content = pmi_pattern.sub(pmi_obj_str + ",", content)
        else:
            content = content.replace("const rawServicesPmiData = [", "const rawServicesPmiData = [\n            " + pmi_obj_str + ",", 1)

        # Update Ranklists
        no_growth = update['no_growth']
        no_decline = update['no_decline']
        js_growth = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_growth]) + "]"
        js_decline = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_decline]) + "]"
        rank_pattern = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
        if rank_pattern.search(content):
            content = rank_pattern.sub(f'"{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', content)
        else:
             content = content.replace("const ranklists = {", f'const ranklists = {{\n            "{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', 1)

    # Write back Main Structures
    new_months_js = "const months = " + json.dumps(current_months) + ";"
    content = re.sub(r'const months = \[.*?\];', new_months_js, content, flags=re.DOTALL)
    
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const servicesData = {\n" + ",\n".join(data_lines) + "\n        };"
    content = re.sub(r'const servicesData = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)
    
    content = content.replace(",,", ",")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    if 'name="deployment-version"' in content:
        content = re.sub(r'<meta name="deployment-version" content=".*?">', 
                         f'<meta name="deployment-version" content="auto-updated-{timestamp}">', 
                         content)

    today_str = datetime.date.today().strftime("%b %d, %Y")
    content = re.sub(r'<span id="last-updated-date">.*?</span>', 
                     f'<span id="last-updated-date">{today_str}</span>', 
                     content)

    # Update Bottom Summary Box (services-pmi-survey-insights)
    # Using the latest update's summary
    if sorted_updates:
        latest_update = sorted_updates[-1]
        l_month = latest_update['month_name']
        l_summary = latest_update['summary']
        l_no_summary = latest_update.get('no_summary', '')
        # Short month format: Nov 2025
        l_short_month = l_month[:3] + " " + l_month[-4:]
        
        # 1. Bottom Summary (services-pmi-survey-insights)
        summary_pattern = r'(<div id="services-pmi-survey-insights"[^>]*>)\s*<span class="summary-title">Key Insights \(.*?\)</span>\s*<p>.*?</p>\s*(?=</div>)'
        new_summary_html = f'\\1\n        <span class="summary-title">Key Insights ({l_short_month})</span>\n        <p>{l_summary}</p>'
        
        if re.search(summary_pattern, content, re.DOTALL):
            content = re.sub(summary_pattern, new_summary_html, content, flags=re.DOTALL)

        # 2. Main Summary Box (main-summary-box)
        # Note: generate_services_key_insights.py appends Trend Analysis *after* the <p>.
        # We want to replace the <h3> and <p> but KEEP the Trend Analysis if present (or let the other script handle it).
        # Actually, replace_file_content replaces the whole block.
        # Let's match up to the <p>...</p>.
        # If Trend Analysis exists, it follows the <p>.
        
        main_sum_pat = r'(<div id="main-summary-box"[^>]*>)\s*<h3>Key Insights \(.*?\)</h3>\s*<p>.*?</p>'
        new_main_html = f'\\1\n        <h3>Key Insights ({l_short_month})</h3>\n        <p>{l_summary}</p>'
        if re.search(main_sum_pat, content, re.DOTALL):
            content = re.sub(main_sum_pat, new_main_html, content, flags=re.DOTALL)

        # 3. New Orders Summary Box (new-orders-summary-box)
        no_sum_pat = r'(<div id="new-orders-summary-box"[^>]*>)\s*<h3>New Orders Key Insights \(.*?\)</h3>\s*<p>.*?</p>'
        new_no_html = f'\\1\n        <h3>New Orders Key Insights ({l_short_month})</h3>\n        <p>{l_no_summary}</p>'
        if re.search(no_sum_pat, content, re.DOTALL):
            content = re.sub(no_sum_pat, new_no_html, content, flags=re.DOTALL)

        if re.search(no_sum_pat, content, re.DOTALL):
            content = re.sub(no_sum_pat, new_no_html, content, flags=re.DOTALL)

    # Update Title Date Range
    # current_months is fully updated now.
    if current_months:
        start_m = current_months[0] # e.g. "Nov 2024"
        end_m = current_months[-1]   # e.g. "Dec 2025"
        
        def format_title_date(m_str):
            parts = m_str.split()
            if len(parts) == 2:
                return f"{parts[0]} '{parts[1][2:]}"
            return m_str

        title_start = format_title_date(start_m)
        title_end = format_title_date(end_m)
        new_title = f"ISM Services Industry Trends ({title_start} - {title_end})"
        
        # Regex to find H1
        # <h1>ISM Services Industry Trends (Nov '24 - Nov '25)</h1>
        title_pattern = r'<h1>ISM Services Industry Trends \(.*?\)</h1>'
        content = re.sub(title_pattern, f'<h1>{new_title}</h1>', content)

    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("Services HTML Updated.")

def update_comments_block(updates):
    if not os.path.exists(COMMENTS_FILE): return
    with open(COMMENTS_FILE, 'r') as f: content = f.read()

    sorted_updates = sorted(updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y"), reverse=True)

    for update in sorted_updates:
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:]
        comments = update['comments']
        if not comments: continue

        block_lines = [f"## {short_month}"]
        for ind, quote in comments:
            block_lines.append(f'- **{clean_name(ind)}**: "{quote}"')
        new_block_str = "\n".join(block_lines) + "\n"

        pattern = re.compile(r'(## ' + short_month + r'.*?)(\n## |$)', re.DOTALL)
        match = pattern.search(content)
        if match:
            content = content.replace(match.group(1), new_block_str.strip() + "\n")
        else:
            content = content.replace("const rawComments = `", "const rawComments = `" + new_block_str)

    with open(COMMENTS_FILE, 'w') as f: f.write(content)

def update_index_timestamp():
    """Update the 'Last Updated' timestamp for Services PMI in index.html"""
    if not os.path.exists(INDEX_FILE): return
    
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        # Look for the Services PMI card meta specifically
        # <a href="services_pmi.html" class="card services">
        # ...
        # <span>Macro Indicator • Dec 20, 2025</span>
        pattern = re.compile(
            r'(class="card services".*?<span>)(Macro Indicator\s*•\s*)([^<]*?)(</span>)', 
            re.DOTALL | re.IGNORECASE
        )
        
        if pattern.search(content):
            today_str = datetime.date.today().strftime("%b %d, %Y")
            # Replacement: capture group 1 + constant label + group 3
            content = pattern.sub(f"\\g<1>Macro Indicator • {today_str}\\g<4>", content)
            
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✓ Updated Index Page timestamp for Services PMI.")
    except Exception as e:
        print(f"Error updating index timestamp: {e}")

def main():
    dates = get_last_n_months(2)
    all_updates = {}
    for d in dates:
        data = fetch_report_data(d)
        if data: all_updates[d.strftime("%Y-%m")] = data
    
    if all_updates:
        update_html_with_revisions(all_updates)
        update_comments_block(all_updates)

    update_index_timestamp()

if __name__ == "__main__":
    main()
