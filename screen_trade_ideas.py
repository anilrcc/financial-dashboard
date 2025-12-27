import re
import os
import json

def parse_js_data(file_path, var_name):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Regex to find the variable definition
    # Looking for: const var_name = { ... };
    # We'll try to capture the content inside the braces
    pattern = f'const {var_name} = ({{.*?}});'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"Could not find {var_name} in {file_path}")
        return {}
    
    json_str = match.group(1)
    
    # The dictionary keys in the file might not be quoted if it's raw JS, 
    # but based on previous file views, they looked like "Key": [values].
    # However, standard JS allows unquoted keys. 
    # Let's clean it up to be valid JSON if needed.
    # The previous view showed quoted keys: "Retail Trade": [...]
    
    try:
        # It might have trailing commas which JSON doesn't like
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {var_name}: {e}")
        # Fallback manual parsing if strict JSON fails
        data = {}
        # formatting appears to be "Industry": [list]
        for line in json_str.split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                key = parts[0].strip().strip('"').strip("'")
                val_str = parts[1].strip().rstrip(',').rstrip(';')
                try:
                    val = json.loads(val_str)
                    data[key] = val
                except:
                    pass
        return data

def analyze_6mo_trend(name, values, dataset_type):
    # Ensure we have at least 6 months
    if len(values) < 6:
        return None

    # Get last 6 months
    last_6 = values[-6:]
    
    # Calculate Metrics
    score_6mo = sum(last_6)
    
    # Momentum: (Avg of Last 3) - (Avg of Previous 3)
    recent_3 = last_6[-3:] # Sep, Oct, Nov
    prev_3 = last_6[:3]    # Jun, Jul, Aug
    
    avg_recent = sum(recent_3) / 3
    avg_prev = sum(prev_3) / 3
    momentum = avg_recent - avg_prev
    
    trend_desc = "Neutral"
    if score_6mo > 15: trend_desc = "Very Strong"
    elif score_6mo > 5: trend_desc = "Strong"
    elif score_6mo < -15: trend_desc = "Very Weak"
    elif score_6mo < -5: trend_desc = "Weak"
    
    # Check for Reversals
    if avg_prev < 0 and avg_recent > 2:
        trend_desc = "Turnaround (Bullish)"
    elif avg_prev > 0 and avg_recent < -2:
        trend_desc = "Deterioration (Bearish)"

    return {
        "Industry": name,
        "Sector": dataset_type,
        "Trend": trend_desc,
        "Score_6mo": score_6mo,
        "Momentum": momentum,
        "History": last_6
    }


