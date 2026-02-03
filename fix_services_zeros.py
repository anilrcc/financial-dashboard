#!/usr/bin/env python3
import re
import json
import os

HEATMAP_FILE = "services_pmi.html"
COMMENTS_FILE = "services_comments.html"

# Industry Mapping
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

# Data to Inject
DATA_UPDATES = {
    "Nov 2025": {
        "pmi_data": {
            "servicesPmi": 52.6,
            "businessActivity": 54.5,
            "newOrders": 52.9,
            "employment": 48.9,
            "supplierDeliveries": 54.1,
            "inventories": 53.4,
            "prices": 65.4,
            "backlogOrders": 49.1,
            "newExportOrders": 48.7,
            "imports": 48.9,
            "inventorySentiment": 54.8
        },
        "growth": ["Retail Trade", "Arts, Entertainment & Recreation", "Accommodation & Food Services", "Wholesale Trade", "Health Care & Social Assistance", "Educational Services", "Public Administration", "Agriculture, Forestry, Fishing & Hunting", "Finance & Insurance", "Information", "Professional, Scientific & Technical Services", "Utilities"],
        "contraction": ["Construction", "Real Estate, Rental & Leasing", "Mining", "Management of Companies & Support Services", "Transportation & Warehousing"],
        "no_growth": ["Public Administration", "Arts, Entertainment & Recreation", "Retail Trade", "Other Services", "Wholesale Trade", "Health Care & Social Assistance", "Educational Services", "Transportation & Warehousing", "Finance & Insurance", "Professional, Scientific & Technical Services", "Utilities", "Information"],
        "no_decline": ["Real Estate, Rental & Leasing", "Management of Companies & Support Services", "Construction", "Accommodation & Food Services"],
        "summary": "The Services PMI registered 52.6 percent in November 2025.",
        "comments": [
            ("Construction", "Residential home sales continue to be hampered by mortgage rates... intentional pause."),
            ("Management of Companies & Support Services", "With the end of the federal government shutdown, we have resumed normal operations."),
            ("Retail Trade", "Business continues to be strong, driven by customer traffic. Pricing stable."),
            ("Wholesale Trade", "Anticipating demand to be consistent... Lumber production set to be reduced significantly.")
        ]
    },
    "Dec 2025": {
        "pmi_data": {
            "servicesPmi": 54.4,
            "businessActivity": 56.0,
            "newOrders": 57.9,
            "employment": 52.0,
            "supplierDeliveries": 51.8,
            "inventories": 54.2,
            "prices": 64.3,
            "backlogOrders": 42.6,
            "newExportOrders": 54.2,
            "imports": 50.3,
            "inventorySentiment": 54.1
        },
        "growth": ["Retail Trade", "Finance & Insurance", "Accommodation & Food Services", "Transportation & Warehousing", "Arts, Entertainment & Recreation", "Mining", "Health Care & Social Assistance", "Information", "Wholesale Trade", "Public Administration", "Utilities"],
        "contraction": ["Management of Companies & Support Services", "Professional, Scientific & Technical Services", "Agriculture, Forestry, Fishing & Hunting", "Educational Services", "Construction"],
        "no_growth": ["Mining", "Transportation & Warehousing", "Finance & Insurance", "Arts, Entertainment & Recreation", "Other Services", "Health Care & Social Assistance", "Retail Trade", "Information", "Wholesale Trade"],
        "no_decline": ["Management of Companies & Support Services", "Agriculture, Forestry, Fishing & Hunting", "Accommodation & Food Services", "Professional, Scientific & Technical Services", "Construction", "Educational Services"],
        "summary": "The Services PMI registered 54.4 percent in December 2025.",
        "comments": [
            ("Accommodation & Food Services", "Higher prices, primarily due to the impact of the administration’s trade and tariff policies."),
            ("Educational Services", "Rising labor and staffing shortages... continued inflationary pressure on supplies."),
            ("Health Care & Social Assistance", "Flu cases on the rise; respiratory equipment and supplies seeing a surge in demand."),
            ("Public Administration", "Continuing uncertainty and apprehension regarding tariffs."),
            ("Wholesale Trade", "Year-over-year growth has been coming down... government shutdown was a contributor.")
        ]
    }
}

