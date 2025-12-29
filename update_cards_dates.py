
import os
import re
import datetime
import sys

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, 'index.html')

def update_index_dates(targets=None):
    if not os.path.exists(INDEX_FILE):
        print("Index file not found!")
        return

    with open(INDEX_FILE, 'r') as f:
        content = f.read()

    # Current Date
    current_date = datetime.datetime.now().strftime('%b %d, %Y')
    new_text = f'International • Updated {current_date}'

    # Regex patterns for the three IDs
    def replace_span(id_name, new_content):
        # Using a specialized regex to handle the content inside the span
        # <span id="card-meta-china">...</span>
        pattern = fr'(<span id="{id_name}">).*?(</span>)'
        return re.sub(pattern, fr'\1{new_content}\2', content)

    # Determine what to update
    all_targets = ['china', 'euro', 'global']
    if not targets:
        targets = all_targets
    
    # Map 'china' -> 'card-meta-china'
    id_map = {
        'china': 'card-meta-china',
        'euro': 'card-meta-euro',
        'global': 'card-meta-global'
    }

    for t in targets:
        lower_t = t.lower()
        if lower_t in id_map:
            content = replace_span(id_map[lower_t], new_text)
            print(f"Updated {lower_t} card date to: {current_date}")

    with open(INDEX_FILE, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    # Parse args
    args = sys.argv[1:]
    update_index_dates(args)
