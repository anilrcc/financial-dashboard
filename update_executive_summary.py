#!/usr/bin/env python3
"""
Generate Executive Summary for Financial Dashboard
Synthesizes data from ISM PMI, Services PMI, Treasury Yields, Corporate Bonds, and Consumer Sentiment.
"""

import os
import re
import datetime
import json

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, 'index.html')
MFG_PMI_FILE = os.path.join(BASE_DIR, 'industry_heatmap.html')
SVC_PMI_FILE = os.path.join(BASE_DIR, 'services_pmi.html')
YIELDS_FILE = os.path.join(BASE_DIR, 'yield_curve.html')
SENTIMENT_FILE = os.path.join(BASE_DIR, 'consumer_sentiment.html')
BONDS_FILE = os.path.join(BASE_DIR, 'corporate_bonds.html')
PERMITS_FILE = os.path.join(BASE_DIR, 'building_permits.html')
OPTIMISM_FILE = os.path.join(BASE_DIR, 'small_business_optimism.html')

def get_market_data():
    data = {
        'mfg_pmi': None,
        'svc_pmi': None,
        'yield_spread_10y2y': None,
        'consumer_sentiment': None,
        'credit_spread_bbb_aaa': None,
        'housing_permits': None,
        'sb_optimism': None,
        'regime': 'Unknown'
    }

    # 1. Manufacturing PMI
    if os.path.exists(MFG_PMI_FILE):
        with open(MFG_PMI_FILE, 'r') as f:
            content = f.read()
            # Find all matches of pmi: VALUE in rawPmiData array
            # matches = re.findall(r'pmi:\s*([0-9.]+)', content)
            # The file structure has dates descending, so first match is newest.
            match = re.search(r'pmi:\s*([0-9.]+)', content)
            if match:
                data['mfg_pmi'] = float(match.group(1))

    # 2. Services PMI
    if os.path.exists(SVC_PMI_FILE):
        with open(SVC_PMI_FILE, 'r') as f:
            content = f.read()
            # Find servicesPmi: VALUE
            match = re.search(r'servicesPmi:\s*([0-9.]+)', content)
            if match:
                data['svc_pmi'] = float(match.group(1))

    # 3. Yield Curve (10Y - 2Y)
    if os.path.exists(YIELDS_FILE):
        with open(YIELDS_FILE, 'r') as f:
            content = f.read()
            # Look for id="kpi-spread">... bps</div>
            # Handles +73, -15, 73, etc.
            match = re.search(r'id="kpi-spread">\s*([+\-]?[\d.]+)\s*bps</div>', content)
            if match:
                # Convert bps to percentage for consistency (e.g. 73 bps -> 0.73%)
                val_bps = float(match.group(1))
                data['yield_spread_10y2y'] = val_bps / 100.0

    # 4. Consumer Sentiment
    if os.path.exists(SENTIMENT_FILE):
        with open(SENTIMENT_FILE, 'r') as f:
            content = f.read()
            # Extract from sentimentData array
            # Array built ascending: { month: "...", index: ... }
            # So we want the LAST occurrence
            matches = re.findall(r'index:\s*([0-9.]+)', content)
            if matches:
                data['consumer_sentiment'] = float(matches[-1])

    # 5. Corporate Bond Spreads (Credit Risk Premium: BBB - AAA)
    if os.path.exists(BONDS_FILE):
        with open(BONDS_FILE, 'r') as f:
            content = f.read()
            # Parse the JSON data arrays directly to get the latest values
            # const aaaFullData = [...];
            aaa_match = re.search(r'const aaaFullData = (\[.*?\]);', content, re.DOTALL)
            bbb_match = re.search(r'const bbbFullData = (\[.*?\]);', content, re.DOTALL)
            
            if aaa_match and bbb_match:
                try:
                    aaa_list = json.loads(aaa_match.group(1))
                    bbb_list = json.loads(bbb_match.group(1))
                    
                    if aaa_list and bbb_list:
                        # Ensure we get the latest non-null values
                        latest_aaa = aaa_list[-1].get('value')
                        latest_bbb = bbb_list[-1].get('value')
                        
                        if latest_aaa is not None and latest_bbb is not None:
                            data['credit_spread_bbb_aaa'] = round(latest_bbb - latest_aaa, 2)
                except Exception as e:
                    print(f"Error parsing bond data: {e}")


    # 6. Building Permits
    if os.path.exists(PERMITS_FILE):
        with open(PERMITS_FILE, 'r') as f:
            content = f.read()
            # Look for id="kpi-total">1330k</div>
            match = re.search(r'id="kpi-total">\s*([\d.]+)k</div>', content)
            if match:
                data['housing_permits'] = float(match.group(1))

    # 7. Small Business Optimism
    if os.path.exists(OPTIMISM_FILE):
        with open(OPTIMISM_FILE, 'r') as f:
            content = f.read()
            # Matches { month: "...", index: ... }
            matches = re.findall(r'index:\s*([0-9.]+)', content)
            if matches:
                data['sb_optimism'] = float(matches[-1])
    return data

