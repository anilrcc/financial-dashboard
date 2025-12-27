
import re
import csv
import os

def extract_data_from_html(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Regex to find the object list
    pattern = re.compile(r'const optimismData = \[(.*?)\];', re.DOTALL)
    match = pattern.search(content)
    if not match:
        print("Could not find optimismData array")
        return []
    
    array_content = match.group(1)
    
    # Parse the JS object strings into Python dicts
    # Format: { month: "Jan 1990", index: 89.4, ... }
    # We can use regex to extract values
    
    data_points = []
    
    # Split by }, { roughly
    lines = array_content.split('},')
    
    for line in lines:
        try:
            line = line.strip()
            if not line: continue
            
            # Simple parsing using regex for each field
            month_match = re.search(r'month:\s*"([^"]+)"', line)
            index_match = re.search(r'index:\s*(-?[\d\.]+)', line)
            
            if month_match and index_match:
                item = {
                    'month': month_match.group(1),
                    'index': float(index_match.group(1)),
                }
                
                # Optional fields
                for field in ['employment', 'expand', 'inventory', 'economy', 'sales', 'uncertainty']:
                    val_match = re.search(f'{field}:\s*(-?[\d\.]+)', line)
                    if val_match:
                        item[field] = float(val_match.group(1))
                    else:
                        item[field] = None
                
                data_points.append(item)
        except Exception as e:
            print(f"Error parsing line: {line[:50]}... : {e}")
            
    return data_points

def main():
    bak_file = 'small_business_optimism.html.bak'
    
    print(f"Extracting data from {bak_file}...")
    data = extract_data_from_html(bak_file)
    print(f"Extracted {len(data)} records.")
    
    csv_file = 'nfib_history.csv'
    print(f"Writing to {csv_file}...")
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Month', 'Index', 'Employment', 'Expand', 'Inventory', 'Economy', 'Sales', 'Uncertainty'])
        
        for item in data:
            writer.writerow([
                item['month'],
                item['index'],
                item.get('employment') if item.get('employment') is not None else '',
                item.get('expand') if item.get('expand') is not None else '',
                item.get('inventory') if item.get('inventory') is not None else '',
                item.get('economy') if item.get('economy') is not None else '',
                item.get('sales') if item.get('sales') is not None else '',
                item.get('uncertainty') if item.get('uncertainty') is not None else ''
            ])
            
    print("Done.")

if __name__ == "__main__":
    main()
