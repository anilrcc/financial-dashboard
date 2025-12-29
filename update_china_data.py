
import os
import json
import datetime

# --- Data Source ---
# Historical data compiled from NBS and Caixin reports (2020-2025)
# Last updated: Dec 2025

# Dates (Matches the data points below)
dates_2020 = [f"2020-{m:02d}" for m in range(1, 13)]
dates_2021 = [f"2021-{m:02d}" for m in range(1, 13)]
dates_2022 = [f"2022-{m:02d}" for m in range(1, 13)]
dates_2023 = [f"2023-{m:02d}" for m in range(1, 13)]
dates_2024 = [f"2024-{m:02d}" for m in range(1, 13)]
dates_2025 = [f"2025-{m:02d}" for m in range(1, 12)] # Up to Nov

all_dates = dates_2020 + dates_2021 + dates_2022 + dates_2023 + dates_2024 + dates_2025

# NBS Official Manufacturing PMI
nbs_2020 = [50.0, 35.7, 52.0, 50.8, 50.6, 50.9, 51.1, 51.0, 51.5, 51.4, 52.1, 51.9]
nbs_2021 = [51.3, 50.6, 51.9, 51.1, 49.7, 50.9, 50.4, 50.1, 49.6, 49.2, 50.1, 50.3]
nbs_2022 = [50.1, 50.2, 49.5, 47.4, 49.6, 50.2, 49.0, 49.4, 50.1, 49.2, 48.0, 47.0]
nbs_2023 = [50.1, 52.6, 51.9, 49.2, 48.8, 49.0, 49.3, 49.7, 50.2, 49.5, 49.4, 49.0]
nbs_2024 = [49.2, 49.1, 50.8, 50.4, 49.5, 49.5, 49.4, 49.1, 49.8, 50.1, 50.3, 50.1]
nbs_2025 = [49.1, 50.2, 50.5, 49.0, 49.5, 49.7, 49.3, 49.4, 49.8, 49.0, 49.2]

nbs_data = nbs_2020 + nbs_2021 + nbs_2022 + nbs_2023 + nbs_2024 + nbs_2025

# Caixin China General Manufacturing PMI
caixin_2020 = [51.1, 40.3, 50.1, 49.4, 50.7, 51.2, 52.8, 53.1, 54.8, 53.6, 54.9, 53.0]
caixin_2021 = [51.5, 50.9, 50.6, 51.9, 52.0, 51.3, 50.3, 49.2, 50.0, 50.6, 49.9, 50.9]
caixin_2022 = [49.1, 50.4, 48.1, 46.0, 48.1, 51.7, 50.4, 49.5, 48.1, 49.2, 49.4, 49.0]
caixin_2023 = [49.2, 51.6, 50.0, 49.5, 50.9, 50.5, 49.2, 51.0, 50.6, 49.5, 50.7, 50.8]
caixin_2024 = [50.8, 50.9, 51.1, 51.4, 51.7, 51.8, 49.8, 50.4, 49.3, 50.3, 51.5, 50.8]
caixin_2025 = [50.1, 50.8, 51.2, 50.4, 48.3, 50.4, 49.5, 50.5, 51.2, 50.6, 49.9]

caixin_data = caixin_2020 + caixin_2021 + caixin_2022 + caixin_2023 + caixin_2024 + caixin_2025

# Validate lengths
assert len(all_dates) == len(nbs_data) == len(caixin_data), "Data Integration Error: Array lengths mismatch"

# Create Table Data (Reverse Order for Display)
table_data = []
for i in range(len(all_dates) - 1, -1, -1):
    table_data.append({
        "date": datetime.datetime.strptime(all_dates[i], "%Y-%m").strftime("%b %Y"),
        "nbs": nbs_data[i],
        "caixin": caixin_data[i]
    })

