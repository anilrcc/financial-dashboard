#!/usr/bin/env python3
"""
Manual update script for February 2026 ISM Manufacturing and Services PMI data.
Extracted from the February 2026 PDF reports.
"""

import re
import json
import datetime
import os

# --- Configuration ---
MANUFACTURING_HEATMAP = "industry_heatmap.html"
MANUFACTURING_COMMENTS = "industry_comments.html"
SERVICES_HEATMAP = "services_pmi.html"
SERVICES_COMMENTS = "services_comments.html"
INDEX_FILE = "index.html"

# Industry mapping for Manufacturing
MFG_INDUSTRY_MAP = {
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

# Industry mapping for Services
SERVICES_INDUSTRY_MAP = {
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

def clean_mfg_name(name):
    return MFG_INDUSTRY_MAP.get(name.strip(), name.strip())

def clean_services_name(name):
    return SERVICES_INDUSTRY_MAP.get(name.strip(), name.strip())

# --- FEBRUARY 2026 MANUFACTURING DATA ---
FEBRUARY_2026_MFG_DATA = {
    "month_name": "February 2026",
    "growth": [
        "Printing & Related Support Activities", "Textile Mills", "Primary Metals", 
        "Nonmetallic Mineral Products", "Chemical Products", "Machinery", 
        "Electrical Equipment, Appliances & Components", "Fabricated Metal Products", 
        "Transportation Equipment", "Plastics & Rubber Products", 
        "Miscellaneous Manufacturing", "Computer & Electronic Products"
    ],
    "contraction": [
        "Apparel, Leather & Allied Products", "Furniture & Related Products", 
        "Petroleum & Coal Products", "Wood Products", "Food, Beverage & Tobacco Products"
    ],
    "no_growth": [ # New Orders Growth
        "Printing & Related Support Activities", "Nonmetallic Mineral Products", 
        "Computer & Electronic Products", "Chemical Products", "Primary Metals", 
        "Wood Products", "Plastics & Rubber Products", "Electrical Equipment, Appliances & Components", 
        "Machinery", "Fabricated Metal Products", "Transportation Equipment", "Miscellaneous Manufacturing"
    ],
    "no_decline": [ # New Orders Decline
        "Apparel, Leather & Allied Products", "Furniture & Related Products"
    ],
    "pmi_data": {
        "pmi": 52.4,
        "newOrders": 55.8,
        "production": 53.5,
        "employment": 48.8,
        "supplierDel": 55.1,
        "inv": 48.8,
        "custInv": 38.8,
        "prices": 70.5,
        "backlog": 56.6,
        "export": 50.3,
        "imports": 54.9,
        "trend": "Expansion"
    },
    "summary": "Economic activity in the manufacturing sector expanded in February for the second straight month but only the third time in 40 months.",
    "comments": [
        ("Transportation Equipment", "Today, American produced commodities like steel and aluminum are the highest priced in the world, by far. Hence, the Section 232 tariff policy is having the exact opposite effect of their intention..."),
        ("Chemical Products", "Economic activity seems to be also challenging for this year. Some recovery in certain sectors... Cost discipline is the priority."),
        ("Chemical Products", "January sales continued to provide positive indications for growth opportunities. Data center, health care, and food and beverages remain positive growth areas."),
        ("Petroleum & Coal Products", "South American instability has begun to be a factor for our suppliers and inventory management."),
        ("Miscellaneous Manufacturing", "Pricing for outside purchases has stabilized. We are spending significant effort to work with our supply base to mitigate tariff impacts."),
        ("Computer & Electronic Products", "Overall orders and supply footprint are improving. As we review customer demand, we are also taking several categories of established materials and supplies out to RFP for review and cost improvements..."),
        ("Computer & Electronic Products", "Continue to be impacted by tariffs. Seeing metals prices rise too. Business is steady, but domestic growth is slower than expected."),
        ("Electrical Equipment, Appliances & Components", "Business was slow in January. Many orders pulled into end of 2025 to meet revenue goals. Order book is strong going forward."),
        ("Machinery", "Tariff policy changes affect total acquisition costs and purchasing source decisions. So far this year, tariff instability still exists."),
        ("Fabricated Metal Products", "Business is improving by the week. Backlog is growing, and new opportunities are everywhere.")
    ]
}

# --- FEBRUARY 2026 SERVICES DATA ---
FEBRUARY_2026_SERVICES_DATA = {
    "month_name": "February 2026",
    "growth": [
        "Mining", "Information", "Real Estate, Rental & Leasing", "Agriculture, Forestry, Fishing & Hunting", 
        "Accommodation & Food Services", "Wholesale Trade", "Finance & Insurance", "Utilities", 
        "Professional, Scientific & Technical Services", "Construction", "Management of Companies & Support Services", 
        "Public Administration", "Health Care & Social Assistance", "Educational Services"
    ],
    "contraction": [
        "Retail Trade", "Arts, Entertainment & Recreation", "Transportation & Warehousing"
    ],
    "no_growth": [ # New Orders Growth
        "Mining", "Information", "Real Estate, Rental & Leasing", "Construction", "Wholesale Trade", 
        "Finance & Insurance", "Accommodation & Food Services", "Agriculture, Forestry, Fishing & Hunting", 
        "Other Services", "Utilities", "Professional, Scientific & Technical Services", "Public Administration", 
        "Educational Services", "Management of Companies & Support Services", "Health Care & Social Assistance"
    ],
    "no_decline": [ # New Orders Decline
        "Retail Trade", "Arts, Entertainment & Recreation"
    ],
    "pmi_data": {
        "servicesPmi": 56.1,
        "businessActivity": 59.9,
        "newOrders": 58.6,
        "employment": 51.8,
        "supplierDeliveries": 53.9,
        "inventories": 56.4,
        "prices": 63.0,
        "backlogOrders": 55.9,
        "newExportOrders": 57.2,
        "imports": 51.8,
        "inventorySentiment": 55.3
    },
    "summary": "The Services PMI registered 56.1 percent, its 20th month in a row in expansion territory and the highest since July 2022.",
    "no_summary": "The New Orders Index registered 58.6 percent in February. New orders grew for the month and registered the highest level since early 2024.",
    "comments": [
        ("Accommodation & Food Services", "India tariffs are anticipated to provide some measure of cost relief once current inventory levels are worked through. At a high level, we are addressing price/value perception which continues to drive negative sales impact."),
        ("Agriculture, Forestry, Fishing & Hunting", "Our industry seems to have adapted to the tariffs. The costs are embedded into the import cost the company has to shoulder."),
        ("Construction", "Residential homebuilding continues to lag due to affordability and interest rate issues... More material cost increases have rolled in for beginning of the second quarter, so margins continue to be reduced."),
        ("Educational Services", "Higher education institutions are operating cautiously due to enrollment fluctuations and uncertainty in state and federal funding and name, image and likeness licensing."),
        ("Mining", "Tariff volatility and shifting bilateral trade agreements are materially impacting our purchasing operations. Changes in U.S. semiconductor supply constraints continue to pressure component pricing and availability."),
        ("Real Estate, Rental & Leasing", "The business climate remains solid overall, but significant unknown risks from further potential tariff actions by the U.S. government are dampening business investment."),
        ("Retail Trade", "Due to random-access memory shortages, we are seeing increased cost and lead times from key technology providers. Quotes that were normally secure for 90 days are now 30 days or less."),
        ("Transportation & Warehousing", "Transportation/truck capacity has been extremely tight, causing rates to spike 30 percent to 40 percent. Some of this can be attributed to the weather..."),
        ("Utilities", "Mid-first quarter business conditions are good. The unseasonable cold weather has helped to increase demand and boost revenues."),
        ("Wholesale Trade", "Overall, our business performance in January and February has been solid (minus some winter storm hurdles). Our upstream oil and gas business has stalled for two years and is not supporting our growth.")
    ]
}

def update_mfg_html(data):
    if not os.path.exists(MANUFACTURING_HEATMAP): return False
    with open(MANUFACTURING_HEATMAP, 'r') as f: content = f.read()

    short_month = data['month_name'][:3] + " " + data['month_name'][-4:]
    
    # Update months array
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match: return False
    current_months = json.loads(months_match.group(1))
    if short_month not in current_months: current_months.append(short_month)
    idx = current_months.index(short_month)

    # Update data object (ranks)
    data_match = re.search(r'const data = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match: return False
    current_data = {}
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_match.group(1)):
        current_data[match.group(1)] = json.loads(match.group(2))

    rank_map = {}
    for i, name in enumerate(data['growth']): rank_map[clean_mfg_name(name)] = len(data['growth']) - i
    for i, name in enumerate(data['contraction']): rank_map[clean_mfg_name(name)] = -(len(data['contraction']) - i)

    for ind in current_data:
        while len(current_data[ind]) <= idx: current_data[ind].append(0)
        current_data[ind][idx] = rank_map.get(ind, 0)

    # Update rawPmiData
    pd = data['pmi_data']
    pmi_obj = f'{{ date: "{short_month}", pmi: {pd["pmi"]}, newOrders: {pd["newOrders"]}, production: {pd["production"]}, employment: {pd["employment"]}, supplierDel: {pd["supplierDel"]}, inv: {pd["inv"]}, custInv: {pd["custInv"]}, prices: {pd["prices"]}, backlog: {pd["backlog"]}, export: {pd["export"]}, imports: {pd["imports"]}, trend: "{pd["trend"]}" }}'
    pmi_pattern = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
    if pmi_pattern.search(content): content = pmi_pattern.sub(pmi_obj + ",", content)
    else: content = content.replace("const rawPmiData = [", f"const rawPmiData = [\n            {pmi_obj},", 1)

    # Update ranklists
    js_growth = json.dumps([clean_mfg_name(x) for x in data['no_growth']])
    js_decline = json.dumps([clean_mfg_name(x) for x in data['no_decline']])
    rank_pattern = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
    if rank_pattern.search(content):
        content = rank_pattern.sub(f'"{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', content)
    else:
        content = content.replace("const ranklists = {", f'const ranklists = {{\n            "{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', 1)

    # Write structures back
    content = re.sub(r'const months = \[.*?\];', f"const months = {json.dumps(current_months)};", content, flags=re.DOTALL)
    data_lines = [f'            "{k}": {json.dumps(current_data[k])}' for k in sorted(current_data.keys())]
    content = re.sub(r'const data = \{[\s\S]*?\};', "const data = {\n" + ",\n".join(data_lines) + "\n        };", content, flags=re.DOTALL)
    
    with open(MANUFACTURING_HEATMAP, 'w') as f: f.write(content)
    print(f"✓ Updated {MANUFACTURING_HEATMAP}")
    return True

def update_services_html(data):
    if not os.path.exists(SERVICES_HEATMAP): return False
    with open(SERVICES_HEATMAP, 'r') as f: content = f.read()

    short_month = data['month_name'][:3] + " " + data['month_name'][-4:]
    
    # Update months array
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match: return False
    current_months = json.loads(months_match.group(1))
    if short_month not in current_months: current_months.append(short_month)
    idx = current_months.index(short_month)

    # Update servicesData object (ranks)
    data_match = re.search(r'const servicesData = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match: return False
    current_data = {}
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_match.group(1)):
        current_data[match.group(1)] = json.loads(match.group(2))

    rank_map = {}
    for i, name in enumerate(data['growth']): rank_map[clean_services_name(name)] = len(data['growth']) - i
    for i, name in enumerate(data['contraction']): rank_map[clean_services_name(name)] = -(len(data['contraction']) - i)

    for ind in current_data:
        while len(current_data[ind]) <= idx: current_data[ind].append(0)
        current_data[ind][idx] = rank_map.get(ind, 0)

    # Update rawServicesPmiData
    pd = data['pmi_data']
    pmi_obj = f'{{ date: "{short_month}", servicesPmi: {pd["servicesPmi"]}, businessActivity: {pd["businessActivity"]}, newOrders: {pd["newOrders"]}, employment: {pd["employment"]}, supplierDeliveries: {pd["supplierDeliveries"]}, inventories: {pd["inventories"]}, prices: {pd["prices"]}, backlogOrders: {pd["backlogOrders"]}, newExportOrders: {pd["newExportOrders"]}, imports: {pd["imports"]}, inventorySentiment: {pd["inventorySentiment"]} }}'
    pmi_pattern = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
    if pmi_pattern.search(content): content = pmi_pattern.sub(pmi_obj + ",", content)
    else: content = content.replace("const rawServicesPmiData = [", f"const rawServicesPmiData = [\n            {pmi_obj},", 1)

    # Update ranklists
    js_growth = json.dumps([clean_services_name(x) for x in data['no_growth']])
    js_decline = json.dumps([clean_services_name(x) for x in data['no_decline']])
    rank_pattern = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
    if rank_pattern.search(content):
        content = rank_pattern.sub(f'"{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', content)
    else:
        content = content.replace("const ranklists = {", f'const ranklists = {{\n            "{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', 1)

    # Update summary boxes
    l_summary = data['summary']
    l_no_summary = data['no_summary']
    
    summary_pattern = r'(<div id="services-pmi-survey-insights"[^>]*>)\s*<span class="summary-title">Key Insights \(.*?\)</span>\s*<p>.*?</p>'
    content = re.sub(summary_pattern, f'\\1\n        <span class="summary-title">Key Insights ({short_month})</span>\n        <p>{l_summary}</p>', content, flags=re.DOTALL)

    main_sum_pat = r'(<div id="main-summary-box"[^>]*>)\s*<h3>Key Insights \(.*?\)</h3>\s*<p>.*?</p>'
    content = re.sub(main_sum_pat, f'\\1\n        <h3>Key Insights ({short_month})</h3>\n        <p>{l_summary}</p>', content, flags=re.DOTALL)

    no_sum_pat = r'(<div id="new-orders-summary-box"[^>]*>)\s*<h3>New Orders Key Insights \(.*?\)</h3>\s*<p>.*?</p>'
    content = re.sub(no_sum_pat, f'\\1\n        <h3>New Orders Key Insights ({short_month})</h3>\n        <p>{l_no_summary}</p>', content, flags=re.DOTALL)

    # Update title date range
    start_m = current_months[0]
    end_m = current_months[-1]
    new_title = f"ISM Services Industry Trends ({start_m.split()[0]} '{start_m.split()[1][2:]} - {end_m.split()[0]} '{end_m.split()[1][2:]})"
    content = re.sub(r'<h1>ISM Services Industry Trends \(.*?\)</h1>', f'<h1>{new_title}</h1>', content)

    # Write structures back
    content = re.sub(r'const months = \[.*?\];', f"const months = {json.dumps(current_months)};", content, flags=re.DOTALL)
    data_lines = [f'            "{k}": {json.dumps(current_data[k])}' for k in sorted(current_data.keys())]
    content = re.sub(r'const servicesData = \{[\s\S]*?\};', "const servicesData = {\n" + ",\n".join(data_lines) + "\n        };", content, flags=re.DOTALL)
    
    with open(SERVICES_HEATMAP, 'w') as f: f.write(content)
    print(f"✓ Updated {SERVICES_HEATMAP}")
    return True

def update_comments_file(filename, data, is_mfg=True):
    if not os.path.exists(filename): return False
    with open(filename, 'r') as f: content = f.read()

    short_month = data['month_name'][:3] + " " + data['month_name'][-4:]
    block_lines = [f"## {short_month}"]
    for ind, quote in data['comments']:
        name = clean_mfg_name(ind) if is_mfg else clean_services_name(ind)
        block_lines.append(f'- **{name}**: "{quote}"')
    new_block = "\n".join(block_lines) + "\n"

    pattern = re.compile(r'(## ' + short_month + r'.*?)(\n## |$)', re.DOTALL)
    if pattern.search(content): content = pattern.sub(new_block, content)
    else: content = content.replace("const rawComments = `", f"const rawComments = `{new_block}")

    with open(filename, 'w') as f: f.write(content)
    print(f"✓ Updated {filename}")
    return True

def update_index():
    if not os.path.exists(INDEX_FILE): return
    with open(INDEX_FILE, 'r') as f: content = f.read()
    today_str = datetime.date.today().strftime("%b %d, %Y")
    
    # Update Mfg card
    content = re.compile(r'(class="card mfg".*?<span>)(Macro Indicator\s*•\s*)([^<]*?)(</span>)', re.DOTALL).sub(f"\\1Macro Indicator • {today_str}\\4", content)
    # Update Services card
    content = re.compile(r'(class="card services".*?<span>)(Macro Indicator\s*•\s*)([^<]*?)(</span>)', re.DOTALL).sub(f"\\1Macro Indicator • {today_str}\\4", content)
    
    with open(INDEX_FILE, 'w') as f: f.write(content)
    print(f"✓ Updated {INDEX_FILE}")

def main():
    print("Updating ISM PMI Data for February 2026...")
    update_mfg_html(FEBRUARY_2026_MFG_DATA)
    update_comments_file(MANUFACTURING_COMMENTS, FEBRUARY_2026_MFG_DATA, True)
    update_services_html(FEBRUARY_2026_SERVICES_DATA)
    update_comments_file(SERVICES_COMMENTS, FEBRUARY_2026_SERVICES_DATA, False)
    update_index()
    print("Done!")

if __name__ == "__main__":
    main()
