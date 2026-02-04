#!/usr/bin/env python3
"""
Automated ISM Services PMI Update using Browser Automation
This script uses Playwright to handle the disclaimer modal and extract data automatically.
"""

import re
import json
import datetime
import os
import sys

# --- Configuration ---
HEATMAP_FILE = "services_pmi.html"
COMMENTS_FILE = "services_comments.html"
BASE_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/services/"

# Services Industries Map
INDUSTRY_MAP = {
    "Accommodation & Food Services": "Accommodation & Food Services",
    "Agriculture, Forestry, Fishing & Hunting": "Agriculture, Forestry, Fishing & Hunting",
    "Arts, Entertainment & Recreation": "Arts, Entertainment & Recreation",
    "Construction": "Construction",
    "Educational Services": "Educational Services",
    "Finance & Insurance": "Finance & Insurance",
    "Health Care & Social Assistance": "Health Care & Social Assistance",
    "Information": "Information",
    "Management of Companies & Support Services": "Management of Companies & Support Services",
    "Mining": "Mining",
    "Other Services": "Other Services",
    "Professional, Scientific & Technical Services": "Professional, Scientific & Technical Services",
    "Public Administration": "Public Administration",
    "Real Estate, Rental & Leasing": "Real Estate, Rental & Leasing",
    "Retail Trade": "Retail Trade",
    "Transportation & Warehousing": "Transportation & Warehousing",
    "Utilities": "Utilities",
    "Wholesale Trade": "Wholesale Trade"
}

def clean_name(name):
    name = name.strip()
    return INDUSTRY_MAP.get(name, name)

def get_last_n_months(n=2):
    dates = []
    today = datetime.date.today()
    curr = today.replace(day=1) - datetime.timedelta(days=1)
    for _ in range(n):
        dates.append(curr)
        curr = curr.replace(day=1) - datetime.timedelta(days=1)
    return dates

