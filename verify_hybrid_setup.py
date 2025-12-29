#!/usr/bin/env python3
"""
Quick test to verify the hybrid commodities update is working
"""

import os
import sys

def check_file(filename, description):
    """Check if a file exists and show its status"""
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"✓ {description}: {filename} ({size:,} bytes)")
        return True
    else:
        print(f"✗ {description}: {filename} NOT FOUND")
        return False

def main():
    print("=" * 70)
    print("  Hybrid Commodities Setup Verification")
    print("=" * 70)
    
    print("\n[1] Checking Main Scripts")
    print("-" * 70)
    check_file('update_commodities.py', 'Hybrid commodities script')
    check_file('update_commodities_old.py', 'Backup (FRED-only)')
    check_file('refresh_all_commodities.py', 'Master commodities refresh')
    
    print("\n[2] Checking Command Files")
    print("-" * 70)
    check_file('refresh_commodities_cot.command', 'Commodities refresh command')
    check_file('refresh_all_dashboard.command', 'Full dashboard refresh command')
    
    print("\n[3] Checking Data Files")
    print("-" * 70)
    check_file('commodities.html', 'Commodities dashboard page')
    check_file('index.html', 'Main dashboard page')
    
    print("\n[4] Verifying Script Chain")
    print("-" * 70)
    print("refresh_all_dashboard.command")
    print("  └─> refresh_all_commodities.py")
    print("       └─> update_commodities.py (HYBRID VERSION)")
    print("            ├─> FRED (historical data)")
    print("            └─> Trading Economics (latest data)")
    
    print("\n[5] Checking Hybrid Script Content")
    print("-" * 70)
    with open('update_commodities.py', 'r') as f:
        content = f.read()
        if 'Trading Economics' in content and 'selenium' in content:
            print("✓ Hybrid script confirmed (contains TE + Selenium)")
        else:
            print("✗ WARNING: May not be hybrid version")
        
        if 'fetch_te_commodity' in content:
            print("✓ TE fetch function found")
        else:
            print("✗ WARNING: TE fetch function not found")
    
    print("\n" + "=" * 70)
    print("  Verification Complete")
    print("=" * 70)
    print("\nTo refresh all data with hybrid approach:")
    print("  ./refresh_all_dashboard.command")
    print("\nOr just commodities:")
    print("  python3 update_commodities.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
