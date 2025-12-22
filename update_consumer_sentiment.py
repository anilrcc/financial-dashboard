import os
import datetime
import re
import sys

# Configuration
SENTIMENT_FILE = os.path.join(os.getcwd(), 'consumer_sentiment.html')
INDEX_FILE = os.path.join(os.getcwd(), 'index.html')

def update_sentiment_file(month_str, index_val, summary_text=None):
    if not os.path.exists(SENTIMENT_FILE):
        print(f"Error: {SENTIMENT_FILE} not found.")
        return

    with open(SENTIMENT_FILE, 'r') as f: content = f.read()
    
    # 1. Update Data Array
    # const sentimentData = [ ... ];
    # We want to check if month exists, if not append it.
    
    # Regex to find the array content
    array_match = re.search(r'(const sentimentData = \[)(.*?)(\];)', content, re.DOTALL)
    if array_match:
        data_block = array_match.group(2)
        if month_str in data_block:
            print(f"Data for {month_str} already exists.")
        else:
            print(f"Adding data for {month_str}: {index_val}")
            # Append new object
            new_entry = f', {{ month: "{month_str}", index: {index_val} }}'
            # Insert before the last brace or ] ? 
            # The regex captured the inside. We just append to it.
            # But the inside might end with whitespace or newline.
            # Let's clean it up.
            
            # Simple append approach: replace the closing bracket
            content = content.replace(data_block + "];", data_block.rstrip() + new_entry + "\n        ];")
    
    # 2. Update Summary Box
    if summary_text:
        # <div id="sentiment-summary-box" class="summary-box">
        #    <h3>Current Reading: ...</h3>
        #    <p>...</p>
        # </div>
        
        new_summary_html = f'''
        <h3>Current Reading: {month_str}</h3>
        <p>{summary_text}</p>
        '''
        pattern = re.compile(r'(<div id="sentiment-summary-box" class="summary-box">)(.*?)(</div>)', re.DOTALL)
        content = pattern.sub(f'\\1{new_summary_html}\\3', content)

    # 3. Update Last Updated Date
    today_str = datetime.date.today().strftime("%b %d, %Y")
    if 'id="last-updated-date">' in content:
        content = re.sub(r'(id="last-updated-date">)(.*?)(</span>)', f'\\1{today_str}\\3', content)

    with open(SENTIMENT_FILE, 'w') as f: f.write(content)
    print("Updated Consumer Sentiment HTML.")

def update_index_timestamp():
    if not os.path.exists(INDEX_FILE): return

    with open(INDEX_FILE, 'r') as f: content = f.read()

    # Find the Consumer Sentiment card's timestamp
    # <a href="consumer_sentiment.html" ... <span>Macro Indicator • Dec 22, 2025</span>
    
    pattern = re.compile(r'(href="consumer_sentiment.html".*?class="card-meta">\s*<span>Macro Indicator • )([^<]*?)(</span>)', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        today_str = datetime.date.today().strftime("%b %d, %Y")
        content = pattern.sub(f"\\g<1>{today_str}\\g<3>", content)
        with open(INDEX_FILE, 'w') as f: f.write(content)
        print("Updated Index Page timestamp for Consumer Sentiment.")
    else:
        print("Could not find Consumer Sentiment timestamp in index.html")

if __name__ == "__main__":
    # Example usage: python update_consumer_sentiment.py "Jan 2026" 53.5 "Consumer sentiment rose..."
    if len(sys.argv) >= 3:
        month = sys.argv[1]
        val = float(sys.argv[2])
        summary = sys.argv[3] if len(sys.argv) > 3 else None
        
        update_sentiment_file(month, val, summary)
        update_index_timestamp()
    else:
        print("Usage: python update_consumer_sentiment.py <Month Year> <Index Value> [Summary Text]")
