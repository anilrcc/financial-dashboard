
import os
import requests
import zipfile
import io
import pandas as pd
import json
import datetime
import re

# URLs and File Paths
DATA_URL = "https://ec.europa.eu/economy_finance/db_indicators/surveys/documents/series/nace2_ecfin_2511/main_indicators_sa_nace2.zip"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'eurozone_pmi.html')

# Regions to extract
REGIONS = {
    'EA': 'Eurozone',
    'DE': 'Germany',
    'FR': 'France',
    'IT': 'Italy',
    'ES': 'Spain',
    'NL': 'Netherlands'
}

def fetch_and_process_data():
    print(f"Downloading data from {DATA_URL}...")
    try:
        response = requests.get(DATA_URL)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            excel_files = [f for f in z.namelist() if f.endswith('.xlsx')]
            if not excel_files:
                return None
            
            target_file = excel_files[0]
            print(f"Processing {target_file}...")
            
            with z.open(target_file) as f:
                df = pd.read_excel(f, sheet_name='MONTHLY', header=0)
                df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
                
                all_region_data = {}
                
                for code, name in REGIONS.items():
                    print(f"Extracting data for {name} ({code})...")
                    # Columns for this region
                    cols = {
                        'INDU': f'{code}.INDU',
                        'SERV': f'{code}.SERV',
                        'CONS': f'{code}.CONS',
                        'RETA': f'{code}.RETA',
                        'BUIL': f'{code}.BUIL',
                        'ESI': f'{code}.ESI',
                        'EEI': f'{code}.EEI'
                    }
                    
                    # Verify cols exist
                    if cols['ESI'] not in df.columns:
                        print(f"Warning: Columns for {code} not found. Skipping.")
                        continue

                    # --- Table Data (Last 15 months) ---
                    df_sorted = df.sort_values(by='Date', ascending=False)
                    df_table = df_sorted.head(15)
                    
                    table_data = []
                    for _, row in df_table.iterrows():
                        def get_val(r, col_name):
                            if col_name not in r: return None
                            val = r[col_name]
                            return round(float(val), 1) if pd.notnull(val) else None

                        entry = {
                            'date': row['Date'].strftime('%b %Y'),
                            'headlinePmi': get_val(row, cols['INDU']),
                            'servicesPmi': get_val(row, cols['SERV']),
                            'consumerConf': get_val(row, cols['CONS']),
                            'retailConf': get_val(row, cols['RETA']),
                            'buildingConf': get_val(row, cols['BUIL']),
                            'esi': get_val(row, cols['ESI']),
                            'eei': get_val(row, cols['EEI'])
                        }
                        table_data.append(entry)
                        
                    # --- Historical Data ---
                    df_hist = df.sort_values(by='Date', ascending=True)
                    
                    def get_hist_list(col_name):
                        if col_name not in df_hist: return []
                        return [round(float(v), 1) if pd.notnull(v) else None for v in df_hist[col_name]]

                    history = {
                        'dates': [d.strftime('%Y-%m') for d in df_hist['Date']],
                        'esi': get_hist_list(cols['ESI']),
                        'eei': get_hist_list(cols['EEI']),
                        'headlinePmi': get_hist_list(cols['INDU']),
                        'servicesPmi': get_hist_list(cols['SERV']),
                        'consumerConf': get_hist_list(cols['CONS']),
                        'retailConf': get_hist_list(cols['RETA']),
                        'buildingConf': get_hist_list(cols['BUIL'])
                    }
                    
                    all_region_data[code] = {
                        'table_data': table_data,
                        'history': history,
                        'name': name
                    }
                    
                    # Generate Insight for this region
                    if table_data:
                        latest = table_data[0]
                        prev = table_data[1] if len(table_data) > 1 else latest
                        
                        def get_trend(curr, prev):
                            if curr is None or prev is None: return "N/A", "gray"
                            diff = curr - prev
                            if diff > 0.5: return "improved", "green"
                            if diff < -0.5: return "deteriorated", "red"
                            return "remained stable", "gray"

                        esi_trend, _ = get_trend(latest['esi'], prev['esi']) # Colors handled in CSS/HTML structure or ignored for simple text
                        eei_trend, _ = get_trend(latest['eei'], prev['eei'])
                        
                        # Dynamic wording based on region
                        region_title = name if code != 'EA' else "The Eurozone"
                        
                        insight_html = f"""<h3>{name} Overview</h3><p>{region_title} Economic Sentiment Indicator (ESI) <strong>{esi_trend}</strong> to <strong>{latest['esi']}</strong> in {latest['date']}. Meanwhile, the Employment Expectations Indicator (EEI) <strong>{eei_trend}</strong> to <strong>{latest['eei']}</strong>.</p><p>Manufacturing Confidence came in at <strong>{latest['headlinePmi']}</strong>, while Services Confidence was <strong>{latest['servicesPmi']}</strong>.</p>"""
                        
                        all_region_data[code]['insight'] = insight_html

                return all_region_data

    except Exception as e:
        print(f"Error processing data: {e}")
        return None

