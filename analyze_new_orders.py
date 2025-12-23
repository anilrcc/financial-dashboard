#!/usr/bin/env python3
"""Analyze New Orders rank data trends"""

months = [
    "Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025",
    "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
]

# This is the ranklists data from the HTML
ranklists = {
    "Nov 2025": {
        "growth": ["Electrical Equipment, Appliances & Comp", "Computer & Electronic Products", "Machinery", "Miscellaneous Manufacturing", "Food, Beverage & Tobacco Products", "Primary Metals"],
        "decline": ["Wood Products", "Textile Mills", "Apparel, Leather & Allied Products", "Paper Products", "Fabricated Metal Products", "Petroleum & Coal Products", "Nonmetallic Mineral Products", "Transportation Equipment", "Chemical Products"]
    },
    "Oct 2025": {
        "growth": ["Primary Metals", "Plastics & Rubber Products", "Fabricated Metal Products", "Transportation Equipment"],
        "decline": ["Apparel, Leather & Allied Products", "Textile Mills", "Paper Products", "Petroleum & Coal Products", "Furniture & Related Products", "Nonmetallic Mineral Products", "Miscellaneous Manufacturing", "Chemical Products", "Computer & Electronic Products", "Machinery", "Electrical Equipment, Appliances & Comp"]
    },
    "Sep 2025": {
        "growth": ["Textile Mills", "Furniture & Related Products", "Fabricated Metal Products", "Miscellaneous Manufacturing", "Primary Metals", "Electrical Equipment, Appliances & Comp"],
        "decline": ["Wood Products", "Nonmetallic Mineral Products", "Plastics & Rubber Products", "Paper Products", "Transportation Equipment", "Computer & Electronic Products", "Machinery", "Food, Beverage & Tobacco Products", "Chemical Products"]
    },
    "Aug 2025": {
        "growth": ["Textile Mills", "Apparel, Leather & Allied Products", "Nonmetallic Mineral Products", "Food, Beverage & Tobacco Products", "Petroleum & Coal Products", "Miscellaneous Manufacturing", "Primary Metals"],
        "decline": ["Paper Products", "Wood Products", "Plastics & Rubber Products", "Fabricated Metal Products", "Transportation Equipment", "Machinery"]
    },
    "Jul 2025": {
        "growth": ["Apparel, Leather & Allied Products", "Plastics & Rubber Products", "Primary Metals", "Miscellaneous Manufacturing"],
        "decline": ["Fabricated Metal Products"]
    },
    "Jun 2025": {
        "growth": ["Apparel, Leather & Allied Products", "Petroleum & Coal Products", "Furniture & Related Products", "Nonmetallic Mineral Products", "Miscellaneous Manufacturing", "Food, Beverage & Tobacco Products", "Computer & Electronic Products"],
        "decline": []
    },
    "May 2025": {
        "growth": ["Plastics & Rubber Products", "Nonmetallic Mineral Products", "Petroleum & Coal Products", "Furniture & Related Products", "Electrical Equipment, Appliances & Comp", "Fabricated Metal Products", "Machinery"],
        "decline": ["Paper Products", "Wood Products", "Food, Beverage & Tobacco Products", "Primary Metals", "Computer & Electronic Products", "Chemical Products", "Miscellaneous Manufacturing"]
    },
    "Apr 2025": {
        "growth": ["Petroleum & Coal Products", "Machinery", "Computer & Electronic Products", "Chemical Products"],
        "decline": ["Wood Products", "Paper Products", "Furniture & Related Products", "Transportation Equipment", "Nonmetallic Mineral Products", "Food, Beverage & Tobacco Products"]
    },
    "Mar 2025": {
        "growth": ["Textile Mills", "Petroleum & Coal Products", "Fabricated Metal Products", "Primary Metals", "Computer & Electronic Products", "Nonmetallic Mineral Products", "Transportation Equipment", "Electrical Equipment, Appliances & Comp", "Miscellaneous Manufacturing"],
        "decline": ["Wood Products", "Paper Products", "Plastics & Rubber Products", "Furniture & Related Products", "Chemical Products", "Food, Beverage & Tobacco Products", "Machinery"]
    },
    "Feb 2025": {
        "growth": ["Petroleum & Coal Products", "Wood Products", "Electrical Equipment, Appliances & Comp", "Miscellaneous Manufacturing", "Primary Metals", "Machinery", "Fabricated Metal Products", "Food, Beverage & Tobacco Products", "Chemical Products"],
        "decline": ["Furniture & Related Products", "Textile Mills", "Nonmetallic Mineral Products", "Computer & Electronic Products", "Plastics & Rubber Products"]
    },
    "Jan 2025": {
        "growth": ["Textile Mills", "Primary Metals", "Petroleum & Coal Products", "Chemical Products", "Machinery", "Transportation Equipment", "Plastics & Rubber Products", "Electrical Equipment, Appliances & Comp"],
        "decline": ["Nonmetallic Mineral Products", "Miscellaneous Manufacturing", "Wood Products", "Furniture & Related Products", "Food, Beverage & Tobacco Products"]
    },
    "Dec 2024": {
        "growth": ["Primary Metals", "Electrical Equipment, Appliances & Comp", "Wood Products", "Furniture & Related Products", "Paper Products", "Miscellaneous Manufacturing", "Plastics & Rubber Products"],
        "decline": ["Textile Mills", "Fabricated Metal Products", "Printing & Related Support Activities", "Machinery", "Chemical Products", "Transportation Equipment", "Nonmetallic Mineral Products"]
    },
    "Nov 2024": {
        "growth": ["Food, Beverage & Tobacco Products", "Computer & Electronic Products", "Electrical Equipment, Appliances & Comp", "Machinery", "Miscellaneous Manufacturing", "Primary Metals"],
        "decline": ["Printing & Related Support Activities", "Plastics & Rubber Products", "Chemical Products", "Paper Products", "Transportation Equipment", "Fabricated Metal Products", "Furniture & Related Products", "Nonmetallic Mineral Products"]
    }
}

