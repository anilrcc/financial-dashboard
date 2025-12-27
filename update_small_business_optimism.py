
import os
import re
import requests
import datetime
import json

# Configuration
HTML_FILE = os.path.join(os.getcwd(), 'small_business_optimism.html')
INDEX_FILE = os.path.join(os.getcwd(), 'index.html')
DATA_URL = 'https://www.nfib.com/news/monthly_report/sbet/'

# Initial "Seed" Data (since we don't have a full full history file yet)
# This replaces the dummy placeholders.
INITIAL_HISTORY = [
    {"month": "Jan 2024", "index": 89.9},
    {"month": "Feb 2024", "index": 89.4},
    {"month": "Mar 2024", "index": 88.5},
    {"month": "Apr 2024", "index": 89.7},
    {"month": "May 2024", "index": 90.5},
    {"month": "Jun 2024", "index": 91.5},
    {"month": "Jul 2024", "index": 93.7},
    {"month": "Aug 2024", "index": 91.2},
    {"month": "Sep 2024", "index": 91.5}, 
    {"month": "Oct 2024", "index": 93.7},
    {"month": "Nov 2024", "index": 92.5}, # est
    {"month": "Dec 2024", "index": 91.9}, # est
    {"month": "Jan 2025", "index": 102.8},
    {"month": "Feb 2025", "index": 100.7},
    {"month": "Mar 2025", "index": 99.5}, # est
    {"month": "Apr 2025", "index": 99.0}, # est
    {"month": "May 2025", "index": 98.8},
    {"month": "Jun 2025", "index": 98.6},
    {"month": "Jul 2025", "index": 100.3},
    {"month": "Aug 2025", "index": 100.8},
    {"month": "Sep 2025", "index": 98.8},
    {"month": "Oct 2025", "index": 98.2}
]

