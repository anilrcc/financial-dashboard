#!/usr/bin/env python3
"""Analyze industry trends from the heatmap data"""

months = [
    "Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025",
    "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
]

data = {
    "Apparel, Leather & Allied Products": [0, 0, 0, 0, 0, 1, 0, 1, 1, 2, -10, -11, -11],
    "Chemical Products": [-9, -3, 4, 7, -3, 10, -2, -3, -8, -2, -6, -4, -5],
    "Computer & Electronic Products": [2, 0, -3, -2, 5, 6, 0, 6, -4, -3, -1, -1, 1],
    "Electrical Equipment, Appliances & Comp": [3, 2, 8, 6, 8, 4, 5, 9, -2, -4, -5, -5, 0],
    "Fabricated Metal Products": [-6, -6, -5, 9, 3, -1, 6, -1, -5, -1, 4, 5, -7],
    "Food, Beverage & Tobacco Products": [1, 0, -1, 5, -2, -3, -4, 8, -1, 4, 0, 2, 2],
    "Furniture & Related Products": [-5, 4, -4, -5, -4, -5, 4, 5, 6, -6, -7, -10, -3],
    "Machinery": [-4, -4, 5, -1, -1, 9, 7, 7, -7, -5, -2, -3, 4],
    "Miscellaneous Manufacturing": [-2, 6, -7, 2, 9, 8, 0, 4, 5, 6, 5, -2, 3],
    "Nonmetallic Mineral Products": [-3, -1, -8, -3, 6, 7, 2, 3, 3, 3, -3, 6, -4],
    "Paper Products": [-8, 5, -2, 0, -6, -4, -7, -4, -9, -10, -8, -9, -9],
    "Petroleum & Coal Products": [0, 0, 3, 1, 2, 2, 3, 2, 0, 5, 1, -6, -6],
    "Plastics & Rubber Products": [-10, 7, 7, 8, -5, 3, 1, 0, 2, -8, -9, 4, -1],
    "Primary Metals": [-1, 1, 2, 3, 4, 11, -1, 0, 7, 7, 2, 1, 0],
    "Printing & Related Support Activities": [-11, -5, 0, 0, 0, 0, -5, 0, -10, 0, 0, -8, 0],
    "Textile Mills": [0, -7, 1, -4, 1, 5, 0, -6, 4, 1, 3, -12, -8],
    "Transportation Equipment": [-7, -2, 6, 10, 7, -2, -3, -2, -3, -7, -4, 3, -2],
    "Wood Products": [0, 3, -6, 4, -7, -6, -6, -5, -6, -9, -11, -7, -10]
}

def find_longest_periods(industry_data):
    """Find the longest consecutive growth and contraction periods"""
    max_growth = 0
    max_contraction = 0
    current_growth = 0
    current_contraction = 0

    for value in industry_data:
        if value > 0:
            current_growth += 1
            current_contraction = 0
            max_growth = max(max_growth, current_growth)
        elif value < 0:
            current_contraction += 1
            current_growth = 0
            max_contraction = max(max_contraction, current_contraction)
        else:
            current_growth = 0
            current_contraction = 0

    return max_growth, max_contraction

def get_transition(prev, curr):
    """Determine the type of transition between two periods"""
    if prev < 0 and curr > 0:
        return 'contraction-to-growth'
    if prev > 0 and curr < 0:
        return 'growth-to-contraction'
    if prev == 0 and curr > 0:
        return 'stable-to-growth'
    if prev == 0 and curr < 0:
        return 'stable-to-contraction'
    if prev < 0 and curr == 0:
        return 'contraction-to-stable'
    if prev > 0 and curr == 0:
        return 'growth-to-stable'
    return 'no-change'

# Analyze all industries
analysis = {}
for industry, values in data.items():
    max_growth, max_contraction = find_longest_periods(values)
    latest_value = values[-1]
    previous_value = values[-2]
    
    analysis[industry] = {
        'max_growth': max_growth,
        'max_contraction': max_contraction,
        'latest_value': latest_value,
        'previous_value': previous_value,
        'transition': get_transition(previous_value, latest_value)
    }

# Sort by longest growth periods
longest_growth = sorted(analysis.items(), key=lambda x: x[1]['max_growth'], reverse=True)[:3]

# Sort by longest contraction periods
longest_contraction = sorted(analysis.items(), key=lambda x: x[1]['max_contraction'], reverse=True)[:3]

# Find transitions
contraction_to_growth = [industry for industry, data in analysis.items() 
                         if data['transition'] == 'contraction-to-growth']

growth_to_contraction = [industry for industry, data in analysis.items() 
                         if data['transition'] == 'growth-to-contraction']

print('=== TOP 3 INDUSTRIES WITH LONGEST GROWTH PERIODS ===')
for industry, data in longest_growth:
    print(f"{industry}: {data['max_growth']} months")

print('\n=== TOP 3 INDUSTRIES WITH LONGEST CONTRACTION PERIODS ===')
for industry, data in longest_contraction:
    print(f"{industry}: {data['max_contraction']} months")

print('\n=== INDUSTRIES MOVING FROM CONTRACTION TO GROWTH (Latest Report) ===')
print(', '.join(contraction_to_growth) if contraction_to_growth else 'None')

print('\n=== INDUSTRIES MOVING FROM GROWTH TO CONTRACTION (Latest Report) ===')
print(', '.join(growth_to_contraction) if growth_to_contraction else 'None')

# Also check stable to growth/contraction
stable_to_growth = [industry for industry, data in analysis.items() 
                    if data['transition'] == 'stable-to-growth']
stable_to_contraction = [industry for industry, data in analysis.items() 
                         if data['transition'] == 'stable-to-contraction']

print('\n=== INDUSTRIES MOVING FROM STABLE TO GROWTH (Latest Report) ===')
print(', '.join(stable_to_growth) if stable_to_growth else 'None')

print('\n=== INDUSTRIES MOVING FROM STABLE TO CONTRACTION (Latest Report) ===')
print(', '.join(stable_to_contraction) if stable_to_contraction else 'None')
