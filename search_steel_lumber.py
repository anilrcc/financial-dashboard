#!/usr/bin/env python3
"""
Search for historical COT data for Steel and Lumber
"""

import requests
import zipfile
import io
import pandas as pd
from datetime import datetime

# Commodity codes from the CFTC page
STEEL_LUMBER_CODES = {
    'steel_hrc': '192651',
    'steel_euro': '192691',
    'lumber': '058644'
}

def check_disaggregated_archives():
    """Check if Steel/Lumber are in the disaggregated archives"""
    
    print("Checking disaggregated futures archives...")
    
    # Try 2024 as a test year
    url = "https://www.cftc.gov/files/dea/history/fut_disagg_txt_2024.zip"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
            
            with z.open(txt_file) as f:
                df = pd.read_csv(f, low_memory=False, nrows=10000)
                
                # Get unique commodity codes
                unique_codes = df['CFTC_Contract_Market_Code'].unique()
                
                print(f"\nFound {len(unique_codes)} unique commodity codes in disaggregated futures")
                
                for name, code in STEEL_LUMBER_CODES.items():
                    if code in unique_codes:
                        print(f"  ✓ {name} (Code: {code}) - FOUND!")
                    else:
                        print(f"  ✗ {name} (Code: {code}) - NOT FOUND")
                
    except Exception as e:
        print(f"Error: {e}")

def check_combined_archives():
    """Check combined futures and options archives"""
    
    print("\n" + "="*80)
    print("Checking combined futures+options archives...")
    
    # Try the combined format
    url = "https://www.cftc.gov/files/dea/history/com_disagg_txt_2024.zip"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
            
            with z.open(txt_file) as f:
                df = pd.read_csv(f, low_memory=False, nrows=10000)
                
                unique_codes = df['CFTC_Contract_Market_Code'].unique()
                
                print(f"\nFound {len(unique_codes)} unique commodity codes in combined")
                
                for name, code in STEEL_LUMBER_CODES.items():
                    if code in unique_codes:
                        print(f"  ✓ {name} (Code: {code}) - FOUND!")
                        
                        # Get a sample record
                        sample = df[df['CFTC_Contract_Market_Code'] == code].iloc[0]
                        print(f"    Market: {sample.get('Market_and_Exchange_Names', 'N/A')}")
                    else:
                        print(f"  ✗ {name} (Code: {code}) - NOT FOUND")
                
    except Exception as e:
        print(f"Error: {e}")

def check_historical_combined():
    """Check the 2006-2016 historical combined archive"""
    
    print("\n" + "="*80)
    print("Checking 2006-2016 historical combined archive...")
    
    url = "https://www.cftc.gov/files/dea/history/com_disagg_txt_hist_2006_2016.zip"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
            print(f"Archive file: {txt_file}")
            
            with z.open(txt_file) as f:
                df = pd.read_csv(f, low_memory=False, nrows=20000)
                
                unique_codes = df['CFTC_Contract_Market_Code'].unique()
                
                print(f"\nFound {len(unique_codes)} unique commodity codes in historical combined")
                
                for name, code in STEEL_LUMBER_CODES.items():
                    if code in unique_codes:
                        print(f"  ✓ {name} (Code: {code}) - FOUND!")
                        
                        # Count records
                        records = df[df['CFTC_Contract_Market_Code'] == code]
                        print(f"    Records in sample: {len(records)}")
                    else:
                        print(f"  ✗ {name} (Code: {code}) - NOT FOUND")
                
    except Exception as e:
        print(f"Error: {e}")

def list_all_available_commodities():
    """List all commodities available in combined format"""
    
    print("\n" + "="*80)
    print("Listing ALL available commodities in combined format (2024)...")
    
    url = "https://www.cftc.gov/files/dea/history/com_disagg_txt_2024.zip"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            txt_file = [f for f in z.namelist() if f.endswith('.txt')][0]
            
            with z.open(txt_file) as f:
                df = pd.read_csv(f, low_memory=False)
                
                # Get unique combinations of code and name
                commodities = df[['CFTC_Contract_Market_Code', 'Market_and_Exchange_Names']].drop_duplicates()
                commodities = commodities.sort_values('Market_and_Exchange_Names')
                
                print(f"\nTotal unique commodities: {len(commodities)}")
                print("\nSearching for Steel and Lumber...")
                
                # Search for steel and lumber
                steel_lumber = commodities[
                    commodities['Market_and_Exchange_Names'].str.contains(
                        'STEEL|LUMBER|HRC|HOT', 
                        case=False, 
                        na=False
                    )
                ]
                
                if not steel_lumber.empty:
                    print("\nFound Steel/Lumber related commodities:")
                    for _, row in steel_lumber.iterrows():
                        print(f"  Code: {row['CFTC_Contract_Market_Code']} - {row['Market_and_Exchange_Names']}")
                else:
                    print("\nNo Steel or Lumber commodities found")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("="*80)
    print("SEARCHING FOR STEEL AND LUMBER HISTORICAL COT DATA")
    print("="*80)
    print()
    
    check_disaggregated_archives()
    check_combined_archives()
    check_historical_combined()
    list_all_available_commodities()
    
    print("\n" + "="*80)
    print("SEARCH COMPLETE")
    print("="*80)