def parse_comments_from_html(file_path):
    """Parses comments from the HTML file variables"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract the rawComments variable content
        match = re.search(r'const rawComments = `(.*?)`;', content, re.DOTALL)
        if not match:
            return {}
            
        raw_text = match.group(1)
        comments_by_industry = {}
        
        # Simple parsing of markdown-like structure in the JS string
        # Looking for - **Industry**: "Comment"
        lines = raw_text.split('\n')
        current_month = ""
        
        for line in lines:
            if line.startswith('##'):
                current_month = line.strip('# ').strip()
                continue
                
            # Regex to capture industry and comment
            # - **Industry**: "Comment"
            comment_match = re.search(r'\- \*\*(.*?)\*\*:\s*"(.*?)"', line)
            
            if comment_match:
                industry = comment_match.group(1)
                comment = comment_match.group(2)
                
                if industry not in comments_by_industry:
                    comments_by_industry[industry] = []
                    
                comments_by_industry[industry].append({
                    'month': current_month,
                    'text': comment
                })
        
        return comments_by_industry
    except Exception as e:
        print(f"Error parsing comments: {e}")
        return {}

def analyze_sentiment(comments):
    """Basic keyword analysis of comments for recent months"""
    if not comments:
        return "No Comments", 0, []
        
    recent_comments = comments[:3] # Last 3 entries (which are top of the list usually)
    
    # Keywords
    bullish_words = ['strong', 'growth', 'improved', 'stable', 'positive', 'increase', 'good', 'optimistic', 'picking up', 'busy']
    bearish_words = ['weak', 'slow', 'decrease', 'concern', 'uncertainty', 'tariff', 'inflation', 'down', 'soft', 'struggle', 'flat', 'delay']
    
    score = 0
    snippets = []
    
    for c in recent_comments:
        text = c['text'].lower()
        
        # Simple scoring
        bull_hits = sum(1 for w in bullish_words if w in text)
        bear_hits = sum(1 for w in bearish_words if w in text)
        
        score += (bull_hits - bear_hits)
        snippets.append(f"[{c['month']}] {c['text'][:60]}...")
        
    rating = "Neutral"
    if score >= 2: rating = "Positive"
    elif score <= -2: rating = "Negative"
        
    return rating, score, snippets

def main():
    base_path = "."
    mfg_file = os.path.join(base_path, "industry_heatmap.html")
    svc_file = os.path.join(base_path, "services_pmi.html")
    mfg_comments_file = os.path.join(base_path, "industry_comments.html")
    svc_comments_file = os.path.join(base_path, "services_comments.html")
    
    # 1. Get Quantitative Data
    mfg_data = parse_js_data(mfg_file, "data")
    svc_data = parse_js_data(svc_file, "servicesData")
    
    # 2. Get Qualitative Data
    mfg_comments = parse_comments_from_html(mfg_comments_file)
    svc_comments = parse_comments_from_html(svc_comments_file)
    
    all_industries = []
    
    # helper
    def process(data, comments_dict, sector_name):
        for ind, vals in data.items():
            trend_res = analyze_6mo_trend(ind, vals, sector_name)
            if not trend_res: continue
            
            # Normalize name for comment lookup (basic attempt)
            comment_key = ind
            # Try exact match first, then partial
            found_comments = comments_dict.get(ind, [])
            
            # Analyze sentiment
            sent_rating, sent_score, snippets = analyze_sentiment(found_comments)
            
            trend_res['Sentiment_Rating'] = sent_rating
            trend_res['Sentiment_Score'] = sent_score
            trend_res['Snippets'] = snippets
            
            all_industries.append(trend_res)

    process(mfg_data, mfg_comments, "Mfg")
    process(svc_data, svc_comments, "Svc")
            
    # Screening Logic: High Confidence
    # Longs: Strong/Very Strong Trend AND Positive/Neutral Sentiment
    # Shorts: Weak/Very Weak/Deteriorating Trend AND Negative Sentiment
    
    longs = [x for x in all_industries if (x['Trend'] in ["Strong", "Very Strong", "Turnaround (Bullish)"]) and (x['Sentiment_Score'] >= 0)]
    shorts = [x for x in all_industries if (x['Trend'] in ["Weak", "Very Weak", "Deterioration (Bearish)"]) and (x['Sentiment_Score'] <= -1)] # Stricter on shorts

    print(f"\n{'='*40}")
    print("      HIGH CONFIDENCE TRADE IDEAS")
    print(f"{'='*40}\n")
    
    print("🚀 LONG IDEAS (Quant Trend + Sentiment Support)")
    print(f"{'INDUSTRY':<35} | {'TREND':<20} | {'SENTIMENT'}")
    print("-" * 75)
    for r in sorted(longs, key=lambda x: x['Score_6mo'], reverse=True):
        print(f"{r['Industry']:<35} | {r['Trend']:<20} | {r['Sentiment_Rating']} ({r['Sentiment_Score']})")
        # Print valid comment snippet if exists
        if r['Snippets']:
            print(f"   🗣️  \"{r['Snippets'][0]}\"")
        print("")

    print("\n🔻 SHORT IDEAS (Quant Weakness + Bearish Commentary)")
    print(f"{'INDUSTRY':<35} | {'TREND':<20} | {'SENTIMENT'}")
    print("-" * 75)
    for r in sorted(shorts, key=lambda x: x['Score_6mo']):
        print(f"{r['Industry']:<35} | {r['Trend']:<20} | {r['Sentiment_Rating']} ({r['Sentiment_Score']})")
        if r['Snippets']:
             print(f"   🗣️  \"{r['Snippets'][0]}\"")
        print("")


if __name__ == "__main__":
    main()
