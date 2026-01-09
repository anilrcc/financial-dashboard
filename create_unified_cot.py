#!/usr/bin/env python3
"""
Create a unified COT page with tabs for all commodities
Congruent with the website's clean, professional aesthetic.
"""

import json
import os

COMMODITIES = [
    {'id': 'copper', 'name': 'Copper', 'icon': '🔩'},
    {'id': 'gold', 'name': 'Gold', 'icon': '🥇'},
    {'id': 'silver', 'name': 'Silver', 'icon': '🥈'},
    {'id': 'platinum', 'name': 'Platinum', 'icon': '⚪'},
    {'id': 'palladium', 'name': 'Palladium', 'icon': '⚫'},
    {'id': 'aluminum', 'name': 'Aluminum', 'icon': '🔘'},
    {'id': 'lumber', 'name': 'Lumber', 'icon': '🪵'},
    {'id': 'steel_hrc', 'name': 'Steel HRC', 'icon': '🏗️'},
    {'id': 'steel_euro', 'name': 'North Euro Steel', 'icon': '🔩'},
]

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Commitment of Traders - Market Pulse</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        :root {{
            --primary-bg: #f8fafc;
            --text-main: #1e293b;
            --text-secondary: #64748b;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --hover-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--primary-bg);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .header-section {{
            width: 100%;
            background: #fff;
            border-bottom: 1px solid var(--border-color);
            padding: 60px 20px;
            text-align: center;
            margin-bottom: 40px;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin: 0 0 10px 0;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .subtitle {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            font-weight: 400;
            max-width: 600px;
            margin: 0 auto;
        }}

        .back-nav {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            width: 100%;
        }}

        .back-link {{
            color: var(--accent-blue);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
        }}

        .back-link:hover {{
            transform: translateX(-4px);
        }}

        .tabs-container {{
            background: white;
            padding: 10px;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            margin-bottom: 30px;
            overflow-x: auto;
        }}

        .tabs {{
            display: flex;
            gap: 8px;
            min-width: max-content;
        }}

        .tab {{
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--text-secondary);
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .tab:hover {{
            background: #f1f5f9;
            color: var(--text-main);
        }}

        .tab.active {{
            background: #eff6ff;
            color: var(--accent-blue);
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .card-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-main);
        }}

        .time-filters {{
            display: flex;
            background: #f1f5f9;
            padding: 4px;
            border-radius: 10px;
            gap: 4px;
        }}

        .time-btn {{
            padding: 6px 16px;
            border-radius: 8px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .time-btn:hover {{
            color: var(--text-main);
        }}

        .time-btn.active {{
            background: white;
            color: var(--accent-blue);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        .chart-container {{
            position: relative;
            height: 550px;
            width: 100%;
        }}

        .info-box {{
            margin-top: 30px;
            padding: 20px;
            background: #f8fafc;
            border-left: 4px solid var(--accent-blue);
            border-radius: 8px;
            line-height: 1.6;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}

        .info-box strong {{
            color: var(--text-main);
            display: block;
            margin-bottom: 5px;
        }}

        .commodity-view {{
            display: none;
        }}

        .commodity-view.active {{
            display: block;
        }}

        @media (max-width: 768px) {{
            .card-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .time-filters {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>

<body>
    <header class="header-section">
        <div class="container" style="padding: 0;">
            <a href="index.html" class="back-link" style="margin-bottom: 30px;">← Back to Financial Dashboard</a>
            <h1>Commitment of Traders</h1>
            <p class="subtitle">Institutional sentiment analysis of commodity futures through Managed Money net positioning.</p>
        </div>
    </header>

    <main class="container">
        <!-- Commodity Tabs -->
        <div class="tabs-container">
            <div class="tabs">
{tabs}
            </div>
        </div>

        <!-- Commodity Views -->
{views}
    </main>

    <!-- Load all commodity data -->
{scripts}

    <script>
        let currentChart = null;
        let currentCommodity = 'copper';
        let currentPeriod = 'ALL';

        function showCommodity(commodityId) {{
            // Hide all views
            document.querySelectorAll('.commodity-view').forEach(view => {{
                view.classList.remove('active');
            }});

            // Show selected view
            const selectedView = document.getElementById(commodityId + '-view');
            if (selectedView) {{
                selectedView.classList.add('active');
            }}

            // Update tab states
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            const activeTab = document.querySelector(`[data-commodity="${{commodityId}}"]`);
            if (activeTab) {{
                activeTab.classList.add('active');
            }}

            // Scroll tab into view if needed
            if (activeTab) {{
                activeTab.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
            }}

            // Update current commodity and recreate chart
            currentCommodity = commodityId;
            updateChart(currentPeriod);
        }}

        function filterDataByPeriod(data, period) {{
            if (period === 'ALL') {{
                return data;
            }}

            const now = new Date(data[data.length - 1].date);
            const cutoffDate = new Date(now);

            if (period === '1Y') {{
                cutoffDate.setFullYear(now.getFullYear() - 1);
            }} else if (period === '5Y') {{
                cutoffDate.setFullYear(now.getFullYear() - 5);
            }}

            return data.filter(d => new Date(d.date) >= cutoffDate);
        }}

        function createChart(data, canvasId) {{
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            if (currentChart) {{
                currentChart.destroy();
            }}

            currentChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: data.map(d => d.date),
                    datasets: [{{
                        label: 'Managed Money Net % OI',
                        data: data.map(d => d.net_pct_oi),
                        segment: {{
                            borderColor: ctx => {{
                                const value = ctx.p1.parsed.y;
                                return value >= 0 ? '#22c55e' : '#ef4444';
                            }},
                            backgroundColor: ctx => {{
                                const value = ctx.p1.parsed.y;
                                return value >= 0 ? 'rgba(34, 197, 94, 0.08)' : 'rgba(239, 68, 68, 0.08)';
                            }}
                        }},
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        intersect: false,
                        mode: 'index'
                    }},
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            titleColor: '#1e293b',
                            bodyColor: '#475569',
                            borderColor: '#e2e8f0',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: true,
                            callbacks: {{
                                title: function(context) {{
                                    return new Date(context[0].parsed.x).toLocaleDateString(undefined, {{ year: 'numeric', month: 'long', day: 'numeric' }});
                                }},
                                label: function (context) {{
                                    const dataPoint = data[context.dataIndex];
                                    return [
                                        `Net % OI: ${{dataPoint.net_pct_oi.toFixed(2)}}%`,
                                        `Long Positions: ${{dataPoint.mm_long.toLocaleString()}}`,
                                        `Short Positions: ${{dataPoint.mm_short.toLocaleString()}}`,
                                        `Total Open Interest: ${{dataPoint.open_interest.toLocaleString()}}`
                                    ];
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            type: 'time',
                            time: {{
                                unit: data.length > 500 ? 'year' : 'month',
                                displayFormats: {{
                                    month: 'MMM yyyy',
                                    year: 'yyyy'
                                }}
                            }},
                            grid: {{
                                display: false
                            }},
                            ticks: {{
                                color: '#94a3b8',
                                font: {{ size: 11 }}
                            }}
                        }},
                        y: {{
                            grid: {{
                                color: '#f1f5f9'
                            }},
                            ticks: {{
                                color: '#94a3b8',
                                font: {{ size: 11 }},
                                callback: function (value) {{
                                    return value.toFixed(0) + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function updateChart(period) {{
            currentPeriod = period;

            // Update button states in all views (to keep them in sync or just the active one)
            document.querySelectorAll('.time-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.getAttribute('data-period') === period) {{
                    btn.classList.add('active');
                }}
            }});

            // Get data for current commodity
            const data = window[currentCommodity + 'Data'];
            if (!data) return;

            const filteredData = filterDataByPeriod(data, period);
            const canvasId = currentCommodity + '-chart';
            
            createChart(filteredData, canvasId);
        }}

        // Initialize with copper
        window.addEventListener('DOMContentLoaded', () => {{
            showCommodity('copper');
        }});
    </script>
</body>
</html>'''

def generate_unified_page():
    """Generate unified COT page with tabs"""
    
    # Generate tabs HTML
    tabs_html = []
    for commodity in COMMODITIES:
        data_file = f"{commodity['id']}_cot_data.json"
        if os.path.exists(data_file):
            tabs_html.append(
                f'                <div class="tab" data-commodity="{commodity["id"]}" onclick="showCommodity(\'{commodity["id"]}\')">'
                f'{commodity["icon"]} {commodity["name"]}</div>'
            )
    
    # Generate views HTML
    views_html = []
    for commodity in COMMODITIES:
        data_file = f"{commodity['id']}_cot_data.json"
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                start_year = data[0]['date'][:4]
                
                view_html = f'''        <div id="{commodity['id']}-view" class="commodity-view">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">{commodity['icon']} {commodity['name']} Sentiment <span style="font-weight: 400; color: var(--text-secondary); font-size: 0.9rem; margin-left: 10px;">({start_year} - Present)</span></h2>
                    <div class="time-filters">
                        <button class="time-btn" data-period="ALL" onclick="updateChart('ALL')">ALL</button>
                        <button class="time-btn" data-period="5Y" onclick="updateChart('5Y')">5Y</button>
                        <button class="time-btn" data-period="1Y" onclick="updateChart('1Y')">1Y</button>
                    </div>
                </div>

                <div class="chart-container">
                    <canvas id="{commodity['id']}-chart"></canvas>
                </div>

                <div class="info-box">
                    <strong>About Managed Money Net Position</strong>
                    This indicator calculates the net position (Longs minus Shorts) of "Managed Money" traders as a percentage of total open interest. 
                    Managed Money includes hedge funds and commodity trading advisors whose positioning often drives momentum. 
                    <span style="color: var(--accent-green); font-weight: 600;">Positive values</span> indicate a net long (bullish) positioning, while 
                    <span style="color: var(--accent-red); font-weight: 600;">negative values</span> show a net short (bearish) positioning.
                </div>
            </div>
        </div>'''
                views_html.append(view_html)
            except Exception as e:
                print(f"Error processing {commodity['id']}: {e}")
    
    # Generate script tags
    scripts_html = []
    for commodity in COMMODITIES:
        data_file = f"{commodity['id']}_cot_data.json"
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                scripts_html.append(f'    <script>window.{commodity["id"]}Data = {json.dumps(data)};</script>')
            except Exception as e:
                print(f"Error loading data for script {commodity['id']}: {e}")
    
    # Generate final HTML
    html = HTML_TEMPLATE.format(
        tabs='\n'.join(tabs_html),
        views='\n'.join(views_html),
        scripts='\n'.join(scripts_html)
    )
    
    # Save
    with open('cot_reports.html', 'w') as f:
        f.write(html)
    
    print("✓ Generated premium cot_reports.html with unified design")

if __name__ == '__main__':
    print("\n" + "="*80)
    print("GENERATING PREMIUM UNIFIED COT PAGE")
    print("="*80)
    print()
    
    generate_unified_page()
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
