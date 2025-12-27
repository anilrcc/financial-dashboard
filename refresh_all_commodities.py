#!/usr/bin/env python3
"""
Master script to refresh all commodity-related data:
1. Benchmark prices (Oil, Copper, Lumber, Iron Ore) via FRED/TradingEconomics.
2. Commitment of Traders (COT) data for all 9 commodities via CFTC.
3. Re-generation of the unified COT report page.
"""

import os
import subprocess
import sys
from datetime import datetime

def run_script(script_name):
    """Run a python script and report status"""
    print(f"\n>>> Running {script_name}...")
    try:
        # Use sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(f"✓ {script_name} completed successfully.")
        # Print last few lines of output
        lines = result.stdout.splitlines()
        for line in lines[-5:]:
            print(f"  {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}:")
        print(e.stderr)
        return False

def update_index_timestamp():
    """Update the 'Last Updated' timestamp for COT in index.html"""
    index_file = 'index.html'
    if not os.path.exists(index_file): return
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        # Look for the Commitment of Traders card meta
        pattern = re.compile(r'(class="card commodities".*?📊.*?class="card-meta"[^>]*?>\s*)(Market Data • Weekly)(</span>)', re.DOTALL | re.IGNORECASE)
        
        if pattern.search(content):
            today_str = datetime.now().strftime("%b %d, %Y")
            # We refresh the cards description or meta to show last updated
            # Instead of changing "Market Data • Weekly", let's append the date or replace if preferred.
            # Mirroring update_commodities.py style:
            pattern_with_date = re.compile(r'(class="card commodities".*?📊.*?class="card-meta"[^>]*?>\s*)([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
            today_str = datetime.now().strftime("%b %d, %Y")
            content = pattern_with_date.sub(f"\\g<1>Market Data • {today_str}\\g<3>", content)
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✓ Updated Index Page timestamp for COT Reports.")
    except Exception as e:
        print(f"Error updating index timestamp: {e}")

def main():
    print("="*80)
    print(f"STARTING COMPREHENSIVE COMMODITY REFRESH: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. Update Benchmark Prices (Oil, Copper, etc.)
    # Note: This updates commodities.html
    run_script('update_commodities.py')
    
    # 2. Update Metals COT (Gold, Silver, Copper, Platinum, Palladium, Aluminum)
    run_script('fetch_all_commodities.py')
    
    # 3. Update Steel & Lumber COT
    run_script('fetch_steel_lumber.py')
    
    # 4. Re-generate individual COT pages (if still being used as standalone)
    run_script('generate_cot_pages.py')
    
    # 5. Re-generate Unified COT Tabbed Page
    run_script('create_unified_cot.py')
    
    # 6. Update Dashboard Timestamp
    update_index_timestamp()
    
    print("\n" + "="*80)
    print("REFRESH COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