def fetch_latest_data():
    """Scrape the latest index value from the NFIB report page."""
    try:
        print(f"Fetching {DATA_URL}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
        response = requests.get(DATA_URL, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        # 1. Extract Date from Header
        # Patterns like: "November 2025: Small Business Optimism..."
        date_match = re.search(r'([A-Z][a-z]+ \d{4}): Small Business Optimism', content)
        if not date_match:
            print("Could not find date in header.")
            return None
        
        report_month_str = date_match.group(1) # e.g., "November 2025"
        
        # Normalize to "Nov 2025" format
        try:
            dt = datetime.datetime.strptime(report_month_str, "%B %Y")
            report_month = dt.strftime("%b %Y")
        except ValueError:
            # Try abbreviated just in case
            try:
                dt = datetime.datetime.strptime(report_month_str, "%b %Y")
                report_month = dt.strftime("%b %Y")
            except ValueError:
                print(f"Could not parse date format: {report_month_str}")
                return None
        
        # 2. Extract Index Value
        # Pattern: "rose X points ... to 99.0" or "Index ... to 99.0"
        # Look for "to (\d+\.?\d*)" near "Optimism Index"
        # Simplistic regex: "Optimism Index.*?to (\d+\.?\d+)"
        # Note: HTML might have tags.
        
        # Isolate the first paragraph or section content
        # We can search in the whole text but need to be careful.
        val_match = re.search(r'Optimism Index.*?to\s+(\d+\.?\d*)', content, re.DOTALL | re.IGNORECASE)
        if not val_match:
             # Fallback: look for just the number if it says "stood at X.X" or similar
             val_match = re.search(r'Index.*?at\s+(\d+\.?\d*)', content, re.DOTALL | re.IGNORECASE)
        
        if val_match:
            value = float(val_match.group(1))
            print(f"Found Latest Data: {report_month} -> {value}")
            return {"month": report_month, "index": value}
        else:
            print("Could not find index value in text.")
            return None

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def read_existing_data(file_path):
    """Parse the existing JS array from the HTML file."""
    if not os.path.exists(file_path):
        return []
        
    with open(file_path, 'r') as f:
        content = f.read()
        
    match = re.search(r'const optimismData = \[\s*(.*?)\s*\];', content, re.DOTALL)
    if match:
        # data_str looks like: { month: "Jan 2020", index: 104.3 }, ...
        # We need to parse this effectively.
        # Quick and dirty: use Regex to find all objects
        items = []
        entry_pattern = re.compile(r'{\s*month:\s*"([^"]+)",\s*index:\s*([\d\.]+)\s*}')
        for m in entry_pattern.finditer(match.group(1)):
            items.append({"month": m.group(1), "index": float(m.group(2))})
        return items
    return []

def update_html_file(new_data_point):
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    # Read current data
    current_data = read_existing_data(HTML_FILE)
    
    # Check if current_data is placeholder (heuristic: check if it contains the dummy 'Dec 2025' with 90.0 value which we put there)
    # The dummy data had 'Dec 2025' : 90.0. 
    # If we are effectively in Nov 2025, Dec 2025 shouldn't exist or be real.
    # We will replace the list with INITIAL_HISTORY if it looks like the placeholder list.
    
    is_placeholder = False
    if len(current_data) > 0:
        if current_data[-1]['month'] == "Dec 2025" and current_data[-1]['index'] == 90.0:
            is_placeholder = True
    
    final_data = []
    
    if is_placeholder:
        print("Detected placeholder data. replacing with Seed Data.")
        final_data = list(INITIAL_HISTORY)
    else:
        final_data = current_data

    # Append or Update Latest
    if new_data_point:
        # Check if already exists
        exists = False
        for item in final_data:
            if item['month'] == new_data_point['month']:
                item['index'] = new_data_point['index'] # Update if exists
                exists = True
                break
        if not exists:
            final_data.append(new_data_point)
            
    # Sort by date? 
    # Current format "Month YYYY". Use datetime to sort.
    def parse_date(d):
        return datetime.datetime.strptime(d['month'], "%b %Y")
    
    final_data.sort(key=parse_date)
    
    # 3. Generate JS Array String
    js_lines = []
    for item in final_data:
        js_lines.append(f'{{ month: "{item["month"]}", index: {item["index"]} }}')
    
    js_array_str = ",\n            ".join(js_lines)
    
    # 4. Read File Content again to write
    with open(HTML_FILE, 'r') as f: content = f.read()
    
    # Replace Array
    pattern = re.compile(r'(const optimismData = \[)(.*?)(\];)', re.DOTALL)
    replacement = f'\\1\n            {js_array_str}\n        \\3'
    content = pattern.sub(replacement, content)
    
    # 5. Generate Insights (Summary Box)
    if final_data:
        latest = final_data[-1]
        val = latest['index']
        prev = final_data[-2] if len(final_data) > 1 else None
        
        # Logic for insights
        status = "Above Average" if val >= 98 else "Below Average"
        color = "#10b981" if val >= 98 else "#ef4444" # Green if >= 98 (avg), Red if < 98
        
        change_text = ""
        if prev:
            diff = val - prev['index']
            if diff > 0: change_text = f"rise of {diff:.1f} points from {prev['month']}"
            elif diff < 0: change_text = f"drop of {abs(diff):.1f} points from {prev['month']}"
            else: change_text = "unchanged from previous month"
            
        summary_html = f'''
        <h3>Key Insights: {latest['month']}</h3>
        <p><strong>Current Index: {val:.1f} ({status})</strong> - The index remains <strong style="color: {color};">{status.lower()}</strong> relative to the 50-year average of 98. This represents a {change_text}.</p>
        <p><strong>Historical Context:</strong> The index is currently {"recovering" if val > 95 else "depressed"}, sitting {"above" if val > 98 else "below"} the historical average. Inflation and labor quality continue to be key headwinds for small business owners.</p>
        '''
        
        # Replace Summary Box
        # Look for <div id="optimism-summary-box" ...> ... </div>
        # Use a non-greedy regex inside the div
        sum_pattern = re.compile(r'(<div id="optimism-summary-box"[^>]*>)(.*?)(</div>)', re.DOTALL)
        content = sum_pattern.sub(f'\\1{summary_html}\\3', content)

    # 6. Update Timestamp
    today_str = datetime.date.today().strftime("%b %d, %Y")
    if 'id="last-updated-date">' in content:
        content = re.sub(r'(id="last-updated-date">)(.*?)(</span>)', f'\\1{today_str}\\3', content)

    with open(HTML_FILE, 'w') as f: f.write(content)
    print(f"Successfully updated {HTML_FILE}")

def update_index_page():
    if not os.path.exists(INDEX_FILE): return
    
    with open(INDEX_FILE, 'r') as f: content = f.read()
    
    # Update timestamp for Optimism card
    # <a href="small_business_optimism.html" ... > ... <span>Macro Indicator • Dec 26, 2025</span>
    
    # Regex to find the card and its date
    # We look for the href, then scan forward to the Date span
    pattern = re.compile(r'(href="small_business_optimism.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        today_str = datetime.date.today().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(INDEX_FILE, 'w') as f: f.write(content)
        print("Updated Index Page timestamp for Optimism.")

if __name__ == "__main__":
    latest_data = fetch_latest_data()
    update_html_file(latest_data)
    update_index_page()
