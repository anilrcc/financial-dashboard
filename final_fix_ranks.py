#!/usr/bin/env python3
"""
Final precise fix for January 2026 rankings.
Ensuring:
- Printing (first mentioned) = +9
- Computer (last mentioned) = +1
- All other industries in between follow the descending order.
- Contraction follows first mentioned = most negative (-8).
"""

import re
import json

HEATMAP_FILE = "industry_heatmap.html"

# Precise Order for Jan 2026 Overall Rankings (15th month, index 14)
CORRECT_HEATMAP_RANKS = {
    "Printing & Related Support Activities": 9,
    "Apparel, Leather & Allied Products": 8,
    "Fabricated Metal Products": 7,
    "Primary Metals": 6,
    "Transportation Equipment": 5,
    "Machinery": 4,
    "Chemical Products": 3,
    "Food, Beverage & Tobacco Products": 2,
    "Computer & Electronic Products": 1,
    "Textile Mills": -8,
    "Wood Products": -7,
    "Nonmetallic Mineral Products": -6,
    "Electrical Equipment, Appliances & Comp": -5,
    "Petroleum & Coal Products": -4,
    "Plastics & Rubber Products": -3,
    "Furniture & Related Products": -2,
    "Miscellaneous Manufacturing": -1,
    "Paper Products": 0
}

# Precise Order for New Orders Ranklists (used for the second table)
JAN_2026_NEW_ORDERS = {
    "growth": [
        "Printing & Related Support Activities",
        "Apparel, Leather & Allied Products",
        "Fabricated Metal Products",
        "Primary Metals",
        "Transportation Equipment",
        "Machinery",
        "Chemical Products",
        "Food, Beverage & Tobacco Products"
    ],
    "decline": [
        "Wood Products",
        "Nonmetallic Mineral Products",
        "Textile Mills",
        "Paper Products",
        "Electrical Equipment, Appliances & Comp",
        "Miscellaneous Manufacturing",
        "Computer & Electronic Products"
    ]
}

def main():
    print("Applying precise January 2026 rankings...")
    
    with open(HEATMAP_FILE, 'r') as f:
        content = f.read()

    # 1. Update heatmap data object (const data = { ... })
    data_match = re.search(r'const data = ({[\s\S]*?});', content, re.DOTALL)
    if data_match:
        data_block = data_match.group(1)
        current_data = {}
        for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
            ind = match.group(1)
            arr = json.loads(match.group(2))
            if ind in CORRECT_HEATMAP_RANKS:
                # Ensure array is long enough (index 14)
                while len(arr) <= 14:
                    arr.append(0)
                arr[14] = CORRECT_HEATMAP_RANKS[ind]
            current_data[ind] = arr
        
        # Build new data block
        data_lines = []
        for k in sorted(current_data.keys()):
            data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
        new_data_js = "const data = {\n" + ",\n".join(data_lines) + "\n        };"
        content = re.sub(r'const data = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)

    # 2. Update ranklists for January 2026
    # Pattern to find the ranklists entry for Jan 2026
    rank_pattern = re.compile(r'"Jan 2026":\s*\{\s*growth:.*?decline:.*?\}(?:,)?', re.DOTALL)
    new_rank_entry = f'"Jan 2026": {{\n                growth: {json.dumps(JAN_2026_NEW_ORDERS["growth"])},\n                decline: {json.dumps(JAN_2026_NEW_ORDERS["decline"])}\n            }},'
    
    if rank_pattern.search(content):
        content = rank_pattern.sub(new_rank_entry, content)
    else:
        # Prepend if not found
        content = content.replace("const ranklists = {", "const ranklists = {\n            " + new_rank_entry, 1)

    with open(HEATMAP_FILE, 'w') as f:
        f.write(content)
    
    print("✓ Rankings fixed for Jan 2026.")

if __name__ == "__main__":
    main()
