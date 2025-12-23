#!/usr/bin/env python3
"""Analyze Services New Orders rank data trends"""

months = [
    "Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025",
    "Apr 2025", "May 2025", "Jun 2025", "Jul 2025", "Aug 2025", "Sep 2025", "Oct 2025", "Nov 2025"
]

ranklists = {
    "Nov 2024": {
        "growth": ["Arts, Entertainment & Recreation", "Accommodation & Food Services", "Management of Companies & Support Services", "Public Administration", "Information", "Wholesale Trade", "Retail Trade", "Agriculture, Forestry, Fishing & Hunting", "Health Care & Social Assistance", "Professional, Scientific & Technical Services", "Finance & Insurance", "Transportation & Warehousing", "Utilities"],
        "decline": ["Mining", "Real Estate, Rental & Leasing", "Educational Services"]
    },
    "Dec 2024": {
        "growth": ["Arts, Entertainment & Recreation", "Finance & Insurance", "Transportation & Warehousing", "Retail Trade", "Public Administration", "Health Care & Social Assistance", "Utilities"],
        "decline": ["Real Estate, Rental & Leasing", "Educational Services", "Construction", "Information", "Professional, Scientific & Technical Services"]
    },
    "Jan 2025": {
        "growth": ["Accommodation & Food Services", "Agriculture, Forestry, Fishing & Hunting", "Educational Services", "Finance & Insurance", "Wholesale Trade", "Transportation & Warehousing", "Health Care & Social Assistance", "Public Administration", "Construction", "Retail Trade"],
        "decline": ["Real Estate, Rental & Leasing", "Other Services", "Professional, Scientific & Technical Services", "Information", "Management of Companies & Support Services"]
    },
    "Feb 2025": {
        "growth": ["Mining", "Construction", "Finance & Insurance", "Agriculture, Forestry, Fishing & Hunting", "Other Services", "Health Care & Social Assistance", "Wholesale Trade", "Utilities", "Public Administration", "Transportation & Warehousing", "Professional, Scientific & Technical Services"],
        "decline": ["Management of Companies & Support Services", "Accommodation & Food Services", "Retail Trade", "Educational Services"]
    },
    "Mar 2025": {
        "growth": ["Transportation & Warehousing", "Wholesale Trade", "Utilities", "Accommodation & Food Services", "Finance & Insurance", "Public Administration", "Retail Trade", "Information", "Health Care & Social Assistance"],
        "decline": ["Professional, Scientific & Technical Services", "Real Estate, Rental & Leasing", "Management of Companies & Support Services", "Educational Services"]
    },
    "Apr 2025": {
        "growth": ["Accommodation & Food Services", "Wholesale Trade", "Transportation & Warehousing", "Educational Services", "Real Estate, Rental & Leasing", "Information", "Retail Trade", "Health Care & Social Assistance"],
        "decline": ["Professional, Scientific & Technical Services", "Management of Companies & Support Services", "Construction", "Finance & Insurance", "Public Administration"]
    },
    "May 2025": {
        "growth": ["Accommodation & Food Services", "Arts, Entertainment & Recreation", "Public Administration", "Educational Services", "Utilities", "Information"],
        "decline": ["Mining", "Management of Companies & Support Services", "Real Estate, Rental & Leasing", "Other Services", "Wholesale Trade", "Retail Trade", "Construction"]
    },
    "Jun 2025": {
        "growth": ["Other Services", "Finance & Insurance", "Professional, Scientific & Technical Services", "Transportation & Warehousing", "Wholesale Trade", "Utilities", "Public Administration", "Educational Services"],
        "decline": ["Agriculture, Forestry, Fishing & Hunting", "Mining", "Real Estate, Rental & Leasing", "Construction"]
    },
    "Jul 2025": {
        "growth": ["Wholesale Trade", "Transportation & Warehousing", "Finance & Insurance", "Public Administration", "Other Services", "Management of Companies & Support Services", "Utilities"],
        "decline": ["Accommodation & Food Services", "Construction", "Arts, Entertainment & Recreation", "Agriculture, Forestry, Fishing & Hunting", "Educational Services", "Real Estate, Rental & Leasing", "Health Care & Social Assistance"]
    },
    "Aug 2025": {
        "growth": ["Wholesale Trade", "Educational Services", "Arts, Entertainment & Recreation", "Information", "Transportation & Warehousing", "Retail Trade", "Utilities", "Management of Companies & Support Services", "Health Care & Social Assistance", "Finance & Insurance", "Public Administration", "Professional, Scientific & Technical Services", "Real Estate, Rental & Leasing"],
        "decline": ["Construction", "Accommodation & Food Services"]
    },
    "Sep 2025": {
        "growth": ["Accommodation & Food Services", "Other Services", "Health Care & Social Assistance", "Public Administration", "Information", "Wholesale Trade", "Educational Services", "Finance & Insurance", "Utilities"],
        "decline": ["Real Estate, Rental & Leasing", "Construction", "Agriculture, Forestry, Fishing & Hunting", "Retail Trade", "Management of Companies & Support Services", "Professional, Scientific & Technical Services"]
    },
    "Oct 2025": {
        "growth": ["Accommodation & Food Services", "Retail Trade", "Wholesale Trade", "Real Estate, Rental & Leasing", "Health Care & Social Assistance", "Utilities", "Transportation & Warehousing", "Agriculture, Forestry, Fishing & Hunting", "Information", "Professional, Scientific & Technical Services", "Educational Services"],
        "decline": ["Arts, Entertainment & Recreation", "Management of Companies & Support Services", "Finance & Insurance", "Public Administration", "Construction", "Other Services"]
    },
    "Nov 2025": {
        "growth": ["Public Administration", "Arts, Entertainment & Recreation", "Retail Trade", "Other Services", "Wholesale Trade", "Health Care & Social Assistance", "Educational Services", "Transportation & Warehousing", "Finance & Insurance", "Professional, Scientific & Technical Services", "Utilities", "Information"],
        "decline": ["Real Estate, Rental & Leasing", "Management of Companies & Support Services", "Construction", "Accommodation & Food Services"]
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
            pos = month_data["growth"].index(industry) + 1
            industry_status[industry].append(len(month_data["growth"]) - pos + 1)
        elif industry in month_data["decline"]:
            pos = month_data["decline"].index(industry) + 1
            industry_status[industry].append(-(len(month_data["decline"]) - pos + 1))
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

print('=== SERVICES NEW ORDERS: TOP 3 INDUSTRIES WITH LONGEST GROWTH PERIODS ===')
for industry, data in longest_growth:
    print(f"{industry}: {data['max_growth']} months")

print('\n=== SERVICES NEW ORDERS: TOP 3 INDUSTRIES WITH LONGEST CONTRACTION PERIODS ===')
for industry, data in longest_contraction:
    print(f"{industry}: {data['max_contraction']} months")

print('\n=== SERVICES NEW ORDERS: INDUSTRIES MOVING FROM CONTRACTION TO GROWTH (Nov 2025) ===')
print(', '.join(contraction_to_growth) if contraction_to_growth else 'None')

print('\n=== SERVICES NEW ORDERS: INDUSTRIES MOVING FROM GROWTH TO CONTRACTION (Nov 2025) ===')
print(', '.join(growth_to_contraction) if growth_to_contraction else 'None')