def update_heatmap():
    if not os.path.exists(HEATMAP_FILE):
        print(f"Error: {HEATMAP_FILE} not found")
        return
    with open(HEATMAP_FILE, 'r') as f: content = f.read()

    # 1. Parse months
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    current_months = json.loads(months_match.group(1))

    # 2. Parse data
    data_match = re.search(r'const servicesData = ({[\s\S]*?});', content, re.DOTALL)
    data_block = data_match.group(1)
    current_data = {}
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        ind = match.group(1)
        current_data[ind] = json.loads(match.group(2))

    for m_label in ["Nov 2025", "Dec 2025"]:
        idx = current_months.index(m_label)
        update = DATA_UPDATES[m_label]
        
        # Rankings
        rank_map = {}
        growth = update['growth']
        contraction = update['contraction']
        num_growth = len(growth)
        for i, raw_name in enumerate(growth): rank_map[clean_name(raw_name)] = num_growth - i
        num_cont = len(contraction)
        for i, raw_name in enumerate(contraction): rank_map[clean_name(raw_name)] = -(num_cont - i)

        for ind in current_data:
            if ind in rank_map: current_data[ind][idx] = rank_map[ind]
            else: current_data[ind][idx] = 0

        # PMI Table
        pd = update['pmi_data']
        pmi_obj_str = f'{{ date: "{m_label}", servicesPmi: {pd["servicesPmi"]}, businessActivity: {pd["businessActivity"]}, newOrders: {pd["newOrders"]}, employment: {pd["employment"]}, supplierDeliveries: {pd["supplierDeliveries"]}, inventories: {pd["inventories"]}, prices: {pd["prices"]}, backlogOrders: {pd["backlogOrders"]}, newExportOrders: {pd["newExportOrders"]}, imports: {pd["imports"]}, inventorySentiment: {pd["inventorySentiment"]} }}'
        pmi_pattern = re.compile(r'\{\s*date:\s*"' + m_label + r'",.*?\}(?:,)?', re.DOTALL)
        content = pmi_pattern.sub(pmi_obj_str + ",", content)

        # Ranklists
        js_growth = json.dumps([clean_name(x) for x in update['no_growth']])
        js_decline = json.dumps([clean_name(x) for x in update['no_decline']])
        rank_pattern = re.compile(r'"' + m_label + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
        content = rank_pattern.sub(f'"{m_label}": {{ growth: {js_growth}, decline: {js_decline} }},', content)

    # Write back Main Structures
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const servicesData = {\n" + ",\n".join(data_lines) + "\n        };"
    content = re.sub(r'const servicesData = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)

    # 3. Fix summary box texts
    # Dec 2025 summary
    dec_summary = DATA_UPDATES["Dec 2025"]["summary"]
    content = re.sub(r'<h3>Key Insights \(Dec 2025\)</h3>\s*<p>.*?</p>', f'<h3>Key Insights (Dec 2025)</h3>\n        <p>{dec_summary}</p>', content, flags=re.DOTALL)
    content = re.sub(r'<h3>New Orders Key Insights \(Dec 2025\)</h3>\s*<p>.*?</p>', f'<h3>New Orders Key Insights (Dec 2025)</h3>\n        <p>{DATA_UPDATES["Dec 2025"]["summary"].replace("Services PMI", "New Orders Index")} New orders grew for the month.</p>', content, flags=re.DOTALL)
    content = re.sub(r'<span class="summary-title">Key Insights \(Dec 2025\)</span>\s*<p>.*?</p>', f'<span class="summary-title">Key Insights (Dec 2025)</span>\n        <p>{dec_summary}</p>', content, flags=re.DOTALL)

    with open(HEATMAP_FILE, 'w') as f: f.write(content)
    print("Fixed services_pmi.html")

def update_comments():
    if not os.path.exists(COMMENTS_FILE): return
    with open(COMMENTS_FILE, 'r') as f: content = f.read()

    for m_label in ["Dec 2025", "Nov 2025"]:
        update = DATA_UPDATES[m_label]
        comments = update['comments']
        block_lines = [f"## {m_label}"]
        for ind, quote in comments:
            block_lines.append(f'- **{clean_name(ind)}**: "{quote}"')
        new_block_str = "\n".join(block_lines) + "\n"

        pattern = re.compile(r'(## ' + m_label + r'.*?)(\n## |$)', re.DOTALL)
        match = pattern.search(content)
        if match:
            content = content.replace(match.group(1), new_block_str.strip() + "\n")
        else:
            content = content.replace("const rawComments = `", "const rawComments = `" + new_block_str)

    with open(COMMENTS_FILE, 'w') as f: f.write(content)
    print("Fixed services_comments.html")

if __name__ == "__main__":
    update_heatmap()
    update_comments()