def update_html_file(regions_data):
    if not regions_data:
        print("No data to update.")
        return

    # Use EA data for the default display or construction
    ea_data = regions_data.get('EA')
    
    if not os.path.exists(HTML_FILE):
        print(f"HTML file {HTML_FILE} not found.")
        return

    print(f"Updating {HTML_FILE}...")
    with open(HTML_FILE, 'r') as f:
        content = f.read()

    # Create the master JS object
    js_json = json.dumps(regions_data, indent=4)
    
    # Use a placeholder for safe injection via str.replace (avoids regex backslash issues)
    placeholder = "/*__JSON_DATA_PLACEHOLDER__*/"
    
    js_block = f"""
    const allRegionData = {placeholder};
    
    // Default to Eurozone
    let currentRegion = 'EA';
    let euroPmiData = allRegionData['EA'].table_data;
    let euroHistoryData = allRegionData['EA'].history;
    """
    
    # Inject JS Data Wrapper (using regex to find the spot)
    pattern = r"const allRegionData = \{.*?\};"
    
    if re.search(pattern, content, re.DOTALL):
         # Replace the whole structure with the new block structure (containing placeholder)
         # We just replace the variable definition part, but wait, the js_block includes the 'let ...' lines too.
         # The pattern only matches the dict.
         
         # Let's replace the dict part with the placeholder
         content = re.sub(pattern, f"const allRegionData = {placeholder};", content, flags=re.DOTALL)
         
         # Now replace the placeholder with the actual JSON using string replace (safe)
         content = content.replace(placeholder, js_json)
         
    elif "const euroPmiData =" in content:
         # Fallback logic if variable not found
         pass

    # Update summary box
    if ea_data and 'insight' in ea_data:
        # Check if insight contains backslashes, if so, escape them for regex
        # Or safely use replace again.
        
        insight_content = ea_data["insight"]
        # Escape backslashes for re.sub replacement string requirements
        insight_content_safe = insight_content.replace('\\', '\\\\')
        
        summary_pattern = r'<div id="euro-pmi-survey-insights" class="summary-box">.*?</div>'
        new_summary = f'<div id="euro-pmi-survey-insights" class="summary-box">{insight_content_safe}</div>'
        
        if re.search(summary_pattern, content, re.DOTALL):
            content = re.sub(summary_pattern, new_summary, content, flags=re.DOTALL)

    # Clean up old single-region variables if they exist (cleanup)
    content = re.sub(r'const euroPmiData = \[.*?\];', '', content, flags=re.DOTALL)
    content = re.sub(r'const euroHistoryData = \{.*?\};', '', content, flags=re.DOTALL)
        
    # Also update the 'Last Updated' date
    today = datetime.datetime.now().strftime('%b %d, %Y')
    content = re.sub(r'<span id="last-updated-date">.*?</span>', f'<span id="last-updated-date">{today}</span>', content)

    # Also update the Metrics definitions to match what we extracted
    # Current metrics in HTML: 
    # { key: 'headlinePmi', label: 'Manufacturing PMI' },
    # { key: 'output', label: 'Manufacturing Output' }, etc.
    # We extracted: headlinePmi (INDU), servicesPmi (SERV), etc.
    
    new_metrics = [
        "{ key: 'esi', label: 'Economic Sentiment (ESI)' }",
        "{ key: 'headlinePmi', label: 'Manufacturing Confidence' }",
        "{ key: 'servicesPmi', label: 'Services Confidence' }",
        "{ key: 'consumerConf', label: 'Consumer Confidence' }",
        "{ key: 'retailConf', label: 'Retail Confidence' }",
        "{ key: 'buildingConf', label: 'Construction Confidence' }",
        "{ key: 'eei', label: 'Employment Expectations (EEI)' }"
    ]
    metrics_block = "const euroPmiMetrics = [\n            " + ",\n            ".join(new_metrics) + "\n        ];"
    
    metrics_pattern = r"const euroPmiMetrics = \[.*?\];"
    content = re.sub(metrics_pattern, metrics_block, content, flags=re.DOTALL)

    with open(HTML_FILE, 'w') as f:
        f.write(content)
        
    print("HTML updated successfully.")

if __name__ == "__main__":
    result = fetch_and_process_data()
    if result:
        print(f"Data extracted for {len(result)} regions.")
        update_html_file(result)