# --- Insight Generation ---
latest_nbs = nbs_data[-1]
prev_nbs = nbs_data[-2]
latest_caixin = caixin_data[-1]
prev_caixin = caixin_data[-2]
latest_date = datetime.datetime.strptime(all_dates[-1], "%Y-%m").strftime("%b %Y")

def get_trend_text(curr, prev):
    diff = curr - prev
    if diff > 0.5: return "improved", "green"
    if diff < -0.5: return "deteriorated", "red"
    return "remained stable", "gray"

nbs_trend_text, _ = get_trend_text(latest_nbs, prev_nbs)
caixin_trend_text, _ = get_trend_text(latest_caixin, prev_caixin)

insight_html = f"""
<h3>China Manufacturing Overview</h3>
<p>In {latest_date}, the <strong>Official NBS Manufacturing PMI</strong> {nbs_trend_text} to <strong>{latest_nbs}</strong>, while the <strong>Caixin Manufacturing PMI</strong> {caixin_trend_text} to <strong>{latest_caixin}</strong>.</p>
<p>The divergence between the two indices often reflects the performance gap between large state-owned enterprises (NBS) and smaller private-sector exporters (Caixin).</p>
"""

# --- HTML Template ---
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>China PMI Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }}
        .header-section {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #f1f5f9; }}
        .back-link {{ text-decoration: none; color: #64748b; font-weight: 500; display: inline-flex; align-items: center; gap: 8px; font-size: 0.95rem; transition: color 0.2s; }}
        .back-link:hover {{ color: #1e293b; }}
        .page-title {{ font-size: 2.5rem; font-weight: 900; margin: 0; background-image: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); background-clip: text; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .summary-box {{ background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .summary-box h3 {{ margin-top: 0; font-size: 1.1rem; color: #334155; margin-bottom: 15px; font-weight: 700; }}
        .summary-box p {{ margin: 0 0 10px 0; color: #475569; line-height: 1.6; }}
        .charts-section {{ display: grid; grid-template-columns: 1fr; gap: 25px; margin-bottom: 25px; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; margin-bottom: 50px; }}
        @media (max-width: 768px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
        .chart-card {{ background: white; padding: 25px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); height: 400px; position: relative; }}
        canvas {{ width: 100% !important; height: 100% !important; }}
        .table-container {{ overflow-x: auto; background: white; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 50px; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 600px; font-size: 0.9rem; }}
        th, td {{ padding: 16px 24px; text-align: center; border-bottom: 1px solid #f1f5f9; white-space: nowrap; }}
        th {{ background-color: #f8fafc; font-weight: 600; color: #475569; position: sticky; top: 0; }}
        tbody tr:hover {{ background-color: #f8fafc; }}
        .footer {{ text-align: center; margin-top: 50px; font-size: 0.85rem; color: #94a3b8; }}
        .pmi-badge {{ padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }}
        .pmi-exp {{ background-color: #dcfce7; color: #166534; }}
        .pmi-con {{ background-color: #fee2e2; color: #991b1b; }}
        .pmi-neu {{ background-color: #f1f5f9; color: #64748b; }}
    </style>
</head>
<body>
    <div class="header-section">
        <div style="flex: 1;">
            <a href="index.html" class="back-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="feather"><path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Back to Dashboard
            </a>
        </div>
        <div style="flex: 2; text-align: center;">
            <h1 class="page-title">China PMI Monitor</h1>
        </div>
        <div style="flex: 1; text-align: right;">
            <div style="font-size: 0.85rem; color: #64748b; font-weight: 500;">Last Updated</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #334155;">{today}</div>
        </div>
    </div>

    <!-- Insights -->
    <div class="summary-box">
        {insight}
    </div>

    <!-- Main Comparison Chart -->
    <div class="charts-section">
        <div class="chart-card">
            <canvas id="mainChart"></canvas>
        </div>
    </div>

    <!-- Individual Charts -->
    <div class="charts-grid">
        <div class="chart-card">
            <canvas id="nbsChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="caixinChart"></canvas>
        </div>
    </div>

    <!-- Detailed Table -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th style="text-align: left;">Date</th>
                    <th>Official NBS PMI</th>
                    <th>Caixin PMI</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Data Sources: National Bureau of Statistics (NBS) & Caixin/S&P Global</p>
    </div>

    <script>
        const dates = {dates_json};
        const nbsData = {nbs_json};
        const caixinData = {caixin_json};
        const neutralLine = Array(dates.length).fill(50);

        // Common Options
        const commonOptions = (title, color) => ({{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{
                title: {{ display: true, text: title }},
                legend: {{ position: 'top' }},
                tooltip: {{ callbacks: {{ label: (c) => c.dataset.label + ': ' + c.parsed.y }} }}
            }},
            scales: {{
                y: {{ min: 30, max: 60, grid: {{ color: '#f1f5f9' }} }},
                x: {{ grid: {{ display: false }} }}
            }}
        }});

        // 1. Comparison Chart
        new Chart(document.getElementById('mainChart').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Official NBS PMI',
                        data: nbsData,
                        borderColor: '#ef4444', 
                        backgroundColor: '#ef4444',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    }},
                    {{
                        label: 'Caixin PMI',
                        data: caixinData,
                        borderColor: '#f59e0b', 
                        backgroundColor: '#f59e0b',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    }},
                    {{
                        label: '50 Neutral',
                        data: neutralLine,
                        borderColor: '#94a3b8',
                        borderWidth: 1,
                        borderDash: [4, 4],
                        pointRadius: 0,
                        fill: false
                    }}
                ]
            }},
            options: commonOptions('Comparison: NBS vs Caixin (2020-2025)')
        }});

        // 2. Official NBS Chart
        new Chart(document.getElementById('nbsChart').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Official NBS PMI',
                        data: nbsData,
                        borderColor: '#ef4444', 
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2,
                        fill: true
                    }},
                    {{
                        label: '50 Neutral',
                        data: neutralLine,
                        borderColor: '#94a3b8',
                        borderWidth: 1,
                        borderDash: [4, 4],
                        pointRadius: 0
                    }}
                ]
            }},
            options: commonOptions('Official NBS Manufacturing PMI')
        }});

        // 3. Caixin Chart
        new Chart(document.getElementById('caixinChart').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [
                    {{
                        label: 'Caixin PMI',
                        data: caixinData,
                        borderColor: '#f59e0b', 
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2,
                        fill: true
                    }},
                    {{
                        label: '50 Neutral',
                        data: neutralLine,
                        borderColor: '#94a3b8',
                        borderWidth: 1,
                        borderDash: [4, 4],
                        pointRadius: 0
                    }}
                ]
            }},
            options: commonOptions('Caixin China General Manufacturing PMI')
        }});
    </script>
</body>
</html>
"""

# Generate Rows
rows_html = ""
for row in table_data:
    nbs_val = row['nbs']
    caixin_val = row['caixin']
    
    def get_badge(val):
        if val > 50: return f'<span class="pmi-badge pmi-exp">{val}</span>'
        if val < 50: return f'<span class="pmi-badge pmi-con">{val}</span>'
        return f'<span class="pmi-badge pmi-neu">{val}</span>'

    rows_html += f"""
    <tr>
        <td style="text-align: left; font-weight: 600;">{row['date']}</td>
        <td>{get_badge(nbs_val)}</td>
        <td>{get_badge(caixin_val)}</td>
    </tr>
    """

today_str = datetime.datetime.now().strftime("%b %d, %Y")

final_html = html_template.format(
    today=today_str,
    insight=insight_html,
    table_rows=rows_html,
    dates_json=json.dumps(all_dates),
    nbs_json=json.dumps(nbs_data),
    caixin_json=json.dumps(caixin_data)
)

output_file = 'china_pmi.html'
with open(output_file, 'w') as f:
    f.write(final_html)

print(f"Successfully generated {output_file} with comprehensive historical data.")
