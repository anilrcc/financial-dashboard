#!/usr/bin/env python3
"""
Investigate CFTC data availability for Copper from 2006 onwards
"""

import requests
from datetime import datetime
import zipfile
import io

def test_url_patterns():
    """Test various URL patterns to find available data"""
    
    year = 2006
    
    patterns = [
        # Pattern 1: Disaggregated futures only
        f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip",
        
        # Pattern 2: Combined futures and options
        f"https://www.cftc.gov/files/dea/history/com_disagg_txt_{year}.zip",
        
        # Pattern 3: Annual archive
        f"https://www.cftc.gov/files/dea/history/deacot{year}.zip",
        
        # Pattern 4: Legacy format
        f"https://www.cftc.gov/files/dea/history/dea{year}.zip",
        
        # Pattern 5: Supplemental
        f"https://www.cftc.gov/files/dea/history/dea_fut_txt_{year}.zip",
        
        # Pattern 6: Try with different naming
        f"https://www.cftc.gov/files/dea/history/deacot{year}f.zip",
    ]
    
    print(f"Testing URL patterns for {year}:\n")
    
    for i, url in enumerate(patterns, 1):
        print(f"{i}. Testing: {url}")
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✓ SUCCESS! Status: {response.status_code}")
                print(f"   Content-Length: {response.headers.get('Content-Length', 'Unknown')}")
                
                # Try to download and inspect
                print(f"   Downloading to inspect contents...")
                response = requests.get(url, timeout=30)
                
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    files = z.namelist()
                    print(f"   Files in archive: {files}")
                    
                    # Try to read first file
                    if files:
                        with z.open(files[0]) as f:
                            # Read first few lines
                            lines = []
                            for _ in range(5):
                                try:
                                    line = f.readline().decode('utf-8', errors='ignore')
                                    if not line:
                                        break
                                    lines.append(line.strip())
                                except:
                                    break
                            
                            print(f"   First few lines:")
                            for line in lines:
                                print(f"     {line[:100]}")
                
            else:
                print(f"   ✗ Failed: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Error: {str(e)[:80]}")
        
        print()

def check_cftc_website():
    """Check the main CFTC data page"""
    print("\nChecking CFTC historical data page...")
    
    try:
        url = "https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ Page accessible")
            
            # Look for links to 2006 data
            content = response.text
            if '2006' in content:
                print("✓ Found references to 2006 data")
                
                # Extract some context
                import re
                matches = re.finditer(r'.{0,100}2006.{0,100}', content)
                for i, match in enumerate(list(matches)[:3]):
                    print(f"  Context {i+1}: {match.group()[:150]}")
            else:
                print("✗ No references to 2006 found")
        else:
            print(f"✗ Failed: Status {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    print("=" * 80)
    print("CFTC Copper COT Data Investigation")
    print("=" * 80)
    print()
    
    test_url_patterns()
    check_cftc_website()
    
    print("\n" + "=" * 80)
    print("Investigation complete")
    print("=" * 80)
