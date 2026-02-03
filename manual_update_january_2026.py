#!/usr/bin/env python3
"""
Manual update script for January 2026 ISM Manufacturing PMI data
Extracted from browser since automated scraping is blocked by disclaimer modal
"""

import re
import json
import datetime
import os

# --- Configuration ---
HEATMAP_FILE = "industry_heatmap.html"
COMMENTS_FILE = "industry_comments.html"

# Industry mapping (same as update_ism.py)
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

# --- JANUARY 2026 DATA (manually extracted from browser) ---
JANUARY_2026_DATA = {
    "month_name": "January 2026",
    "growth": [
        "Printing & Related Support Activities",
        "Apparel, Leather & Allied Products",
        "Fabricated Metal Products",
        "Primary Metals",
        "Transportation Equipment",
        "Machinery",
        "Chemical Products",
        "Food, Beverage & Tobacco Products",
        "Computer & Electronic Products"
    ],
    "contraction": [
        "Textile Mills",
        "Wood Products",
        "Nonmetallic Mineral Products",
        "Electrical Equipment, Appliances & Components",
        "Petroleum & Coal Products",
        "Plastics & Rubber Products",
        "Furniture & Related Products",
        "Miscellaneous Manufacturing"
    ],
    "no_growth": [  # New Orders Growth
        "Apparel, Leather & Allied Products",
        "Printing & Related Support Activities",
        "Primary Metals",
        "Machinery",
        "Transportation Equipment",
        "Chemical Products",
        "Fabricated Metal Products",
        "Food, Beverage & Tobacco Products"
    ],
    "no_decline": [  # New Orders Decline
        "Wood Products",
        "Nonmetallic Mineral Products",
        "Textile Mills",
        "Paper Products",
        "Electrical Equipment, Appliances & Components",
        "Miscellaneous Manufacturing",
        "Computer & Electronic Products"
    ],
    "pmi_data": {
        "pmi": 52.6,
        "newOrders": 57.1,
        "production": 55.9,
        "employment": 48.1,
        "supplierDel": 54.4,
        "inv": 47.6,
        "custInv": 38.7,
        "prices": 59.0,
        "backlog": 51.6,
        "export": 50.2,
        "imports": 50.0,
        "trend": "Expansion"
    },
    "summary": "Economic activity in the manufacturing sector expanded in January 2026 for the first time in 12 months.",
    "comments": [
        ("Transportation Equipment", "'Hope' has been word of the year... buyers continue to stand on the sidelines... uncertainty brought about by this administration..."),
        ("Machinery", "Latest tariff threats on the European Union will have a huge negative impact on our profit..."),
        ("Computer & Electronic Products", "Another round of emotionally charged tariffs seems imminent... Business conditions remain uncertain. The Supreme Court tariff decision looms."),
        ("Chemical Products", "Moving manufacturing from China to Mexico — which will now impose tariffs on parts made in China."),
        ("Fabricated Metal Products", "Confused and uninformed tariff policies continue to plague small companies, making long-term planning pointless."),
        ("Apparel, Leather & Allied Products", "Tariff impacts on our financial performance last year cannot be overstated... we will continue our multi-country sourcing approach... outside of China.")
    ]
}

