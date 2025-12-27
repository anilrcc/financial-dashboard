#!/usr/bin/env python3
"""
Create a unified COT page with tabs for all commodities
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .back-link {{
            display: inline-block;
            color: white;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            transition: all 0.3s;
        }}

        .back-link:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateX(-5px);
        }}

        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .tab {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 0.95rem;
        }}

        .tab:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}

        .tab.active {{
            background: white;
            color: #667eea;
            border-color: white;
        }}

        .card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin-bottom: 30px;
        }}

        .chart-container {{
            position: relative;
            height: 500px;
            margin-top: 20px;
        }}

        .info-text {{
            color: #64748b;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-top: 20px;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
        }}

        .time-btn {{
            background: white;
            border: 2px solid #667eea;
            color: #667eea;
            padding: 8px 20px;
            margin: 0 5px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }}

        .time-btn:hover {{
            background: #f0f4ff;
        }}

        .time-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: transparent;
        }}

        .commodity-view {{
            display: none;
        }}

        .commodity-view.active {{
            display: block;
        }}
    </style>
</head>

<body>
    <div class="container">
        <a href="index.html" class="back-link">← Back to Financial Dashboard</a>

        <div class="header">
            <h1>📊 Commitment of Traders</h1>
            <p>Managed Money Net Position (% of Open Interest)</p>
        </div>

        <!-- Commodity Tabs -->
        <div class="tabs">
{tabs}
        </div>

        <!-- Commodity Views -->
{views}
    </div>

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
            document.getElementById(commodityId + '-view').classList.add('active');

            // Update tab states
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelector(`[data-commodity="${{commodityId}}"]`).classList.add('active');

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
            const ctx = document.getElementById(canvasId).getContext('2d');

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
                                return value >= 0 ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)';
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
                            display: true,
                            position: 'top'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function (context) {{
                                    const dataPoint = data[context.dataIndex];
                                    return [
                                        `Net % OI: ${{dataPoint.net_pct_oi.toFixed(2)}}%`,
                                        `Long: ${{dataPoint.mm_long.toLocaleString()}}`,
                                        `Short: ${{dataPoint.mm_short.toLocaleString()}}`,
                                        `Open Interest: ${{dataPoint.open_interest.toLocaleString()}}`
                                    ];
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            type: 'time',
                            time: {{
                                unit: 'year',
                                displayFormats: {{
                                    year: 'yyyy'
                                }}
                            }},
                            title: {{
                                display: true,
                                text: 'Date'
                            }},
                            grid: {{
                                display: false
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Net Position (% of Open Interest)'
                            }},
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.05)'
                            }},
                            ticks: {{
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

            // Update button states
            document.querySelectorAll('.time-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');

            // Get data for current commodity
            const data = window[currentCommodity + 'Data'];
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
                f'            <div class="tab" data-commodity="{commodity["id"]}" onclick="showCommodity(\'{commodity["id"]}\')">'
                f'{commodity["icon"]} {commodity["name"]}</div>'
            )
    
    # Generate views HTML
    views_html = []
    for commodity in COMMODITIES:
        data_file = f"{commodity['id']}_cot_data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            start_year = data[0]['date'][:4]
            
            view_html = f'''        <div id="{commodity['id']}-view" class="commodity-view">
            <div class="card">
                <h2 style="text-align: center; margin-bottom: 20px; color: #1e293b;">
                    {commodity['icon']} {commodity['name']} | {start_year} - Present
                </h2>
                
                <!-- Time Period Buttons -->
                <div style="text-align: center; margin-bottom: 20px;">
                    <button class="time-btn active" onclick="updateChart('ALL')">ALL</button>
                    <button class="time-btn" onclick="updateChart('5Y')">5Y</button>
                    <button class="time-btn" onclick="updateChart('1Y')">1Y</button>
                </div>

                <div class="chart-container">
                    <canvas id="{commodity['id']}-chart"></canvas>
                </div>

                <div class="info-text">
                    <strong>About this chart:</strong> This shows the net position of Managed Money traders (hedge funds,
                    CTAs, etc.) as a percentage of total open interest in {commodity['name'].lower()} futures.
                    Positive values indicate net long positions (bullish), while negative values indicate net short
                    positions (bearish). Data source: CFTC Disaggregated Commitments of Traders Report.
                </div>
            </div>
        </div>'''
            
            views_html.append(view_html)
    
    # Generate script tags
    scripts_html = []
    for commodity in COMMODITIES:
        data_file = f"{commodity['id']}_cot_data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
            scripts_html.append(f'    <script>const {commodity["id"]}Data = {json.dumps(data)};</script>')
    
    # Generate final HTML
    html = HTML_TEMPLATE.format(
        tabs='\n'.join(tabs_html),
        views='\n'.join(views_html),
        scripts='\n'.join(scripts_html)
    )
    
    # Save
    with open('cot_reports.html', 'w') as f:
        f.write(html)
    
    print("✓ Generated cot_reports.html with tabs for all commodities")

if __name__ == '__main__':
    print("\n" + "="*80)
    print("GENERATING UNIFIED COT PAGE")
    print("="*80)
    print()
    
    generate_unified_page()
    
    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
