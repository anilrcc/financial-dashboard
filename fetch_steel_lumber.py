#!/usr/bin/env python3
"""
Fetch Steel and Lumber COT data from combined archives
"""

import pandas as pd
import requests
from datetime import datetime
import json
import io
import zipfile

COMMODITIES = {
    'lumber': '058644',
    'steel_hrc': '192651',
    'steel_euro': '192691'
}

def fetch_combined_2017_onwards(commodity_code):
    """Fetch 2017-present from combined archives"""
    
    all_data = []
    current_year = datetime.now().year
    
    for year in range(2017, current_year + 1):
        url = f"https://www.cftc.gov/files/dea/history/com_disagg_txt_{year}.zip"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
                
                with z.open(txt_file) as f:
                    df = pd.read_csv(f, low_memory=False)
                    commodity_data = df[df['CFTC_Contract_Market_Code'] == commodity_code].copy()
                    
                    if not commodity_data.empty:
                        all_data.append(commodity_data)
        except Exception as e:
            continue
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return None

def fetch_combined_historical(commodity_code):
    """Fetch 2006-2016 from historical combined archive"""
    
    url = "https://www.cftc.gov/files/dea/history/com_disagg_txt_hist_2006_2016.zip"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
            
            with z.open(txt_file) as f:
                df = pd.read_csv(f, low_memory=False)
                commodity_data = df[df['CFTC_Contract_Market_Code'] == commodity_code].copy()
                
                if not commodity_data.empty:
                    return commodity_data
    except Exception as e:
        print(f"    Error fetching historical: {e}")
    
    return None

def calculate_net_position(df):
    """Calculate Managed Money Net Position as % of OI"""
    
    df_calc = df[[
        'Report_Date_as_YYYY-MM-DD',
        'Open_Interest_All',
        'M_Money_Positions_Long_All',
        'M_Money_Positions_Short_All'
    ]].copy()
    
    df_calc['MM_Net'] = (
        df_calc['M_Money_Positions_Long_All'] - 
        df_calc['M_Money_Positions_Short_All']
    )
    
    df_calc['MM_Net_Pct_OI'] = (
        df_calc['MM_Net'] / df_calc['Open_Interest_All'] * 100
    )
    
    df_calc = df_calc.rename(columns={
        'Report_Date_as_YYYY-MM-DD': 'date',
        'Open_Interest_All': 'open_interest',
        'M_Money_Positions_Long_All': 'mm_long',
        'M_Money_Positions_Short_All': 'mm_short'
    })
    
    return df_calc

def save_chart_data(df, commodity_name):
    """Save data in JSON format"""
    
    chart_data = []
    
    for _, row in df.iterrows():
        chart_data.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'net_pct_oi': round(row['MM_Net_Pct_OI'], 2),
            'mm_long': int(row['mm_long']),
            'mm_short': int(row['mm_short']),
            'open_interest': int(row['open_interest'])
        })
    
    output_file = f'{commodity_name}_cot_data.json'
    with open(output_file, 'w') as f:
        json.dump(chart_data, f, indent=2)
    
    return output_file, len(chart_data), chart_data[0]['date'], chart_data[-1]['date']

def fetch_commodity(name, code):
    """Fetch and process a commodity"""
    
    print(f"\n{'='*80}")
    print(f"Processing: {name.upper()}")
    print(f"{'='*80}")
    
    # Fetch historical
    print("  Fetching 2006-2016 historical...")
    df_hist = fetch_combined_historical(code)
    if df_hist is not None:
        print(f"    ✓ Found {len(df_hist)} records")
    else:
        print(f"    ✗ No historical data")
    
    # Fetch current
    print("  Fetching 2017-present...")
    df_curr = fetch_combined_2017_onwards(code)
    if df_curr is not None:
        print(f"    ✓ Found {len(df_curr)} records")
    else:
        print(f"    ✗ No current data")
    
    # Combine
    if df_hist is not None and df_curr is not None:
        df_combined = pd.concat([df_hist, df_curr], ignore_index=True)
    elif df_hist is not None:
        df_combined = df_hist
    elif df_curr is not None:
        df_combined = df_curr
    else:
        print(f"  ✗ No data available")
        return None
    
    # Process
    df_combined['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(df_combined['Report_Date_as_YYYY-MM-DD'])
    df_combined = df_combined.sort_values('Report_Date_as_YYYY-MM-DD')
    df_combined = df_combined.drop_duplicates(subset=['Report_Date_as_YYYY-MM-DD'], keep='last')
    
    print(f"  Combined total: {len(df_combined)} records")
    
    # Calculate
    df_calc = calculate_net_position(df_combined)
    
    # Save
    output_file, total, start, end = save_chart_data(df_calc, name)
    
    print(f"  ✓ Saved to {output_file}")
    print(f"  Date range: {start} to {end}")
    print(f"  Latest Net % OI: {df_calc.iloc[-1]['MM_Net_Pct_OI']:.2f}%")
    
    return True

if __name__ == '__main__':
    print("="*80)
    print("FETCHING STEEL AND LUMBER COT DATA")
    print("="*80)
    
    for name, code in COMMODITIES.items():
        fetch_commodity(name, code)
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
