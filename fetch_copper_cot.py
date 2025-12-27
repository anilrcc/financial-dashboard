#!/usr/bin/env python3
"""
Fetch and chart Copper COT (Commitment of Traders) data from CFTC
Shows Managed Money Net Position as % of Open Interest from 2006
"""

import pandas as pd
import requests
from datetime import datetime
import json
import io
import zipfile

def fetch_cot_data():
    """Fetch historical COT data from CFTC"""
    
    all_data = []
    current_year = datetime.now().year
    
    # Try different URL patterns for different year ranges
    # Pattern 1: Annual files (2006-2016 use different format)
    for year in range(2006, 2017):
        # Try the disaggregated format
        url = f"https://www.cftc.gov/files/dea/history/deacot{year}.zip"
        print(f"Trying {year} (legacy format)...")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Look for the disaggregated file
                txt_files = [f for f in z.namelist() if 'disagg' in f.lower() and f.endswith('.txt')]
                
                if txt_files:
                    with z.open(txt_files[0]) as f:
                        df = pd.read_csv(f, low_memory=False)
                        
                        # Filter for Copper
                        copper_data = df[df['CFTC_Contract_Market_Code'] == '085692'].copy()
                        
                        if not copper_data.empty:
                            all_data.append(copper_data)
                            print(f"  Found {len(copper_data)} records for {year}")
                        else:
                            print(f"  No copper data in {year}")
        except Exception as e:
            print(f"  Error with legacy format: {e}")
            
            # Try alternative format
            try:
                url2 = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
                print(f"  Trying alternative format for {year}...")
                response = requests.get(url2, timeout=30)
                response.raise_for_status()
                
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
                    
                    with z.open(txt_file) as f:
                        df = pd.read_csv(f, low_memory=False)
                        copper_data = df[df['CFTC_Contract_Market_Code'] == '085692'].copy()
                        
                        if not copper_data.empty:
                            all_data.append(copper_data)
                            print(f"  Found {len(copper_data)} records for {year}")
            except Exception as e2:
                print(f"  Also failed alternative: {e2}")
    
    # Pattern 2: Current format (2017 onwards)
    for year in range(2017, current_year + 1):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        print(f"Fetching {year} (current format)...")
        
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
                        print(f"  Found {len(copper_data)} records for {year}")
        except Exception as e:
            print(f"  Error fetching {year}: {e}")
    
    if not all_data:
        print("No data found!")
        return None
    
    # Combine all years
    df_combined = pd.concat(all_data, ignore_index=True)
    
    # Convert date column
    df_combined['Report_Date_as_YYYY-MM-DD'] = pd.to_datetime(
        df_combined['Report_Date_as_YYYY-MM-DD']
    )
    
    # Sort by date and remove duplicates
    df_combined = df_combined.sort_values('Report_Date_as_YYYY-MM-DD')
    df_combined = df_combined.drop_duplicates(subset=['Report_Date_as_YYYY-MM-DD'], keep='last')
    
    return df_combined


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
    
    print(f"\nData saved to {output_file}")
    print(f"Total records: {len(chart_data)}")
    print(f"Date range: {chart_data[0]['date']} to {chart_data[-1]['date']}")
    print(f"Latest Net % OI: {chart_data[-1]['net_pct_oi']}%")


if __name__ == '__main__':
    print("Fetching Copper COT data from CFTC (2006 onwards)...\n")
    
    # Fetch data
    df = fetch_cot_data()
    
    if df is not None:
        # Calculate net positions
        df_calc = calculate_net_position(df)
        
        # Save for charting
        save_chart_data(df_calc)
        
        print("\nDone!")
    else:
        print("Failed to fetch data")
