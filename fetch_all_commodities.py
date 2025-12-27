#!/usr/bin/env python3
"""
Fetch COT data for multiple commodities from CFTC
"""

import pandas as pd
import requests
from datetime import datetime
import json
import io
import zipfile
import os

# CFTC Contract Market Codes for commodities
COMMODITY_CODES = {
    'copper': '085692',
    'gold': '088691',
    'silver': '084691',
    'platinum': '076651',
    'palladium': '075651',
    'aluminum': '191693',  # COMEX Aluminum
    # Note: Steel HRC, North Euro Hot-Roll Coil Steel, and Lumber may not have 
    # disaggregated COT data available. We'll check and report.
}

def fetch_historical_2006_2016(commodity_code):
    """Fetch 2006-2016 data from consolidated historical file"""
    
    url = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_hist_2006_2016.zip"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]
            
            if txt_files:
                with z.open(txt_files[0]) as f:
                    df = pd.read_csv(f, low_memory=False)
                    
                    # Filter for commodity
                    commodity_data = df[df['CFTC_Contract_Market_Code'] == commodity_code].copy()
                    
                    if not commodity_data.empty:
                        return commodity_data
    except Exception as e:
        print(f"    Error fetching historical: {e}")
    
    return None

def fetch_current_2017_onwards(commodity_code):
    """Fetch 2017-present data from annual files"""
    
    all_data = []
    current_year = datetime.now().year
    
    for year in range(2017, current_year + 1):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        
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
    """Save data in JSON format for charting"""
    
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

def fetch_commodity_data(commodity_name, commodity_code):
    """Fetch and process data for a single commodity"""
    
    print(f"\n{'='*80}")
    print(f"Processing: {commodity_name.upper()}")
    print(f"{'='*80}")
    
    # Fetch historical data (2006-2016)
    print("  Fetching 2006-2016 historical data...")
    df_historical = fetch_historical_2006_2016(commodity_code)
    
    if df_historical is not None:
        print(f"    ✓ Found {len(df_historical)} records")
    else:
        print(f"    ✗ No historical data found")
    
    # Fetch current data (2017-present)
    print("  Fetching 2017-present data...")
    df_current = fetch_current_2017_onwards(commodity_code)
    
    if df_current is not None:
        print(f"    ✓ Found {len(df_current)} records")
    else:
        print(f"    ✗ No current data found")
    
    # Combine datasets
    if df_historical is not None and df_current is not None:
        df_combined = pd.concat([df_historical, df_current], ignore_index=True)
    elif df_historical is not None:
        df_combined = df_historical
    elif df_current is not None:
        df_combined = df_current
    else:
        print(f"  ✗ No data available for {commodity_name}")
        return None
    
    # Convert dates and sort
    df_combined['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(
        df_combined['Report_Date_as_YYYY-MM-DD']
    )
    df_combined = df_combined.sort_values('Report_Date_as_YYYY-MM-DD')
    df_combined = df_combined.drop_duplicates(subset=['Report_Date_as_YYYY-MM-DD'], keep='last')
    
    print(f"  Combined total: {len(df_combined)} records")
    
    # Calculate net positions
    df_calc = calculate_net_position(df_combined)
    
    # Save for charting
    output_file, total_records, start_date, end_date = save_chart_data(df_calc, commodity_name)
    
    print(f"  ✓ Saved to {output_file}")
    print(f"  Date range: {start_date} to {end_date}")
    print(f"  Latest Net % OI: {df_calc.iloc[-1]['MM_Net_Pct_OI']:.2f}%")
    
    return {
        'name': commodity_name,
        'file': output_file,
        'records': total_records,
        'start_date': start_date,
        'end_date': end_date,
        'latest_net_pct': df_calc.iloc[-1]['MM_Net_Pct_OI']
    }

if __name__ == '__main__':
    print("\n" + "="*80)
    print("FETCHING COT DATA FOR MULTIPLE COMMODITIES")
    print("="*80)
    
    results = []
    
    for commodity_name, commodity_code in COMMODITY_CODES.items():
        result = fetch_commodity_data(commodity_name, commodity_code)
        if result:
            results.append(result)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if results:
        for result in results:
            print(f"\n{result['name'].upper()}:")
            print(f"  Records: {result['records']}")
            print(f"  Range: {result['start_date']} to {result['end_date']}")
            print(f"  Current Net %: {result['latest_net_pct']:.2f}%")
    else:
        print("\nNo data retrieved for any commodity")
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
