#!/usr/bin/env python3
"""
Fix January 2026 rankings - REVERSE them
First mentioned should get LOWEST rank (+1)
Last mentioned should get HIGHEST rank (+9)
"""

import re
import json

HEATMAP_FILE = "industry_heatmap.html"

def main():
    print("=" * 60)
    print("Reversing January 2026 Rankings")
    print("=" * 60)
    
    with open(HEATMAP_FILE, 'r') as f:
        content = f.read()
    
    # Parse data object
    data_match = re.search(r'const data = ({[\s\S]*?});', content, re.DOTALL)
    if not data_match:
        print("Error: Could not find 'data' object")
        return 1
    
    current_data = {}
    data_block = data_match.group(1)
    for match in re.finditer(r'"(.*?)":\s*(\[.*?\])', data_block):
        ind = match.group(1)
        arr_str = match.group(2)
        current_data[ind] = json.loads(arr_str)
    
    # Jan 2026 is at index 14
    jan_2026_idx = 14
    
    print(f"\nReversing rankings for index {jan_2026_idx} (Jan 2026)...\n")
    print("New rule: First mentioned = LOWEST rank, Last mentioned = HIGHEST rank\n")
    
    # Growth industries in ISM report order (first to last)
    growth_order = [
        "Printing & Related Support Activities",  # First = +1
        "Apparel, Leather & Allied Products",  # +2
        "Fabricated Metal Products",  # +3
        "Primary Metals",  # +4
        "Transportation Equipment",  # +5
        "Machinery",  # +6
        "Chemical Products",  # +7
        "Food, Beverage & Tobacco Products",  # +8
        "Computer & Electronic Products"  # Last = +9
    ]
    
    # Contraction industries in ISM report order (first to last)
    contraction_order = [
        "Textile Mills",  # First = -1
        "Wood Products",  # -2
        "Nonmetallic Mineral Products",  # -3
        "Electrical Equipment, Appliances & Comp",  # -4
        "Petroleum & Coal Products",  # -5
        "Plastics & Rubber Products",  # -6
        "Furniture & Related Products",  # -7
        "Miscellaneous Manufacturing"  # Last = -8
    ]
    
    # Apply reversed growth rankings (first = lowest)
    for i, industry in enumerate(growth_order):
        rank = i + 1  # First gets +1, last gets +9
        if industry in current_data:
            old_rank = current_data[industry][jan_2026_idx]
            current_data[industry][jan_2026_idx] = rank
            print(f"  {industry}: {old_rank} → {rank}")
    
    print()
    
    # Apply reversed contraction rankings (first = least severe)
    for i, industry in enumerate(contraction_order):
        rank = -(i + 1)  # First gets -1, last gets -8
        if industry in current_data:
            old_rank = current_data[industry][jan_2026_idx]
            current_data[industry][jan_2026_idx] = rank
            print(f"  {industry}: {old_rank} → {rank}")
    
    # Rebuild data object
    data_lines = []
    for k in sorted(current_data.keys()):
        data_lines.append(f'            "{k}": {json.dumps(current_data[k])}')
    new_data_js = "const data = {\n" + ",\n".join(data_lines) + "\n        };"
    
    # Replace in content
    content = re.sub(r'const data = \{[\s\S]*?\};', new_data_js, content, flags=re.DOTALL)
    
    # Write back
    with open(HEATMAP_FILE, 'w') as f:
        f.write(content)
    
    print(f"\n✓ Updated {HEATMAP_FILE}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