def fetch_report_with_browser(target_date):
    """Fetch ISM Services report using browser automation"""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        print("Playwright not available")
        return None
    
    month_name = target_date.strftime("%B %Y")
    month_slug = target_date.strftime("%B").lower()
    url = f"{BASE_URL}{month_slug}/"
    
    print(f"\n🌐 Fetching Services {month_name} report via browser...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2000)
            
            # Handle Disclaimer
            try:
                agree_button = page.locator("button:has-text('Agree'), button:has-text('Accept')").first
                if agree_button.is_visible(timeout=3000):
                    agree_button.click()
                    page.wait_for_timeout(1000)
            except: pass
            
            text = page.content()
            browser.close()
            return parse_services_report(text, month_name)
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def parse_ism_list(raw_text):
    text = raw_text.replace('\n', ' ').replace('&amp;', '&')
    tokens = text.split(';') if ';' in text else text.split(',')
    return [t.strip().strip('.') for t in tokens if t.strip()]

def parse_services_report(text, month_name):
    try:
        # Indices
        def get_idx(label):
            m = re.search(f"{label}.*?registered\\s+([\\d\\.]+)\\s+percent", text, re.I | re.S)
            return float(m.group(1)) if m else 0.0

        pmi_data = {
            "servicesPmi": get_idx("Services PMI"),
            "businessActivity": get_idx("Business Activity Index"),
            "newOrders": get_idx("New Orders Index"),
            "employment": get_idx("Employment Index"),
            "supplierDeliveries": get_idx("Supplier Deliveries Index"),
            "inventories": get_idx("Inventories Index"),
            "prices": get_idx("Prices Index"),
            "backlogOrders": get_idx("Backlog of Orders Index"),
            "newExportOrders": get_idx("New Export Orders Index"),
            "imports": get_idx("Imports Index"),
            "inventorySentiment": get_idx("Inventory Sentiment Index")
        }

        # Industry Growth/Contraction
        growth = []
        cont = []
        m_growth = re.search(r"industries reporting growth in .*? are: (.*?)\.", text, re.I | re.S)
        if m_growth: growth = parse_ism_list(m_growth.group(1))
        
        m_cont = re.search(r"industries reporting (?:contraction|a decrease) in .*? are: (.*?)\.", text, re.I | re.S)
        if m_cont: cont = parse_ism_list(m_cont.group(1))

        # New Orders Specific
        no_growth = []
        no_decline = []
        m_no_growth = re.search(r"industries reporting (?:growth|an increase) in New Orders .*? are: (.*?)\.", text, re.I | re.S)
        if m_no_growth: no_growth = parse_ism_list(m_no_growth.group(1))
        
        m_no_decline = re.search(r"industries reporting a (?:decrease|decline|contraction) in new orders .*? are:? (.*?)\.", text, re.I | re.S)
        if m_no_decline: no_decline = parse_ism_list(m_no_decline.group(1))

        # Comments
        comments = []
        start_comments = text.find("WHAT RESPONDENTS ARE SAYING")
        if start_comments != -1:
            end_comments = text.find("Services PMI", start_comments + 50)
            section = text[start_comments:end_comments]
            items = re.findall(r"<li>(.*?)</li>", section, re.S)
            for item in items[:10]:
                c = re.sub(r'<[^>]+>', '', item).strip()
                if ":" in c:
                    p = c.split(":", 1)
                    comments.append((clean_name(p[0]), p[1].strip().strip('"')))

        summary = f"The Services PMI registered {pmi_data['servicesPmi']} percent in {month_name}."

        return {
            "month_name": month_name, "growth": growth, "contraction": cont,
            "no_growth": no_growth, "no_decline": no_decline,
            "pmi_data": pmi_data, "comments": comments, "summary": summary
        }
    except Exception as e:
        print(f"   ✗ Parsing Error: {e}")
        return None

def update_html(updates):
    if not os.path.exists(HEATMAP_FILE): return
    with open(HEATMAP_FILE, 'r') as f: content = f.read()

    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    current_months = json.loads(months_match.group(1))
    
    data_match = re.search(r'const servicesData = ({[\s\S]*?});', content, re.DOTALL)
    data_block = data_match.group(1)
    current_data = {}
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        current_data[match.group(1)] = json.loads(match.group(2))

    for update in sorted(updates.values(), key=lambda x: datetime.datetime.strptime(x['month_name'], "%B %Y")):
        m_name = update['month_name']
        short_month = m_name[:3] + " " + m_name[-4:]
        if short_month not in current_months: current_months.append(short_month)
        idx = current_months.index(short_month)

        rank_map = {}
        for i, n in enumerate(update['growth']): rank_map[clean_name(n)] = len(update['growth']) - i
        for i, n in enumerate(update['contraction']): rank_map[clean_name(n)] = -(len(update['contraction']) - i)

        for ind in current_data:
            while len(current_data[ind]) <= idx: current_data[ind].append(0)
            current_data[ind][idx] = rank_map.get(ind, 0)

        pd = update['pmi_data']
        pmi_obj = f'{{ date: "{short_month}", servicesPmi: {pd["servicesPmi"]}, businessActivity: {pd["businessActivity"]}, newOrders: {pd["newOrders"]}, employment: {pd["employment"]}, supplierDeliveries: {pd["supplierDeliveries"]}, inventories: {pd["inventories"]}, prices: {pd["prices"]}, backlogOrders: {pd["backlogOrders"]}, newExportOrders: {pd["newExportOrders"]}, imports: {pd["imports"]}, inventorySentiment: {pd["inventorySentiment"]} }}'
        pmi_pat = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
        if pmi_pat.search(content): content = pmi_pat.sub(pmi_obj + ",", content)
        else: content = content.replace("const rawServicesPmiData = [", f"const rawServicesPmiData = [\n            {pmi_obj},", 1)

        js_g = json.dumps([clean_name(x) for x in update['no_growth']])
        js_d = json.dumps([clean_name(x) for x in update['no_decline']])
        r_pat = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
        if r_pat.search(content): content = r_pat.sub(f'"{short_month}": {{ growth: {js_g}, decline: {js_d} }},', content)
        else: content = content.replace("const ranklists = {", f'const ranklists = {{\n            "{short_month}": {{ growth: {js_g}, decline: {js_d} }},', 1)

    new_months_js = "const months = " + json.dumps(current_months) + ";"
    content = re.sub(r'const months = \[.*?\];', new_months_js, content, flags=re.DOTALL)
    data_lines = [f'            "{k}": {json.dumps(current_data[k])}' for k in sorted(current_data.keys())]
    content = re.sub(r'const servicesData = \{[\s\S]*?\};', "const servicesData = {\n" + ",\n".join(data_lines) + "\n        };", content, flags=re.DOTALL)
    
    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("✓ Services HTML Updated")

def main():
    dates = get_last_n_months(2)
    all_updates = {}
    for d in dates:
        data = fetch_report_with_browser(d)
        if data: all_updates[d.strftime("%Y-%m")] = data
    
    if all_updates:
        update_html(all_updates)
        return 0
    return 1

if __name__ == "__main__":
    sys.exit(main())
