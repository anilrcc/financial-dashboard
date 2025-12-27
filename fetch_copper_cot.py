#!/usr/bin/env python3
"""
Fetch Copper COT data from 2006 onwards using the historical consolidated file
"""

import pandas as pd
import requests
from datetime import datetime
import json
import io
import zipfile

def fetch_historical_2006_2016():
    """Fetch 2006-2016 data from consolidated historical file"""
    
    print("Fetching 2006-2016 historical data...")
    url = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_hist_2006_2016.zip"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]
            
            if txt_files:
                print(f"  Found file: {txt_files[0]}")
                with z.open(txt_files[0]) as f:
                    df = pd.read_csv(f, low_memory=False)
                    
                    # Filter for Copper
                    copper_data = df[df['CFTC_Contract_Market_Code'] == '085692'].copy()
                    
                    if not copper_data.empty:
                        print(f"  Found {len(copper_data)} Copper records (2006-2016)")
                        return copper_data
                    else:
                        print("  No Copper data found in historical file")
                        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def fetch_current_2017_onwards():
    """Fetch 2017-present data from annual files"""
    
    all_data = []
    current_year = datetime.now().year
    
    for year in range(2017, current_year + 1):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        print(f"Fetching {year}...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
                
                with z.open(txt_file) as f:
                    df = pd.read_csv(f, low_memory=False)
                    copper_data = df[df['CFTC_Contract_Market_Code'] == '085692'].copy()
                    
                    if not copper_data.empty:
                        all_data.append(copper_data)
                        print(f"  Found {len(copper_data)} records")
        except Exception as e:
            print(f"  Error: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return None

def calculate_net_position(df):
    """Calculate Managed Money Net Position as % of OI"""
    
    # Extract relevant columns
    df_calc = df[[
        'Report_Date_as_YYYY-MM-DD',
        'Open_Interest_All',
        'M_Money_Positions_Long_All',
        'M_Money_Positions_Short_All'
    ]].copy()
    
    # Calculate net position
    df_calc['MM_Net'] = (
        df_calc['M_Money_Positions_Long_All'] - 
        df_calc['M_Money_Positions_Short_All']
    )
    
    # Calculate as % of Open Interest
    df_calc['MM_Net_Pct_OI'] = (
        df_calc['MM_Net'] / df_calc['Open_Interest_All'] * 100
    )
    
    # Rename for clarity
    df_calc = df_calc.rename(columns={
        'Report_Date_as_YYYY-MM-DD': 'date',
        'Open_Interest_All': 'open_interest',
        'M_Money_Positions_Long_All': 'mm_long',
        'M_Money_Positions_Short_All': 'mm_short'
    })
    
    return df_calc

def save_chart_data(df):
    """Save data in JSON format for charting"""
    
    # Prepare data for Chart.js
    chart_data = []
    
    for _, row in df.iterrows():
        chart_data.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'net_pct_oi': round(row['MM_Net_Pct_OI'], 2),
            'mm_long': int(row['mm_long']),
            'mm_short': int(row['mm_short']),
            'open_interest': int(row['open_interest'])
        })
    
    # Save to JSON
    output_file = 'copper_cot_data.json'
    with open(output_file, 'w') as f:
        json.dump(chart_data, f, indent=2)
    
    print(f"\n✓ Data saved to {output_file}")
    print(f"  Total records: {len(chart_data)}")
    print(f"  Date range: {chart_data[0]['date']} to {chart_data[-1]['date']}")
    print(f"  Latest Net % OI: {chart_data[-1]['net_pct_oi']}%")

if __name__ == '__main__':
    print("=" * 80)
    print("Fetching Copper COT Data (2006 - Present)")
    print("=" * 80)
    print()
    
    # Fetch historical data (2006-2016)
    df_historical = fetch_historical_2006_2016()
    
    print()
    
    # Fetch current data (2017-present)
    df_current = fetch_current_2017_onwards()
    
    print()
    
    # Combine datasets
    if df_historical is not None and df_current is not None:
        print("Combining datasets...")
        df_combined = pd.concat([df_historical, df_current], ignore_index=True)
    elif df_historical is not None:
        df_combined = df_historical
    elif df_current is not None:
        df_combined = df_current
    else:
        print("✗ No data found!")
        exit(1)
    
    # Convert dates and sort
    df_combined['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(
        df_combined['Report_Date_as_YYYY-MM-DD']
    )
    df_combined = df_combined.sort_values('Report_Date_as_YYYY-MM-DD')
    df_combined = df_combined.drop_duplicates(subset=['Report_Date_as_YYYY-MM-DD'], keep='last')
    
    print(f"  Combined total: {len(df_combined)} records")
    print()
    
    # Calculate net positions
    df_calc = calculate_net_position(df_combined)
    
    # Save for charting
    save_chart_data(df_calc)
    
    print()
    print("=" * 80)
    print("✓ Complete!")
    print("=" * 80)
