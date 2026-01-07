#!/usr/bin/env python3
"""
Generate Key Insights for services_pmi.html
This script analyzes the data in the HTML file and updates the Key Insights sections
while preserving the existing narrative insights
"""

import re
import os

SERVICES_FILE = "services_pmi.html"


def extract_data_from_html(content):
    """Extract the servicesData object from the HTML JavaScript"""
    # Find the servicesData object
    data_match = re.search(r'const servicesData = \{(.*?)\};', content, re.DOTALL)
    if not data_match:
        print("Could not find servicesData object")
        return None
    
    data_str = data_match.group(1)
    
    # Parse the data into a dictionary
    data = {}
    industry_pattern = r'"([^"]+)":\s*\[([\d\s,\-]+)\]'
    for match in re.finditer(industry_pattern, data_str):
        industry = match.group(1)
        values_str = match.group(2)
        values = [int(x.strip()) for x in values_str.split(',')]
        data[industry] = values
    
    return data


def extract_ranklists_from_html(content):
    """Extract the ranklists object from the HTML JavaScript"""
    ranklists_match = re.search(r'const ranklists = \{(.*?)\};', content, re.DOTALL)
    if not ranklists_match:
        print("Could not find ranklists object")
        return None
    
    ranklists_str = ranklists_match.group(1)
    
    # Parse ranklists
    ranklists = {}
    month_pattern = r'"([^"]+)":\s*\{[^}]*growth:\s*\[(.*?)\],[^}]*decline:\s*\[(.*?)\]'
    
    for match in re.finditer(month_pattern, ranklists_str, re.DOTALL):
        month = match.group(1)
        growth_str = match.group(2)
        decline_str = match.group(3)
        
        # Extract industry names from the lists
        growth = re.findall(r'"([^"]+)"', growth_str)
        decline = re.findall(r'"([^"]+)"', decline_str)
        
        ranklists[month] = {
            'growth': growth,
            'decline': decline
        }
    
    return ranklists


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


def analyze_main_heatmap(data):
    """Analyze the main heatmap data for insights"""
    analysis = {}
    
    for industry, values in data.items():
        max_growth, max_contraction = find_longest_periods(values)
        latest_value = values[-1]
        previous_value = values[-2] if len(values) > 1 else 0
        
        analysis[industry] = {
            'max_growth': max_growth,
            'max_contraction': max_contraction,
            'latest_value': latest_value,
            'previous_value': previous_value
        }
    
    # Sort by longest growth periods
    longest_growth = sorted(analysis.items(), key=lambda x: x[1]['max_growth'], reverse=True)[:3]
    
    # Sort by longest contraction periods
    longest_contraction = sorted(analysis.items(), key=lambda x: x[1]['max_contraction'], reverse=True)[:3]
    
    # Find transitions
    contraction_to_growth = [
        industry for industry, data in analysis.items()
        if data['previous_value'] < 0 and data['latest_value'] > 0
    ]
    
    growth_to_contraction = [
        industry for industry, data in analysis.items()
        if data['previous_value'] > 0 and data['latest_value'] < 0
    ]
    
    return {
        'longest_growth': longest_growth,
        'longest_contraction': longest_contraction,
        'contraction_to_growth': contraction_to_growth,
        'growth_to_contraction': growth_to_contraction
    }


def analyze_new_orders(ranklists):
    """Analyze the New Orders rank data for insights"""
    # Get all unique industries
    all_industries = set()
    for month_data in ranklists.values():
        all_industries.update(month_data["growth"])
        all_industries.update(month_data["decline"])
    
    # Build a matrix for each industry
    industry_status = {industry: [] for industry in all_industries}
    
    # Get months in order
    months = sorted(ranklists.keys(), key=lambda x: (x.split()[1], ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(x.split()[0])))
    
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
    analysis = {}
    for industry, values in industry_status.items():
        max_growth, max_contraction = find_longest_periods(values)
        latest = values[-1] if values else 0
        previous = values[-2] if len(values) > 1 else 0
        
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
    contraction_to_growth = [
        ind for ind, data in analysis.items()
        if data['previous'] < 0 and data['latest'] > 0
    ]
    
    growth_to_contraction = [
        ind for ind, data in analysis.items()
        if data['previous'] > 0 and data['latest'] < 0
    ]
    
    return {
        'longest_growth': longest_growth,
        'longest_contraction': longest_contraction,
        'contraction_to_growth': contraction_to_growth,
        'growth_to_contraction': growth_to_contraction
    }


def generate_trend_analysis_html(insights):
    """Generate HTML for the Trend Analysis section (to be appended to existing narrative)"""
    html = '''
        <h4 style="margin-top: 25px; color: #d35400;">Trend Analysis</h4>
        <p><strong>Top 3 Industries with Longest Periods of Growth:</strong></p>
        <ul style="margin: 5px 0 15px 20px;">
'''
    
    for industry, data in insights['longest_growth']:
        html += f'            <li><strong>{industry}</strong> ({data["max_growth"]} months)</li>\n'
    
    html += '''        </ul>
        
        <p><strong>Top 3 Industries with Longest Periods of Contraction:</strong></p>
        <ul style="margin: 5px 0 15px 20px;">
'''
    
    for industry, data in insights['longest_contraction']:
        html += f'            <li><strong>{industry}</strong> ({data["max_contraction"]} months)</li>\n'
    
    html += '''        </ul>
        
        <p><strong>Industries Moving from Contraction to Growth (Latest Report):</strong> '''
    
    if insights['contraction_to_growth']:
        industries_str = ', '.join([f'<strong>{ind}</strong>' for ind in insights['contraction_to_growth']])
        html += f'''{industries_str} have shifted from negative to positive territory, signaling renewed momentum in these sectors.</p>'''
    else:
        html += '''None in the latest report.</p>'''
    
    if insights['growth_to_contraction']:
        html += '''
        
        <p><strong>Industries Moving from Growth to Contraction (Latest Report):</strong> '''
        industries_str = ', '.join([f'<strong>{ind}</strong>' for ind in insights['growth_to_contraction']])
        html += f'''{industries_str} have reversed course, indicating emerging headwinds.</p>'''
    
    return html


