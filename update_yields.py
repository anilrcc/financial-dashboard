import requests
import xml.etree.ElementTree as ET
import datetime
import re
import os

# --- Configuration ---
TARGET_FILE = "yield_curve.html"
# Treasury.gov XML Feed (Daily Treasury Par Yield Curve Rates)
# Dynamically getting current month's data
current_date = datetime.date.today()
year_month = current_date.strftime("%Y%m")
XML_URL = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month={year_month}"

# Mapping from Treasury XML tags to our Chart Labels order
# Order in Chart: ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
TAG_MAP = {
    'BC_1MONTH': '1M',
    'BC_3MONTH': '3M',
    'BC_6MONTH': '6M',
    'BC_1YEAR': '1Y',
    'BC_2YEAR': '2Y',
    'BC_3YEAR': '3Y',
    'BC_5YEAR': '5Y',
    'BC_7YEAR': '7Y',
    'BC_10YEAR': '10Y',
    'BC_20YEAR': '20Y',
    'BC_30YEAR': '30Y'
}
ORDERED_KEYS = ['BC_1MONTH', 'BC_3MONTH', 'BC_6MONTH', 'BC_1YEAR', 'BC_2YEAR', 'BC_3YEAR', 'BC_5YEAR', 'BC_7YEAR', 'BC_10YEAR', 'BC_20YEAR', 'BC_30YEAR']

def fetch_treasury_data():
    print(f"Fetching data from: {XML_URL}")
    try:
        response = requests.get(XML_URL)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # XML Namespace usually exists, need to handle or ignore. 
        # Treasury XML is complex, usually has 'entry' -> 'content' -> 'm:properties' for OData
        # Let's try to just find all 'properties' tags regardless of namespace for simplicity
        # Actually, simpler to regex search if XML parsing is brittle, but let's try standard walk.
        
        # Finding the latest entry
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        if not entries:
            print("No entries found in XML. Might be a new month with no data yet? Trying previous month...")
            # Fallback logic could go here, but for now we assume data exists.
            return None

        # Sort entries by date (usually they are ordered, but good to be safe)
        # Extract data from the LAST entry
        latest_entry = entries[-1]
        content = latest_entry.find("{http://www.w3.org/2005/Atom}content")
        props = content.find("{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}properties")
        
        data = {}
        date_str = ""
        
        for child in props:
            tag_name = child.tag.split('}')[-1] # Remove namespace
            if tag_name == 'NEW_DATE':
                date_str = child.text.split('T')[0] # YYYY-MM-DD
            if tag_name in TAG_MAP:
                data[tag_name] = float(child.text) if child.text else 0.0
                
        return date_str, data

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_html(date_str, data):
    if not os.path.exists(TARGET_FILE):
        print(f"Error: {TARGET_FILE} not found.")
        return

    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # 1. Prepare Data Array String
    # Order: ['1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
    new_values = [data.get(k, 0.0) for k in ORDERED_KEYS]
    js_array_str = f"const currentData = {new_values};"
    
    # 2. Update currentData JS variable
    # Regex look for: const currentData = [ ... ];
    content = re.sub(r"const currentData = \[.*?\];", js_array_str, content)

    # 3. Update Last Updated Text
    # Format Date: Dec 19, 2025
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = dt.strftime("%b %d, %Y")
    # Regex for ID: <div class="refresh-badge" id="last-updated">Last Updated: .*?</div>
    content = re.sub(r'(id="last-updated">Last Updated: ).*?(</div>)', f'\\1{formatted_date}\\2', content)

    # 4. Update KPI Cards
    yield_2y = data.get('BC_2YEAR', 0.0)
    yield_10y = data.get('BC_10YEAR', 0.0)
    spread = (yield_10y - yield_2y) * 100 # bps
    
    # Update 2Y
    content = re.sub(r'(id="kpi-2y">).*?(</div>)', f'\\g<1>{yield_2y:.2f}%\\g<2>', content)
    # Update 10Y
    content = re.sub(r'(id="kpi-10y">).*?(</div>)', f'\\g<1>{yield_10y:.2f}%\\g<2>', content)
    # Update Spread
    sign = "+" if spread >= 0 else ""
    content = re.sub(r'(id="kpi-spread">).*?( bps</div>)', f'\\g<1>{sign}{spread:.0f}\\g<2>', content)

    # Write back
    with open(TARGET_FILE, 'w') as f:
        f.write(content)
    
    print(f"Successfully updated {TARGET_FILE}")
    print(f"Date: {formatted_date}")
    print(f"2Y: {yield_2y}% | 10Y: {yield_10y}% | Spread: {spread:.0f} bps")

    # Update Index File
    INDEX_FILE = "index.html"
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f:
            index_content = f.read()
        
        # Regex to find the Yield Curve card and update the date
        # Looking for class="card yield" ..., then the next Macro Indicator date span
        # <a href="yield_curve.html" class="card yield">
        # ...
        # <span>Macro Indicator • Dec 20, 2025</span>
        
        # We can try to be specific:
        pattern = r'(class="card yield".*?<span>Macro Indicator • ).*?(</span>)'
        
        if re.search(pattern, index_content, re.DOTALL):
            index_content = re.sub(pattern, f'\\g<1>{formatted_date}\\g<2>', index_content, flags=re.DOTALL)
            
            with open(INDEX_FILE, 'w') as f:
                f.write(index_content)
            print(f"Successfully updated {INDEX_FILE}")
        else:
            print(f"Could not find Yield Curve card pattern in {INDEX_FILE}")

if __name__ == "__main__":
    result = fetch_treasury_data()
    if result:
        date_val, data_val = result
        update_html(date_val, data_val)
    else:
        print("Failed to get data.")
