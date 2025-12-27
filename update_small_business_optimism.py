
import os
import re
import requests
import datetime
import json

# Configuration
HTML_FILE = os.path.join(os.getcwd(), 'small_business_optimism.html')
INDEX_FILE = os.path.join(os.getcwd(), 'index.html')
DATA_URL = 'https://www.nfib.com/news/monthly_report/sbet/'

# Initial "Seed" Data (Derived from public reports for 2021-2025)
INITIAL_HISTORY = [
    # 2021
    {"month": "Jan 2021", "index": 95.0},
    {"month": "Feb 2021", "index": 95.8},
    {"month": "Mar 2021", "index": 98.2},
    {"month": "Apr 2021", "index": 99.8},
    {"month": "May 2021", "index": 99.6},
    {"month": "Jun 2021", "index": 102.5},
    {"month": "Jul 2021", "index": 99.7},
    {"month": "Aug 2021", "index": 100.1},
    {"month": "Sep 2021", "index": 99.1},
    {"month": "Oct 2021", "index": 98.2},
    {"month": "Nov 2021", "index": 98.4},
    {"month": "Dec 2021", "index": 98.9},
    # 2022
    {"month": "Jan 2022", "index": 97.1},
    {"month": "Feb 2022", "index": 95.7},
    {"month": "Mar 2022", "index": 93.2},
    {"month": "Apr 2022", "index": 93.2},
    {"month": "May 2022", "index": 93.1},
    {"month": "Jun 2022", "index": 89.5},
    {"month": "Jul 2022", "index": 89.9},
    {"month": "Aug 2022", "index": 91.8},
    {"month": "Sep 2022", "index": 92.1},
    {"month": "Oct 2022", "index": 91.3},
    {"month": "Nov 2022", "index": 91.9},
    {"month": "Dec 2022", "index": 89.8},
    # 2023
    {"month": "Jan 2023", "index": 90.3, "employment": 19, "expand": 7, "inventory": -8, "economy": -45, "sales": -14},
    {"month": "Feb 2023", "index": 90.9, "employment": 17, "expand": 6, "inventory": -7, "economy": -47, "sales": -9},
    {"month": "Mar 2023", "index": 90.1, "employment": 15, "expand": 2, "inventory": -4, "economy": -47, "sales": -15},
    {"month": "Apr 2023", "index": 89.0, "employment": 17, "expand": 3, "inventory": -5, "economy": -49, "sales": -19},
    {"month": "May 2023", "index": 89.4, "employment": 19, "expand": 3, "inventory": -2, "economy": -50, "sales": -21},
    {"month": "Jun 2023", "index": 91.0, "employment": 15, "expand": 6, "inventory": -3, "economy": -40, "sales": -14},
    {"month": "Jul 2023", "index": 91.9, "employment": 17, "expand": 6, "inventory": -2, "economy": -30, "sales": -12},
    {"month": "Aug 2023", "index": 91.3, "employment": 17, "expand": 6, "inventory": 0, "economy": -37, "sales": -14},
    {"month": "Sep 2023", "index": 90.8, "employment": 18, "expand": 5, "inventory": -1, "economy": -43, "sales": -13},
    {"month": "Oct 2023", "index": 90.7, "employment": 17, "expand": 6, "inventory": 0, "economy": -43, "sales": -10},
    {"month": "Nov 2023", "index": 90.6, "employment": 18, "expand": 8, "inventory": -3, "economy": -42, "sales": -8},
    {"month": "Dec 2023", "index": 91.9, "employment": 16, "expand": 8, "inventory": -5, "economy": -36, "sales": -4},
    # 2024
    {"month": "Jan 2024", "index": 89.9, "employment": None, "expand": None, "inventory": None, "economy": None, "sales": None},
    {"month": "Feb 2024", "index": 89.4, "employment": None, "expand": None, "inventory": None, "economy": None, "sales": None},
    {"month": "Mar 2024", "index": 88.5, "employment": None, "expand": None, "inventory": None, "economy": -36, "sales": None},
    {"month": "Apr 2024", "index": 89.7, "employment": 12, "expand": 4, "inventory": -6, "economy": None, "sales": -12},
    {"month": "May 2024", "index": 90.5, "employment": 15, "expand": 4, "inventory": -6, "economy": -30, "sales": -13},
    {"month": "Jun 2024", "index": 91.5, "employment": 15, "expand": 4, "inventory": -2, "economy": -25, "sales": -13},
    {"month": "Jul 2024", "index": 93.7, "employment": 15, "expand": 5, "inventory": 2, "economy": -7, "sales": -9},
    {"month": "Aug 2024", "index": 91.2, "employment": 13, "expand": None, "inventory": -1, "economy": -13, "sales": -18},
    {"month": "Sep 2024", "index": 91.5, "employment": 15, "expand": 4, "inventory": -3, "economy": -12, "sales": -9},
    {"month": "Oct 2024", "index": 93.7, "employment": 15, "expand": 6, "inventory": -2, "economy": -5, "sales": -4},
    {"month": "Nov 2024", "index": 101.7, "employment": 18, "expand": 13, "inventory": 1, "economy": 36, "sales": 14}, # Revised based on search
    {"month": "Dec 2024", "index": 105.1, "employment": 19, "expand": 20, "inventory": 6, "economy": 52, "sales": 22}, # Revised based on search
    # 2025
    {"month": "Jan 2025", "index": 102.8},
    {"month": "Feb 2025", "index": 100.7},
    {"month": "Mar 2025", "index": 97.4},
    {"month": "Apr 2025", "index": 95.8},
    {"month": "May 2025", "index": 98.8},
    {"month": "Jun 2025", "index": 98.6},
    {"month": "Jul 2025", "index": 100.3},
    {"month": "Aug 2025", "index": 100.8},
    {"month": "Sep 2025", "index": 98.8},
    {"month": "Oct 2025", "index": 98.2},
    {"month": "Nov 2025", "index": 99.0}
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
        optimism_val = None
        employment_val = None
        expand_val = None
        inventory_val = None
        optimism_val = None
        employment_val = None
        expand_val = None
        inventory_val = None
        economy_val = None
        sales_val = None

        # -- Main Index --
        val_match = re.search(r'Optimism Index.*?to\s+(\d+\.?\d*)', content, re.DOTALL | re.IGNORECASE)
        if not val_match:
             val_match = re.search(r'Index.*?at\s+(\d+\.?\d*)', content, re.DOTALL | re.IGNORECASE)
        if val_match:
            optimism_val = float(val_match.group(1))

        # -- Employment Plans --
        # Pattern: "net 19% of owners plan to create new jobs" or "seasonally adjusted net 19%..."
        # Limit the search window to avoid matching distant numbers
        emp_match = re.search(r'net\s+(-?\d+)%.{0,100}?plan to create new jobs', content, re.IGNORECASE | re.DOTALL)
        if not emp_match:
             emp_match = re.search(r'hiring plans.*?net\s+(-?\d+)%', content, re.IGNORECASE | re.DOTALL)
        if emp_match:
            employment_val = float(emp_match.group(1))

        # -- Good Time to Expand --
        # "net 6% reported it was a good time to expand"
        expand_match = re.search(r'net\s+(-?\d+)%.{0,100}?good time to expand', content, re.IGNORECASE | re.DOTALL)
        if expand_match:
            expand_val = float(expand_match.group(1))

        # -- Inventory Plans --
        # "net negative 1% ... plan inventory investment"
        inv_match = None
        # Try specific pattern first
        inv_match = re.search(r'net\s+(negative\s+)?(\d+)%.{0,100}?plan inventory investment', content, re.IGNORECASE | re.DOTALL)
        
        if inv_match:
             sign = -1 if inv_match.group(1) else 1
             inventory_val = float(inv_match.group(2)) * sign

        # -- Expect Economy to Improve -- 
        # Pattern: "net X% expect better business conditions" or similar
        # "Expect Better Economy" is often "Expect Better Business Conditions" in NFIB terms
        # Look for "expect better business conditions"
        eco_match = re.search(r'net\s+(-?\d+)%.{0,100}?expect better business conditions', content, re.IGNORECASE | re.DOTALL)
        if not eco_match:
             # Try simpler pattern
             eco_match = re.search(r'better business conditions.*?net\s+(-?\d+)%', content, re.IGNORECASE | re.DOTALL)
        if eco_match:
            economy_val = float(eco_match.group(1))

        # -- Expect Real Sales Higher --
        # "net X% expect higher real sales" or similar
        # From previous context: "net percent of owners expecting higher real sales volumes rose ... to a net 15%"
        sales_match = re.search(r'expecting higher real sales.*?net\s+(-?\d+)%', content, re.IGNORECASE | re.DOTALL)
        if not sales_match:
             sales_match = re.search(r'net\s+(-?\d+)%.{0,100}?expect higher real sales', content, re.IGNORECASE | re.DOTALL)
        if sales_match:
            sales_val = float(sales_match.group(1))

        if optimism_val is not None:
             print(f"Found Data: {report_month} -> Opt: {optimism_val}, Emp: {employment_val}, Exp: {expand_val}, Inv: {inventory_val}, Eco: {economy_val}, Sales: {sales_val}")
             return {
                 "month": report_month, 
                 "index": optimism_val,
                 "employment": employment_val,
                 "expand": expand_val,
                 "inventory": inventory_val,
                 "economy": economy_val,
                 "sales": sales_val
             }
        else:
             print("Could not find index value in text.")
             return None

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def load_historical_csv():
    """Load historical data from 'nfib_history.csv' if it exists.
    Expected Format: Month, Index, Employment, Expand, Inventory, Economy, Sales
    """
    csv_path = os.path.join(os.getcwd(), 'nfib_history.csv')
    if not os.path.exists(csv_path):
        return []
    
    csv_data = []
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()[1:] # Skip header
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    month_str = parts[0].strip()
                    try:
                        val = float(parts[1].strip())
                        item = {"month": month_str, "index": val}
                        
                        # Helpers to parse optional extras
                        def parse_float(s):
                            try:
                                v = s.strip()
                                return float(v) if v else None
                            except:
                                return None

                        if len(parts) > 2: item['employment'] = parse_float(parts[2])
                        if len(parts) > 3: item['expand'] = parse_float(parts[3])
                        if len(parts) > 4: item['inventory'] = parse_float(parts[4])
                        if len(parts) > 5: item['economy'] = parse_float(parts[5])
                        if len(parts) > 6: item['sales'] = parse_float(parts[6])
                        
                        csv_data.append(item)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading nfib_history.csv: {e}")
        
    return csv_data

def update_html_file(new_data_point):
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    # 1. Combine Data Sources
    # Priority: 
    #   1. New Scraped Data (most recent)
    #   2. Local CSV History (if provided by user)
    #   3. Initial Hardcoded Seed (fallback/recent history)
    
    # Start with seed
    combined_data = {item['month']: item for item in INITIAL_HISTORY}
    
    # Load CSV and overwrite/append
    csv_history = load_historical_csv()
    if csv_history:
        print(f"Loaded {len(csv_history)} points from nfib_history.csv")
        for item in csv_history:
            combined_data[item['month']] = item
            
    # Add/Update Scraping Result
    if new_data_point:
        combined_data[new_data_point['month']] = new_data_point
    
    # Convert back to list and sort
    final_data = list(combined_data.values())
    
    # Sort by date
    def parse_date(d):
        try:
            return datetime.datetime.strptime(d['month'], "%b %Y")
        except ValueError:
            # Fallback for weird formats? Return min date
            return datetime.datetime(1900, 1, 1)
    
    final_data.sort(key=parse_date)
    
    # 3. Generate JS Array String
    js_lines = []
    for item in final_data:
        emp = item.get('employment', 'null')
        exp = item.get('expand', 'null')
        inv = item.get('inventory', 'null')
        eco = item.get('economy', 'null')
        sal = item.get('sales', 'null')
        
        # Handle None in string formatting
        emp = emp if emp is not None else 'null'
        exp = exp if exp is not None else 'null'
        inv = inv if inv is not None else 'null'
        eco = eco if eco is not None else 'null'
        sal = sal if sal is not None else 'null'

        js_lines.append(f'{{ month: "{item["month"]}", index: {item["index"]}, employment: {emp}, expand: {exp}, inventory: {inv}, economy: {eco}, sales: {sal} }}')
    
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
        # Find prev month in sorted list
        prev = final_data[-2] if len(final_data) > 1 else None
        
        # Logic for insights
        # Logic for insights
        status = "Above Average" if val >= 100 else "Below Average"
        color = "#10b981" if val >= 100 else "#ef4444" 
        
        change_text = ""
        if prev:
            diff = val - prev['index']
            if diff > 0: change_text = f"rise of {diff:.1f} points from {prev['month']}"
            elif diff < 0: change_text = f"drop of {abs(diff):.1f} points from {prev['month']}"
            else: change_text = "unchanged from previous month"

        # Sub-component Analysis
        eco_val = latest.get('economy')
        sales_val = latest.get('sales')
        emp_val = latest.get('employment')

        drivers = []
        if eco_val is not None:
             if eco_val > 0: drivers.append(f"optimism about the economy is net positive ({eco_val}%)")
             elif eco_val < -20: drivers.append(f"economic outlook remains pessimistic ({eco_val}%)")
        
        if sales_val is not None:
             if sales_val > 0: drivers.append(f"sales expectations are improving ({sales_val}%)")
             elif sales_val < 0: drivers.append(f"sales expectations remain soft ({sales_val}%)")

        driver_text = "Owners are seeing mixed signals."
        if drivers:
            driver_text = f"Key drivers include: {', '.join(drivers)}."
            
        summary_html = f'''
        <h3>Key Insights: {latest['month']}</h3>
        <p><strong>Current Index: {val:.1f} ({status})</strong> - The index remains <strong style="color: {color};">{status.lower()}</strong> relative to the baseline of 100. This represents a {change_text}.</p>
        <p><strong>Historical Context:</strong> {driver_text} Inflation and labor quality continue to be cited as persistent headwinds, although recent data suggests some stabilization in sentiment.</p>
        '''
        
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
