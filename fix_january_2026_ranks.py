#!/usr/bin/env python3
"""
REVERT the incorrect fix - restore January 2026 to original rankings
All months use: first mentioned = highest rank
"""

import re
import json

HEATMAP_FILE = "industry_heatmap.html"

# ORIGINAL correct ranking for Jan 2026 (first mentioned = highest)
# Growth: first mentioned should get highest rank
GROWTH_CORRECT_ORDER = [
    "Printing & Related Support Activities",  # Should be +9 (first = highest)
    "Apparel, Leather & Allied Products",  # Should be +8
    "Fabricated Metal Products",  # Should be +7
    "Primary Metals",  # Should be +6
    "Transportation Equipment",  # Should be +5
    "Machinery",  # Should be +4
    "Chemical Products",  # Should be +3
    "Food, Beverage & Tobacco Products",  # Should be +2
    "Computer & Electronic Products"  # Should be +1 (last = lowest)
]

# Contraction: first mentioned should get highest negative rank (most severe)
CONTRACTION_CORRECT_ORDER = [
    "Textile Mills",  # Should be -8 (first = most severe)
    "Wood Products",  # Should be -7
    "Nonmetallic Mineral Products",  # Should be -6
    "Electrical Equipment, Appliances & Comp",  # Should be -5
    "Petroleum & Coal Products",  # Should be -4
    "Plastics & Rubber Products",  # Should be -3
    "Furniture & Related Products",  # Should be -2
    "Miscellaneous Manufacturing"  # Should be -1 (last = least severe)
]

def main():
    print("=" * 60)
    print("REVERTING January 2026 Rankings to Original")
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
    
    # Jan 2026 is at index 14 (15th month, 0-indexed)
    jan_2026_idx = 14
    
    print(f"\nRestoring rankings for index {jan_2026_idx} (Jan 2026)...\n")
    print("Rule: First mentioned = Highest rank\n")
    
    # Apply correct growth rankings (first = highest)
    for i, industry in enumerate(GROWTH_CORRECT_ORDER):
        rank = len(GROWTH_CORRECT_ORDER) - i  # First gets highest
        if industry in current_data:
            old_rank = current_data[industry][jan_2026_idx]
            current_data[industry][jan_2026_idx] = rank
            print(f"  {industry}: {old_rank} → {rank}")
    
    print()
    
    # Apply correct contraction rankings (first = most severe)
    for i, industry in enumerate(CONTRACTION_CORRECT_ORDER):
        rank = -(len(CONTRACTION_CORRECT_ORDER) - i)  # First gets highest negative
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
    
    print(f"\n✓ Restored {HEATMAP_FILE}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main())