def update_html_with_data(data):
    """Update the heatmap HTML file with new data"""
    if not os.path.exists(HEATMAP_FILE):
        print(f"Error: {HEATMAP_FILE} not found")
        return False
    
    with open(HEATMAP_FILE, 'r') as f:
        content = f.read()
    
    m_name = data['month_name']
    short_month = m_name[:3] + " " + m_name[-4:]  # "Jan 2026"
    
    print(f"\nUpdating {HEATMAP_FILE} with {short_month} data...")
    
    # 1. Parse and update 'months' array
    months_match = re.search(r'const months = (\[.*?\]);', content, re.DOTALL)
    if not months_match:
        print("Error: Could not find 'months' array")
        return False
    
    current_months = json.loads(months_match.group(1))
    
    if short_month not in current_months:
        current_months.append(short_month)
        print(f"  ✓ Added {short_month} to months array")
    else:
        print(f"  ℹ {short_month} already in months array")
    
    idx = current_months.index(short_month)
    
    # 2. Parse and update 'data' object
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
    
    # Calculate ranks
    rank_map = {}
    growth = data['growth']
    contraction = data['contraction']
    
    num_growth = len(growth)
    for i, raw_name in enumerate(growth):
        rank_map[clean_name(raw_name)] = num_growth - i
    
    num_cont = len(contraction)
    for i, raw_name in enumerate(contraction):
        rank_map[clean_name(raw_name)] = -(num_cont - i)
    
    # Update current_data arrays
    for ind in current_data:
        while len(current_data[ind]) <= idx:
            current_data[ind].append(0)
        
        if ind in rank_map:
            current_data[ind][idx] = rank_map[ind]
        else:
            current_data[ind][idx] = 0
    
    print(f"  ✓ Updated industry rankings for {short_month}")
    
    # 3. Update rawPmiData
    pd = data['pmi_data']
    pmi_obj_str = f'{{ date: "{short_month}", pmi: {pd["pmi"]}, newOrders: {pd["newOrders"]}, production: {pd["production"]}, employment: {pd["employment"]}, supplierDel: {pd["supplierDel"]}, inv: {pd["inv"]}, custInv: {pd["custInv"]}, prices: {pd["prices"]}, backlog: {pd["backlog"]}, export: {pd["export"]}, imports: {pd["imports"]}, trend: "{pd["trend"]}" }}'
    
    pmi_pattern = re.compile(r'\{\s*date:\s*"' + short_month + r'",.*?\}(?:,)?', re.DOTALL)
    if pmi_pattern.search(content):
        content = pmi_pattern.sub(pmi_obj_str + ",", content)
        print(f"  ✓ Updated PMI data for {short_month}")
    else:
        content = content.replace("const rawPmiData = [", "const rawPmiData = [\n            " + pmi_obj_str + ",", 1)
        print(f"  ✓ Added new PMI data for {short_month}")
    
    # 4. Update ranklists
    no_growth = data['no_growth']
    no_decline = data['no_decline']
    js_growth = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_growth]) + "]"
    js_decline = "[" + ", ".join([f'"{clean_name(x)}"' for x in no_decline]) + "]"
    rank_entry = f'\n            "{short_month}": {{\n                growth: {js_growth},\n                decline: {js_decline}\n            }},'
    
    rank_pattern = re.compile(r'"' + short_month + r'":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
    if rank_pattern.search(content):
        content = rank_pattern.sub(f'"{short_month}": {{ growth: {js_growth}, decline: {js_decline} }},', content)
        print(f"  ✓ Updated new orders rankings for {short_month}")
    else:
        content = content.replace("const ranklists = {", "const ranklists = {" + rank_entry, 1)
        print(f"  ✓ Added new orders rankings for {short_month}")
    
    # 5. Write back updated structures
    new_months_js = "const months = " + json.dumps(current_months) + ";"
    content = re.sub(r'const months = \[.*?\];', new_months_js, content, flags=re.DOTALL)
    
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const data = {\n" + ",\n".join(data_lines) + "\n        };"
    content = re.sub(r'const data = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)
    
    # Cleanup double commas
    content = content.replace(",,", ",")
    
    # Update meta version
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
    if 'name="deployment-version"' in content:
        content = re.sub(r'<meta name="deployment-version" content=".*?">', 
                         f'<meta name="deployment-version" content="manual-update-{timestamp}">', 
                         content)
    
    with open(HEATMAP_FILE, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Saved {HEATMAP_FILE}")
    return True

def update_comments(data):
    """Update the comments HTML file with new data"""
    if not os.path.exists(COMMENTS_FILE):
        print(f"Warning: {COMMENTS_FILE} not found, skipping comments update")
        return False
    
    with open(COMMENTS_FILE, 'r') as f:
        content = f.read()
    
    m_name = data['month_name']
    short_month = m_name[:3] + " " + m_name[-4:]
    comments = data['comments']
    
    if not comments:
        print(f"  ℹ No comments to add for {short_month}")
        return True
    
    print(f"\nUpdating {COMMENTS_FILE} with {short_month} comments...")
    
    # Build new block
    block_lines = [f"## {short_month}"]
    for ind, quote in comments:
        block_lines.append(f'- **{clean_name(ind)}**: "{quote}"')
    new_block_str = "\n".join(block_lines) + "\n"
    
    # Check if block exists
    pattern = re.compile(r'(## ' + short_month + r'.*?)(\n## |$)', re.DOTALL)
    match = pattern.search(content)
    
    if match:
        content = content.replace(match.group(1), new_block_str.strip() + "\n")
        print(f"  ✓ Updated comments for {short_month}")
    else:
        content = content.replace("const rawComments = `", "const rawComments = `" + new_block_str)
        print(f"  ✓ Added new comments for {short_month}")
    
    with open(COMMENTS_FILE, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Saved {COMMENTS_FILE}")
    return True

def main():
    print("=" * 60)
    print("Manual ISM Manufacturing PMI Update - January 2026")
    print("=" * 60)
    
    success = update_html_with_data(JANUARY_2026_DATA)
    if success:
        update_comments(JANUARY_2026_DATA)
        print("\n" + "=" * 60)
        print("✓ Update Complete!")
        print("=" * 60)
        print(f"\nJanuary 2026 PMI: {JANUARY_2026_DATA['pmi_data']['pmi']}% (Expansion)")
        print(f"  - New Orders: {JANUARY_2026_DATA['pmi_data']['newOrders']}%")
        print(f"  - Production: {JANUARY_2026_DATA['pmi_data']['production']}%")
        print(f"  - Employment: {JANUARY_2026_DATA['pmi_data']['employment']}%")
    else:
        print("\n✗ Update failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