# Get all unique industries
all_industries = set()
for month_data in ranklists.values():
    all_industries.update(month_data["growth"])
    all_industries.update(month_data["decline"])

# Build a matrix for each industry
industry_status = {industry: [] for industry in all_industries}

for month in months:
    month_data = ranklists[month]
    for industry in all_industries:
        if industry in month_data["growth"]:
            # Position in growth list (1 = strongest)
            pos = month_data["growth"].index(industry) + 1
            industry_status[industry].append(len(month_data["growth"]) - pos + 1)  # Reverse so higher = stronger
        elif industry in month_data["decline"]:
            # Position in decline list (1 = strongest decline)
            pos = month_data["decline"].index(industry) + 1
            industry_status[industry].append(-(len(month_data["decline"]) - pos + 1))  # Negative
        else:
            industry_status[industry].append(0)

# Find longest consecutive growth/contraction periods
def find_longest_periods(values):
    max_growth = 0
    max_contraction = 0
    current_growth = 0
    current_contraction = 0
    
    for val in values:
        if val > 0:
            current_growth += 1
            current_contraction = 0
            max_growth = max(max_growth, current_growth)
        elif val < 0:
            current_contraction += 1
            current_growth = 0
            max_contraction = max(max_contraction, current_contraction)
        else:
            current_growth = 0
            current_contraction = 0
    
    return max_growth, max_contraction

analysis = {}
for industry, values in industry_status.items():
    max_growth, max_contraction = find_longest_periods(values)
    latest = values[-1]
    previous = values[-2]
    
    analysis[industry] = {
        'max_growth': max_growth,
        'max_contraction': max_contraction,
        'latest': latest,
        'previous': previous
    }

# Sort by longest growth
longest_growth = sorted(analysis.items(), key=lambda x: x[1]['max_growth'], reverse=True)[:3]

# Sort by longest contraction
longest_contraction = sorted(analysis.items(), key=lambda x: x[1]['max_contraction'], reverse=True)[:3]

# Find transitions
contraction_to_growth = [ind for ind, data in analysis.items() if data['previous'] < 0 and data['latest'] > 0]
growth_to_contraction = [ind for ind, data in analysis.items() if data['previous'] > 0 and data['latest'] < 0]

print('=== NEW ORDERS: TOP 3 INDUSTRIES WITH LONGEST GROWTH PERIODS ===')
for industry, data in longest_growth:
    print(f"{industry}: {data['max_growth']} months")

print('\n=== NEW ORDERS: TOP 3 INDUSTRIES WITH LONGEST CONTRACTION PERIODS ===')
for industry, data in longest_contraction:
    print(f"{industry}: {data['max_contraction']} months")

print('\n=== NEW ORDERS: INDUSTRIES MOVING FROM CONTRACTION TO GROWTH (Nov 2025) ===')
print(', '.join(contraction_to_growth) if contraction_to_growth else 'None')

print('\n=== NEW ORDERS: INDUSTRIES MOVING FROM GROWTH TO CONTRACTION (Nov 2025) ===')
print(', '.join(growth_to_contraction) if growth_to_contraction else 'None')