def determine_regime(data):
    # Fallback to sensible defaults if data missing, but we handle None check later
    mfg = data['mfg_pmi'] if data['mfg_pmi'] is not None else 50.0
    svc = data['svc_pmi'] if data['svc_pmi'] is not None else 50.0
    spread = data['yield_spread_10y2y'] if data['yield_spread_10y2y'] is not None else 0.0
    sentiment = data['consumer_sentiment'] if data['consumer_sentiment'] is not None else 75.0
    
    # 1. Contraction / Recession
    # Both PMIs contracting or deeply inverted curve with contracting Mfg
    if (mfg < 50 and svc < 50) or (spread < -0.5 and mfg < 48):
        return "Contraction", "red"
        
    # 2. Slowdown
    # Services still expanding but Mfg contracting, Curve might be inverted or flat
    if mfg < 50 and svc >= 50:
        if spread < 0:
            return "Slowdown (Late Cycle)", "orange"
        else:
            return "Slowdown (Soft Landing)", "yellow"
            
    # 3. Recovery
    # Mfg bouncing back, Curve steepening
    if mfg >= 50 and spread > 0.2:
        return "Recovery", "blue"
        
    # 4. Expansion
    # Both expanding
    if mfg >= 50 and svc >= 50:
        return "Expansion", "green"
        
    return "Mixed Signals", "gray"