def generate_new_orders_trend_html(insights):
    """Generate HTML for New Orders Trend Analysis section"""
    html = '''
        <h4 style="margin-top: 25px; color: #d35400;">Trend Analysis</h4>
        <p><strong>Top 3 Industries with Longest Periods of New Orders Growth:</strong></p>
        <ul style="margin: 5px 0 15px 20px;">
'''
    
    for industry, data in insights['longest_growth']:
        html += f'            <li><strong>{industry}</strong> ({data["max_growth"]} months)</li>\n'
    
    html += '''        </ul>
        
        <p><strong>Top 3 Industries with Longest Periods of New Orders Contraction:</strong></p>
        <ul style="margin: 5px 0 15px 20px;">
'''
    
    for industry, data in insights['longest_contraction']:
        html += f'            <li><strong>{industry}</strong> ({data["max_contraction"]} months)</li>\n'
    
    html += '''        </ul>
        
        <p><strong>Industries Moving from Contraction to Growth (Latest Report):</strong> '''
    
    if insights['contraction_to_growth']:
        industries_str = ', '.join([f'<strong>{ind}</strong>' for ind in insights['contraction_to_growth']])
        html += f'''{industries_str} have all shifted to positive new order growth, indicating renewed demand momentum.</p>'''
    else:
        html += '''None in the latest report.</p>'''
    
    if insights['growth_to_contraction']:
        html += '''
        
        <p><strong>Industries Moving from Growth to Contraction (Latest Report):</strong> '''
        industries_str = ', '.join([f'<strong>{ind}</strong>' for ind in insights['growth_to_contraction']])
        html += f'''{industries_str} have reversed from growth to contraction, suggesting potential seasonal adjustments or sector-specific headwinds.</p>'''
    
    return html


def update_key_insights():
    """Main function to update Key Insights in the HTML file"""
    if not os.path.exists(SERVICES_FILE):
        print(f"Error: {SERVICES_FILE} not found")
        return False
    
    print("Reading services_pmi.html...")
    with open(SERVICES_FILE, 'r') as f:
        content = f.read()
    
    # Extract data
    print("Extracting data...")
    data = extract_data_from_html(content)
    ranklists = extract_ranklists_from_html(content)
    
    if not data or not ranklists:
        print("Error: Could not extract data from HTML")
        return False
    
    # Analyze data
    print("Analyzing main heatmap data...")
    main_insights = analyze_main_heatmap(data)
    
    print("Analyzing new orders data...")
    new_orders_insights = analyze_new_orders(ranklists)
    
    # Generate new HTML for trend analysis sections
    print("Generating Trend Analysis HTML...")
    main_trend_html = generate_trend_analysis_html(main_insights)
    new_orders_trend_html = generate_new_orders_trend_html(new_orders_insights)
    
    # Replace in content - Remove existing Trend Analysis sections first, then add new ones
    print("Updating HTML file...")
    
    # Pattern to find and remove existing Trend Analysis in main summary
    # We want to keep everything up to </ul> after the narrative bullets, then remove any existing Trend Analysis
    # Pattern to find and remove existing Trend Analysis in main summary
    # Match content inside the div up to "Trend Analysis", handling any HTML structure
    main_pattern = r'(id="main-summary-box"[^>]*>[\s\S]*?)\s*<h4[^>]*>Trend Analysis</h4>[\s\S]*?(?=</div>)'
    if re.search(main_pattern, content, re.DOTALL):
        # Remove existing trend analysis
        content = re.sub(main_pattern, r'\1', content, flags=re.DOTALL)
    
    # Now add the new trend analysis before the closing </div> of main-summary-box
    main_insert_pattern = r'(id="main-summary-box"[^>]*>[\s\S]*?)(\s*</div>)'
    content = re.sub(main_insert_pattern, r'\1' + main_trend_html + r'\2', content, count=1, flags=re.DOTALL)
    
    # Same for New Orders section
    new_orders_pattern = r'(id="new-orders-summary-box"[^>]*>[\s\S]*?)\s*<h4[^>]*>Trend Analysis</h4>[\s\S]*?(?=</div>)'
    if re.search(new_orders_pattern, content, re.DOTALL):
        content = re.sub(new_orders_pattern, r'\1', content, flags=re.DOTALL)
    
    new_orders_insert_pattern = r'(id="new-orders-summary-box"[^>]*>[\s\S]*?)(\s*</div>)'
    content = re.sub(new_orders_insert_pattern, r'\1' + new_orders_trend_html + r'\2', content, count=1, flags=re.DOTALL)
    
    # Write back
    with open(SERVICES_FILE, 'w') as f:
        f.write(content)
    
    print("✓ Services PMI Key Insights updated successfully!")
    return True


if __name__ == "__main__":
    success = update_key_insights()
    if not success:
        exit(1)
