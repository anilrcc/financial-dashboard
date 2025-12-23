#!/usr/bin/env python3
"""Analyze Services PMI trends from the heatmap data"""

months = [
    "Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025",
    "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
]

servicesData = {
    "Retail Trade": [6, 7, 6, -2, 7, 7, -7, 6, -2, -2, 4, 7, 4],
    "Arts, Entertainment & Recreation": [13, 8, 0, 0, -2, 6, 9, 7, 7, -2, -2, 11, 13],
    "Accommodation & Food Services": [14, 3, 13, 4, 12, 11, 10, 10, 11, 1, 4, 7, 14],
    "Wholesale Trade": [11, 2, 11, 12, 8, 10, -1, 7, 8, 10, 10, 6, 11],
    "Health Care & Social Assistance": [12, 6, 9, 7, 2, 5, 2, 2, 7, 7, 9, 10, 12],
    "Educational Services": [-1, -5, 8, -1, 3, 2, 5, 2, 5, -3, 9, -2, -3],
    "Public Administration": [9, 4, 2, 1, 6, -2, 8, 6, 2, 1, 2, 8, 9],
    "Agriculture, Forestry, Fishing & Hunting": [10, -4, 14, 10, 5, -6, -5, 4, 6, 8, 12, -2, 10],
    "Finance & Insurance": [8, 9, 10, 13, 9, -4, -4, 8, -3, 11, 8, 12, 8],
    "Information": [4, -2, 5, 2, 0, 3, 3, 2, 6, 3, 5, -2, 4],
    "Professional, Scientific & Technical Services": [3, -3, -1, 3, -1, -5, 1, -2, 3, 2, -2, -2, 3],
    "Utilities": [1, 1, 1, 11, 4, 1, 6, 1, 4, 7, 1, 5, 1],
    "Other Services": [0, 0, -3, 14, 0, 0, -8, 1, -3, 13, -3, 0, 0],
    "Transportation & Warehousing": [5, 5, 7, 5, 11, 4, -2, 9, 6, 4, 7, 9, 5],
    "Management of Companies & Support Services": [7, -1, 3, -3, -3, -3, -6, -6, 1, -2, 2, -1, 7],
    "Mining": [-3, 0, 12, 9, 0, 9, 7, 9, 6, 9, 11, 0, -4],
    "Real Estate, Rental & Leasing": [-2, -6, -2, 8, 10, 8, 4, 4, 5, 6, -2, -4, -2],
    "Construction": [2, 0, 4, 6, 1, -1, -3, 3, -6, 3, 4, 0, 2]
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
for industry, values in servicesData.items():
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

print('=== SERVICES: TOP 3 INDUSTRIES WITH LONGEST GROWTH PERIODS ===')
for industry, data in longest_growth:
    print(f"{industry}: {data['max_growth']} months")

print('\n=== SERVICES: TOP 3 INDUSTRIES WITH LONGEST CONTRACTION PERIODS ===')
for industry, data in longest_contraction:
    print(f"{industry}: {data['max_contraction']} months")

print('\n=== SERVICES: INDUSTRIES MOVING FROM CONTRACTION TO GROWTH (Latest Report) ===')
print(', '.join(contraction_to_growth) if contraction_to_growth else 'None')

print('\n=== SERVICES: INDUSTRIES MOVING FROM GROWTH TO CONTRACTION (Latest Report) ===')
print(', '.join(growth_to_contraction) if growth_to_contraction else 'None')
