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
        <h3>Current Reading: {latest["month"]}</h3>
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
        # Get latest value for summary
        latest = data[-1]
        
        # Check if there's a custom summary provided
        if len(sys.argv) > 1:
            summary = sys.argv[1]
        else:
            # Generate default summary
            prev_month = data[-2] if len(data) > 1 else None
            change = latest['index'] - prev_month['index'] if prev_month else 0
            direction = "up" if change > 0 else "down" if change < 0 else "unchanged"
            
            summary = f"The University of Michigan Consumer Sentiment Index registered <strong>{latest['index']}</strong> in {latest['month']}, {direction} from the previous month."
        
        update_sentiment_file(data, summary)
        update_index_timestamp()
    else:
        print("Failed to fetch data. No updates made.")
