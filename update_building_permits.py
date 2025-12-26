#!/usr/bin/env python3
"""
Update Building Permits data in building_permits.html from FRED (CSV Export)
Fetches Total, Single-Family, and Multi-Family permit data using public CSV endpoints.
"""

import requests
import json
import os
import re
from datetime import datetime

HTML_FILE = "building_permits.html"

# Use FRED public CSV export endpoints (No API key required)
SERIES_URLS = {
    'total': "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PERMIT",
    'single': "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PERMIT1",
    'multi': "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PERMIT5"
}

def fetch_series_csv(url):
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse CSV
        # DATE,VALUE
        # 1960-01-01,92.5
        lines = response.text.strip().split('\n')
        
        if len(lines) < 2:
            return None
            
        data = []
        # Skip header (lines[0])
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) >= 2:
                date_str = parts[0]
                val_str = parts[1]
                if val_str != '.':
                    try:
                        val = float(val_str)
                        data.append({
                            'x': date_str,
                            'y': val
                        })
                    except ValueError:
                        continue
        
        return data
        
    except Exception as e:
        print(f"Error fetching CSV: {e}")
        return None

def generate_html_update(total, single, multi):
    if not total or not single or not multi:
        print("Missing data series")
        return False
        
    print(f"Got {len(total)} months of data for Total Permits")
    
    # Calculate KPIs
    latest_total = total[-1]
    prev_total = total[-2] 
    
    # Check YoY (12 months ago)
    yoy_index = -13 if len(total) >= 13 else 0
    yoy_total_val = total[yoy_index]['y']
    
    latest_single = single[-1]
    latest_multi = multi[-1]
    
    mom_change = ((latest_total['y'] - prev_total['y']) / prev_total['y']) * 100
    yoy_change = ((latest_total['y'] - yoy_total_val) / yoy_total_val) * 100
    
    mom_single = ((latest_single['y'] - single[-2]['y']) / single[-2]['y']) * 100
    mom_multi = ((latest_multi['y'] - multi[-2]['y']) / multi[-2]['y']) * 100
    
    # Generate Insight Text
    trend_text = "up" if mom_change > 0 else "down"
    yoy_text = "higher" if yoy_change > 0 else "lower"
    insight = f"""
    <strong>Total Building Permits</strong> are trending <strong>{trend_text}</strong>, 
    at <strong>{latest_total['y']}k units</strong> (SAAR). 
    This is a <strong>{mom_change:+.1f}%</strong> change from last month and 
    <strong>{yoy_change:+.1f}% {yoy_text}</strong> than a year ago.
    <br><br>
    <strong>Single-Family:</strong> {latest_single['y']}k ({mom_single:+.1f}% MoM)<br>
    <strong>Multi-Family (5+):</strong> {latest_multi['y']}k ({mom_multi:+.1f}% MoM)
    <br><br>
    Housing authorization data is a leading indicator of future construction activity.
    """
    
    # Read HTML
    with open(HTML_FILE, 'r') as f:
        content = f.read()
        
    # Inject Data
    # JS Data Arrays
    # Use json.dumps but to save space we can strip spaces if needed, but standard is fine
    content = re.sub(r'let totalPermitsData = .*?;', f'let totalPermitsData = {json.dumps(total)};', content)
    content = re.sub(r'let singleFamilyData = .*?;', f'let singleFamilyData = {json.dumps(single)};', content)
    content = re.sub(r'let multiFamilyData = .*?;', f'let multiFamilyData = {json.dumps(multi)};', content)
    
    # KPIs
    content = re.sub(r'id="kpi-total">.*?</div>', f'id="kpi-total">{int(latest_total["y"])}k</div>', content)
    content = re.sub(
        r'id="kpi-total-change">.*?</div>', 
        f'id="kpi-total-change"><span class="{get_color_class(mom_change)}">{mom_change:+.1f}% MoM</span></div>', 
        content, flags=re.DOTALL
    )
    
    content = re.sub(r'id="kpi-single">.*?</div>', f'id="kpi-single">{int(latest_single["y"])}k</div>', content)
    content = re.sub(
        r'id="kpi-single-change">.*?</div>', 
        f'id="kpi-single-change"><span class="{get_color_class(mom_single)}">{mom_single:+.1f}% MoM</span></div>', 
        content, flags=re.DOTALL
    )
    
    content = re.sub(r'id="kpi-multi">.*?</div>', f'id="kpi-multi">{int(latest_multi["y"])}k</div>', content)
    content = re.sub(
        r'id="kpi-multi-change">.*?</div>', 
        f'id="kpi-multi-change"><span class="{get_color_class(mom_multi)}">{mom_multi:+.1f}% MoM</span></div>', 
        content, flags=re.DOTALL
    )
    
    # Last Updated Date (Formatted like "Dec 26, 2025")
    today_str = datetime.now().strftime("%b %d, %Y")
    content = re.sub(r'id="last-updated">.*?</div>', f'id="last-updated">Last Updated: {today_str}</div>', content)
    
    # Insight
    content = re.sub(
        r'<div class="analysis-text" id="market-insight">.*?</div>',
        f'<div class="analysis-text" id="market-insight">{insight}</div>',
        content, flags=re.DOTALL
    )
    
    # Save
    with open(HTML_FILE, 'w') as f:
        f.write(content)
        
    print("Successfully updated building_permits.html")
    
    # Update Index Card Date
    index_file = "index.html"
    if os.path.exists(index_file):
        with open(index_file, 'r') as f:
            index_content = f.read()
            
        # Regex to find the Building Permits card and update the date
        # Class is 'card housing'
        pattern = r'(class="card housing".*?<span>Macro Indicator • ).*?(</span>)'
        if re.search(pattern, index_content, re.DOTALL):
            index_content = re.sub(pattern, f'\\g<1>{today_str}\\g<2>', index_content, flags=re.DOTALL)
            with open(index_file, 'w') as f:
                f.write(index_content)
            print(f"Successfully updated {index_file}")
            
    return True

def get_color_class(val):
    if val > 0.1: return "positive"
    if val < -0.1: return "negative"
    return "neutral"

def main():
    print("Updating Building Permits Data (CSV Mode)...")
    
    total = fetch_series_csv(SERIES_URLS['total'])
    single = fetch_series_csv(SERIES_URLS['single'])
    multi = fetch_series_csv(SERIES_URLS['multi'])
    
    generate_html_update(total, single, multi)

if __name__ == "__main__":
    main()
