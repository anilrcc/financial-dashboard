import os
import datetime
import re
import sys
import requests
import csv
from io import StringIO

# Configuration
SENTIMENT_FILE = os.path.join(os.getcwd(), 'consumer_sentiment.html')
INDEX_FILE = os.path.join(os.getcwd(), 'index.html')
DATA_URL = 'https://www.sca.isr.umich.edu/files/tbmics.csv'

def fetch_sentiment_data():
    """Fetch the latest consumer sentiment data from UMich"""
    try:
        response = requests.get(DATA_URL, timeout=10)
        response.raise_for_status()
        
        # Parse CSV
        csv_data = csv.DictReader(StringIO(response.text))
        data_points = []
        
        for row in csv_data:
            month = row['Month']
            year = row['YYYY']
            value = float(row['ICS_ALL'])
            
            # Format as "Mon YYYY"
            month_abbr = month[:3]
            formatted_date = f"{month_abbr} {year}"
            
            data_points.append({
                'month': formatted_date,
                'index': value
            })
        
        print(f"Fetched {len(data_points)} data points from UMich")
        return data_points
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_sentiment_file(data_points, summary_text=None):
    if not os.path.exists(SENTIMENT_FILE):
        print(f"Error: {SENTIMENT_FILE} not found.")
        return

    with open(SENTIMENT_FILE, 'r') as f: content = f.read()
    
    # 1. Update Data Array
    # Replace the entire sentimentData array
    if data_points:
        # Use all available historical data (not just last 60 months)
        # This ensures we maintain the complete historical dataset from 1978
        
        # Build JavaScript array
        js_array_items = []
        for item in data_points:
            js_array_items.append(f'{{ month: "{item["month"]}", index: {item["index"]} }}')
        
        js_array = ',\n            '.join(js_array_items)
        
        # Replace the array content
        pattern = re.compile(r'(const sentimentData = \[)(.*?)(\];)', re.DOTALL)
        replacement = f'\\1\n            {js_array}\n        \\3'
        content = pattern.sub(replacement, content)
        
        print(f"Updated data array with {len(data_points)} months (complete historical dataset)")
    
    # 2. Update Summary Box
    if summary_text and data_points:
        latest = data_points[-1]
        new_summary_html = f'''
        <h3>Key Insights: {latest["month"]}</h3>
        <p>{summary_text}</p>
        '''
        pattern = re.compile(r'(<div[^>]*id="sentiment-summary-box"[^>]*>)(.*?)(</div>)', re.DOTALL)
        content = pattern.sub(f'\\1{new_summary_html}\\3', content)
    
    # 3. Update Last Updated Date
    today_str = datetime.date.today().strftime("%b %d, %Y")
    if 'id="last-updated-date">' in content:
        content = re.sub(r'(id="last-updated-date">)(.*?)(</span>)', f'\\1{today_str}\\3', content)

    with open(SENTIMENT_FILE, 'w') as f: f.write(content)
    print("Updated Consumer Sentiment HTML.")

def update_index_timestamp():
    if not os.path.exists(INDEX_FILE): return

    with open(INDEX_FILE, 'r') as f: content = f.read()

    # Find the Consumer Sentiment card's timestamp
    pattern = re.compile(r'(href="consumer_sentiment.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        today_str = datetime.date.today().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(INDEX_FILE, 'w') as f: f.write(content)
        print("Updated Index Page timestamp for Consumer Sentiment.")
    else:
        print("Could not find Consumer Sentiment timestamp in index.html")

if __name__ == "__main__":
    # Fetch latest data
    data = fetch_sentiment_data()
    
    if data:
        # Get latest value and calculate insights
        latest = data[-1]
        latest_value = latest['index']
        latest_month = latest['month']
        
        # Calculate changes
        prev_month = data[-2] if len(data) > 1 else None
        year_ago = data[-13] if len(data) > 12 else None
        
        mom_change = latest_value - prev_month['index'] if prev_month else 0
        yoy_change = latest_value - year_ago['index'] if year_ago else 0
        yoy_pct = (yoy_change / year_ago['index'] * 100) if year_ago else 0
        
        # Calculate historical average (all available data)
        avg_sentiment = sum(d['index'] for d in data) / len(data)
        
        # Find peak value
        peak = max(data, key=lambda x: x['index'])
        
        # Determine sentiment zone and classification
        if latest_value < 70:
            zone = "red zone (below 70)"
            zone_color = "#ef4444"
            classification = "Bearish"
        elif latest_value < 80:
            zone = "yellow zone (70-80)"
            zone_color = "#f59e0b"
            classification = "Neutral"
        else:
            zone = "green zone (above 80)"
            zone_color = "#10b981"
            classification = "Bullish"
        
        # Determine when entered current zone
        zone_entry = None
        for i in range(len(data) - 1, -1, -1):
            val = data[i]['index']
            if (latest_value < 70 and val >= 70) or \
               (70 <= latest_value < 80 and (val < 70 or val >= 80)) or \
               (latest_value >= 80 and val < 80):
                zone_entry = data[i + 1]['month'] if i + 1 < len(data) else None
                break
        
        # Generate comprehensive insights
        mom_direction = "up" if mom_change > 0 else "down" if mom_change < 0 else "unchanged"
        mom_text = f"{mom_direction} from {prev_month['index']:.1f}" if prev_month else "no prior data"
        
        yoy_direction = "decline" if yoy_change < 0 else "improvement" if yoy_change > 0 else "no change"
        
        summary = f'''<strong>Current Sentiment: {latest_value:.1f} ({classification})</strong> - The index remains in the <strong style="color: {zone_color};">{zone}</strong>, indicating {"weak consumer confidence" if latest_value < 70 else "neutral consumer outlook" if latest_value < 80 else "strong consumer confidence"}. This reading is {mom_text} in {prev_month['month'] if prev_month else 'the previous period'} but still reflects {"pessimistic" if latest_value < 70 else "cautious" if latest_value < 80 else "optimistic"} consumer outlook.</p>
        <p><strong>Historical Context:</strong> Current sentiment is {"significantly below" if latest_value < avg_sentiment - 10 else "below" if latest_value < avg_sentiment else "above"} the long-term average of ~{avg_sentiment:.0f} and well {"below" if latest_value < peak['index'] - 20 else "off"} the peak of {peak['index']:.1f} reached in {peak['month']}. The index has been in {classification.lower()} territory since {zone_entry if zone_entry else "recent months"}.</p>
        <p><strong>Trend:</strong> Month-over-month {"improvement" if mom_change > 0 else "decline" if mom_change < 0 else "stability"} of {abs(mom_change):+.1f} points suggests {"slight stabilization" if abs(mom_change) < 2 else "notable movement" if abs(mom_change) < 5 else "significant shift"}, {"but" if (mom_change > 0 and yoy_change < 0) or (mom_change < 0 and yoy_change > 0) else "and"} year-over-year {yoy_direction} of {yoy_pct:+.1f}% indicates {"sustained weakness" if yoy_change < -5 else "gradual recovery" if yoy_change > 5 else "relative stability"} in consumer confidence.'''
        
        update_sentiment_file(data, summary)
        update_index_timestamp()
    else:
        print("Failed to fetch data. No updates made.")