def generate_summary_html(data):
    regime, color_class = determine_regime(data)
    
    colors = {
        "red": "#ef4444", 
        "orange": "#f97316", 
        "yellow": "#eab308", 
        "green": "#22c55e", 
        "blue": "#3b82f6",
        "purple": "#a855f7",
        "gray": "#64748b"
    }
    theme_color = colors.get(color_class, "#64748b")
    
    # Helper to format and colorize values safely
    def fmt(val, type_fmt="normal", threshold=50, invert=False):
        if val is None:
            return "-", "#64748b"
        
        display_val = f"{val:.1f}" if type_fmt == "pct" else f"{val}"
        color = "#1e293b"
        
        if type_fmt == "pmi":
            color = "#22c55e" if val >= 50 else "#ef4444"
        elif type_fmt == "spread":
            color = "#22c55e" if val >= 0 else "#ef4444"
            display_val = f"{val:.2f}%"
        elif type_fmt == "sentiment":
            display_val = f"{val:.1f}"
            color = "#22c55e" if val >= 80 else "#ef4444" if val < 70 else "#eab308"
        elif type_fmt == "credit":
             # Credit Risk Premium (BBB - AAA) Zones
             # < 0.75%: Tight (Green) - Strong market confidence
             # 0.75% - 1.25%: Normal (Yellow) - Historical average
             # > 1.25%: Elevated (Red) - Rising stress
             display_val = f"{val:.2f}%"
             if val <= 0.75:
                 color = "#22c55e" # Green
             elif val <= 1.25:
                 color = "#eab308" # Yellow
             else:
                 color = "#ef4444" # Red
             

        elif type_fmt == "housing":
             # 1500+ Strong, 1300-1500 Neutral, <1300 Weak
             display_val = f"{val:,.0f}k"
             if val >= 1500:
                 color = "#22c55e"
             elif val >= 1300:
                 color = "#eab308"
             else:
                 color = "#ef4444"
             
        return display_val, color

    mfg_val, mfg_col = fmt(data['mfg_pmi'], "pmi")
    svc_val, svc_col = fmt(data['svc_pmi'], "pmi")
    yield_val, yield_col = fmt(data['yield_spread_10y2y'], "spread")
    sent_val, sent_col = fmt(data['consumer_sentiment'], "sentiment")
    credit_val, credit_col = fmt(data['credit_spread_bbb_aaa'], "credit")
    house_val, house_col = fmt(data['housing_permits'], "housing")
    sb_val, sb_col = fmt(data['sb_optimism'], "sentiment") # Use sentiment formatting for SBAC

    # Generate Dynamic Description
    desc_parts = []
    if data['mfg_pmi']:
        desc_parts.append(f"Manufacturing is <strong>{'expanding' if data['mfg_pmi'] >= 50 else 'contracting'}</strong> ({mfg_val})")
    if data['svc_pmi']:
        desc_parts.append(f"Services are <strong>{'expanding' if data['svc_pmi'] >= 50 else 'contracting'}</strong> ({svc_val})")
    
    if data['housing_permits']:
        h_trends = "robust" if data['housing_permits'] >= 1500 else "soft"
        housing_desc = f", and housing activity is <strong>{h_trends}</strong> ({house_val})"
    
    sb_desc = ""
    if data['sb_optimism']:
        sb_desc = f", Small Business Optimism is <strong>{'strong' if data['sb_optimism'] >= 98 else 'weak'}</strong> ({sb_val})"

    curve_desc = "inverted" if data['yield_spread_10y2y'] and data['yield_spread_10y2y'] < 0 else "normal"
    sent_desc = "Bearish"
    if data['consumer_sentiment']:
        if data['consumer_sentiment'] >= 80: sent_desc = "Bullish"
        elif data['consumer_sentiment'] >= 70: sent_desc = "Neutral"
    
    full_desc = f"The economy shows {', while '.join(desc_parts)}. The yield curve is <strong>{curve_desc}</strong>, consumer sentiment is <strong>{sent_desc}</strong> ({sent_val}){housing_desc}{sb_desc}."

    current_date = datetime.datetime.now().strftime('%b %d, %Y')
    
    html = f"""
    <div class="summary-section" style="max-width: 1200px; margin: 0 auto 40px auto; padding: 0 20px;">
        <div style="background: linear-gradient(to right, #ffffff, #f8fafc); border: 1px solid #e2e8f0; border-left: 6px solid {theme_color}; border-radius: 12px; padding: 30px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);">
            <div style="display: flex; gap: 40px; align-items: center; flex-wrap: wrap;">
                
                <!-- Main Status -->
                <div style="flex: 2; min-width: 300px;">
                    <div style="text-transform: uppercase; font-size: 0.85rem; font-weight: 700; color: {theme_color}; letter-spacing: 1px; margin-bottom: 8px;">Current Market Regime <span style="float: right; font-size: 0.75rem; color: #94a3b8; font-weight: 500; text-transform: none; letter-spacing: normal;">Last Updated: {current_date}</span></div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: #1e293b; margin-bottom: 15px; line-height: 1.1;">{regime}</div>
                    <p style="font-size: 1.1rem; color: #475569; line-height: 1.6; margin: 0;">{full_desc}</p>
                </div>

                <!-- Key Metrics Grid -->
                <div style="flex: 3; display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; min-width: 300px;">
                    
                    <a href="industry_heatmap.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">Manufacturing PMI</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {mfg_col};">{mfg_val}</div>
                    </a>

                    <a href="services_pmi.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">Services PMI</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {svc_col};">{svc_val}</div>
                    </a>

                    <a href="yield_curve.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">10Y-2Y Spread</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {yield_col};">{yield_val}</div>
                    </a>

                    <a href="consumer_sentiment.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">Sentiment</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {sent_col};">{sent_val}</div>
                    </a>

                    <a href="corporate_bonds.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">Credit Premium</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {credit_col};">{credit_val}</div>
                    </a>

                    <a href="building_permits.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">Housing Permits</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {house_col};">{house_val}</div>
                    </a>

                    <a href="small_business_optimism.html" style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; text-align: center; text-decoration: none; display: block; color: inherit; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                        <div style="font-size: 0.8rem; color: #64748b; font-weight: 600; margin-bottom: 5px;">SB Optimism</div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: {sb_col};">{sb_val}</div>
                    </a>

                </div>
            </div>
        </div>
    </div>
    """
    return html

def update_index_page(html_content):
    if not os.path.exists(INDEX_FILE):
        print("Index file not found!")
        return

    with open(INDEX_FILE, 'r') as f:
        content = f.read()

    full_html_block = f"<!-- Executive Summary Section -->\n{html_content}\n<!-- End Executive Summary -->"

    # Check if we can find the existing block to replace in-place
    if '<!-- Executive Summary Section -->' in content and '<!-- End Executive Summary -->' in content:
        content = re.sub(r'<!-- Executive Summary Section -->.*?<!-- End Executive Summary -->', full_html_block, content, flags=re.DOTALL)
        print("Updated existing Executive Summary in place.")
    else:
        # Fallback: Insert after header section
        if '</section>' in content and 'class="header-section"' in content:
             content = content.replace('</section>', f'</section>\n\n    {full_html_block}\n    <!-- Section Divider -->\n    <div style="border-top: 1px solid #e2e8f0; margin: 40px auto; max-width: 1200px;"></div>')
        elif '</body>' in content:
             content = content.replace('</body>', f'{full_html_block}\n</body>')

    with open(INDEX_FILE, 'w') as f:
        f.write(content)
    
    print("Successfully updated Index page with Executive Summary.")

if __name__ == "__main__":
    print("Generating Executive Summary...")
    data = get_market_data()
    print("Market Data Collected:", json.dumps(data, indent=2))
    
    # Proceed even if some data is None (will show as '-')
    html = generate_summary_html(data)
    update_index_page(html)
