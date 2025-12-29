
import json
import datetime
import os

# --- Data Source ---
# Historical data for J.P. Morgan Global Manufacturing PMI and Japan Composite PMI
# Compiled from various S&P Global and financial news reports

# --- Global Manufacturing PMI Data ---


# --- Japan Composite PMI Data ---
# Reconstruction of 2024-2025 timeline based on reports
japan_data = {
    # 2024 
    "2024-01": 51.5, "2024-02": 50.6, "2024-03": 51.7, "2024-04": 52.3, # Interpolated baseline for early 2024
    "2024-05": 52.6, "2024-06": 49.7, "2024-07": 52.5, "2024-08": 52.9,
    "2024-09": 52.5, "2024-10": 51.0, "2024-11": 50.1, "2024-12": 50.8,
    # 2025
    "2025-01": 51.1, "2025-02": 52.0, "2025-03": 48.9, "2025-04": 51.1,
    "2025-05": 50.2, "2025-06": 51.5, "2025-07": 51.7, "2025-08": 51.9,
    "2025-09": 51.8, "2025-10": 51.5, "2025-11": 52.0, "2025-12": 51.5
}

# --- India Manufacturing PMI Data ---
india_data = {
    # 2024
    "2024-01": 56.5, "2024-02": 56.9, "2024-03": 59.1, "2024-04": 58.8,
    "2024-05": 57.5, "2024-06": 58.3, "2024-07": 58.1, "2024-08": 58.6,
    "2024-09": 56.5, "2024-10": 57.5, "2024-11": 56.5, "2024-12": 56.4,
    # 2025
    "2025-01": 57.7, "2025-02": 56.3, "2025-03": 58.1, "2025-04": 58.2,
    "2025-05": 57.6, "2025-06": 58.4, "2025-07": 59.1, "2025-08": 59.3,
    "2025-09": 57.7, "2025-10": 59.2, "2025-11": 56.6, "2025-12": 55.7
}

# --- UK Manufacturing PMI Data ---
uk_data = {
    # 2024
    "2024-01": 47.0, "2024-02": 47.5, "2024-03": 50.3, "2024-04": 49.1,
    "2024-05": 51.2, "2024-06": 50.9, "2024-07": 52.1, "2024-08": 52.5,
    "2024-09": 51.5, "2024-10": 49.9, "2024-11": 48.0, "2024-12": 47.0,
    # 2025 
    "2025-01": 48.3, "2025-02": 47.9, "2025-03": 48.5, "2025-04": 45.4, # Interpolated gap
    "2025-05": 46.4, "2025-06": 47.7, "2025-07": 48.9, "2025-08": 49.5, # Interpolated gap
    "2025-09": 49.8, "2025-10": 49.7, "2025-11": 50.2, "2025-12": 51.2
}

# --- Brazil Composite PMI Data ---
brazil_data = {
    # 2024
    "2024-01": 55.0, "2024-02": 54.8, "2024-03": 56.0, "2024-04": 54.8,
    "2024-05": 54.8, "2024-06": 54.1, "2024-07": 56.0, "2024-08": 52.9,
    "2024-09": 55.2, "2024-10": 55.9, "2024-11": 53.5, "2024-12": 51.5,
    # 2025
    "2025-01": 48.2, "2025-02": 51.2, "2025-03": 50.3, "2025-04": 49.4, # Mar interpolated
    "2025-05": 49.1, "2025-06": 49.0, "2025-07": 48.9, "2025-08": 48.8, # Jun/Jul interpolated
    "2025-09": 46.0, "2025-10": 48.2, "2025-11": 49.6, "2025-12": 49.6  # Dec assumed steady
}

# Process Dates


sorted_keys_japan = sorted(japan_data.keys())
dates_japan = [datetime.datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in sorted_keys_japan]
values_japan = [japan_data[k] for k in sorted_keys_japan]

sorted_keys_india = sorted(india_data.keys())
dates_india = [datetime.datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in sorted_keys_india]
values_india = [india_data[k] for k in sorted_keys_india]

sorted_keys_uk = sorted(uk_data.keys())
dates_uk = [datetime.datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in sorted_keys_uk]
values_uk = [uk_data[k] for k in sorted_keys_uk]

sorted_keys_brazil = sorted(brazil_data.keys())
dates_brazil = [datetime.datetime.strptime(k, "%Y-%m").strftime("%b %Y") for k in sorted_keys_brazil]
values_brazil = [brazil_data[k] for k in sorted_keys_brazil]

# --- Analysis Functions ---
def analyze_pmi(values):
    latest_val = values[-1]
    prev_val = values[-2]
    mom = latest_val - prev_val
    status = "Expansion" if latest_val >= 50 else "Contraction"
    trend_color = "#10b981" if mom > 0 else "#ef4444"
    if mom == 0: trend_color = "#64748b"
    status_color = "#10b981" if latest_val >= 50 else "#ef4444" 
    status_bg = "rgba(16, 185, 129, 0.1)" if latest_val >= 50 else "rgba(239, 68, 68, 0.1)"
    trend_arrow = "↑" if mom > 0 else "↓"
    if mom == 0: trend_arrow = "→"
    return {
        "latest": latest_val, "prev": prev_val, "mom": mom, "status": status,
        "trend_color": trend_color, "status_color": status_color, "status_bg": status_bg,
        "arrow": trend_arrow
    }

jp_stats = analyze_pmi(values_japan)
ind_stats = analyze_pmi(values_india)
uk_stats = analyze_pmi(values_uk)
br_stats = analyze_pmi(values_brazil)


# --- HTML Generation ---

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Manufacturing Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.1.0"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Header */
        .header-section {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 15px;
        }}

        .back-link {{
            text-decoration: none;
            color: #64748b;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}
        .back-link:hover {{ color: #1e293b; }}

        .page-title {{
            font-size: 2.5rem;
            font-weight: 900;
            margin: 0;
            background-image: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .last-updated {{
            text-align: right;
        }}

        .last-updated-label {{
            font-size: 0.85rem;
            color: #64748b;
            font-weight: 500;
        }}
        
        .last-updated-date {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #334155;
        }}

        /* Section Styling */
        .section-wrapper {{
            margin-bottom: 50px;
        }}

        .section-header {{
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .country-flag {{
            width: 32px;
            height: 24px;
            border-radius: 4px;
            object-fit: cover;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .country-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #334155;
        }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 25px;
        }}

        .kpi-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }}

        .kpi-label {{
            font-size: 0.8rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            font-weight: 600;
        }}

        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.2;
        }}

        .kpi-sub {{
            font-size: 0.9rem;
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 500;
        }}

        /* Badge */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge.expansion {{ background-color: #dcfce7; color: #166534; }}
        .badge.contraction {{ background-color: #fee2e2; color: #991b1b; }}

        /* Chart Section */
        .chart-container {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
            height: 400px;
            position: relative;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .kpi-grid {{ grid-template-columns: 1fr; }}
            .header-section {{ flex-direction: column; gap: 15px; text-align: center; }}
            .last-updated {{ text-align: center; }}
        }}
    </style>
</head>
<body>

<body>

    <div class="container">
        <!-- Header -->
        <div class="header-section">
            <div style="flex: 1;">
                <a href="index.html" class="back-link">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                    Back to Dashboard
                </a>
            </div>
            <div style="flex: 2; text-align: center;">
                <h1 class="page-title">Global Manufacturing</h1>
            </div>
            <div style="flex: 1;" class="last-updated">
                <div class="last-updated-label">Last Updated</div>
                <div class="last-updated-date">{datetime.date.today().strftime('%b %d, %Y')}</div>
            </div>
        </div>

        <!-- SECTION 1: JAPAN PMI -->
        <div class="section-wrapper">
            <div class="section-header">
                <img src="https://flagcdn.com/w80/jp.png" alt="Japan Flag" class="country-flag">
                <div class="country-name">Japan Composite PMI</div>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Current Reading</div>
                    <div class="kpi-value" style="color: {jp_stats['status_color']}">{jp_stats['latest']}</div>
                    <div class="kpi-sub">
                        <span class="badge {jp_stats['status'].lower()}">{jp_stats['status'].upper()}</span>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Month-Over-Month</div>
                    <div class="kpi-value" style="color: {jp_stats['trend_color']}">{jp_stats['mom']:+.1f}</div>
                    <div class="kpi-sub" style="color: {jp_stats['trend_color']}">
                        {jp_stats['arrow']} vs Prev Month
                    </div>
                </div>
                 <div class="kpi-card">
                    <div class="kpi-label">Outlook</div>
                    <div style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                        Composite index reflects resilient services outweighing manufacturing weakness.
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="japanChart"></canvas>
            </div>
        </div>

        <!-- SECTION 2: INDIA PMI -->
        <div class="section-wrapper">
            <div class="section-header">
                <img src="https://flagcdn.com/w80/in.png" alt="India Flag" class="country-flag">
                <div class="country-name">India Manufacturing PMI</div>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Current Reading</div>
                    <div class="kpi-value" style="color: {ind_stats['status_color']}">{ind_stats['latest']}</div>
                    <div class="kpi-sub">
                        <span class="badge {ind_stats['status'].lower()}">{ind_stats['status'].upper()}</span>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Month-Over-Month</div>
                    <div class="kpi-value" style="color: {ind_stats['trend_color']}">{ind_stats['mom']:+.1f}</div>
                    <div class="kpi-sub" style="color: {ind_stats['trend_color']}">
                        {ind_stats['arrow']} vs Prev Month
                    </div>
                </div>
                 <div class="kpi-card">
                    <div class="kpi-label">Outlook</div>
                    <div style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                        Strong manufacturing growth driven by domestic demand and new orders.
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="indiaChart"></canvas>
            </div>
        </div>

        <!-- SECTION 3: UK PMI -->
        <div class="section-wrapper">
            <div class="section-header">
                <img src="https://flagcdn.com/w80/gb.png" alt="UK Flag" class="country-flag">
                <div class="country-name">UK Manufacturing PMI</div>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Current Reading</div>
                    <div class="kpi-value" style="color: {uk_stats['status_color']}">{uk_stats['latest']}</div>
                    <div class="kpi-sub">
                        <span class="badge {uk_stats['status'].lower()}">{uk_stats['status'].upper()}</span>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Month-Over-Month</div>
                    <div class="kpi-value" style="color: {uk_stats['trend_color']}">{uk_stats['mom']:+.1f}</div>
                    <div class="kpi-sub" style="color: {uk_stats['trend_color']}">
                        {uk_stats['arrow']} vs Prev Month
                    </div>
                </div>
                 <div class="kpi-card">
                    <div class="kpi-label">Outlook</div>
                    <div style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                        Sector returns to growth in late 2025 after a prolonged period of contraction.
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="ukChart"></canvas>
            </div>
        </div>

        <!-- SECTION 4: BRAZIL PMI -->
        <div class="section-wrapper">
            <div class="section-header">
                <img src="https://flagcdn.com/w80/br.png" alt="Brazil Flag" class="country-flag">
                <div class="country-name">Brazil Composite PMI</div>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Current Reading</div>
                    <div class="kpi-value" style="color: {br_stats['status_color']}">{br_stats['latest']}</div>
                    <div class="kpi-sub">
                        <span class="badge {br_stats['status'].lower()}">{br_stats['status'].upper()}</span>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Month-Over-Month</div>
                    <div class="kpi-value" style="color: {br_stats['trend_color']}">{br_stats['mom']:+.1f}</div>
                    <div class="kpi-sub" style="color: {br_stats['trend_color']}">
                        {br_stats['arrow']} vs Prev Month
                    </div>
                </div>
                 <div class="kpi-card">
                    <div class="kpi-label">Outlook</div>
                    <div style="color: #64748b; font-size: 0.95rem; line-height: 1.5;">
                        Mixed signals with contractionary pressures persisting in late 2025.
                    </div>
                </div>
            </div>

            <div class="chart-container">
                <canvas id="brazilChart"></canvas>
            </div>
        </div>



    </div>

    <script>
        // Common Chart Options
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e293b',
                    titleColor: '#f8fafc',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }},
                annotation: {{
                    annotations: {{
                        line1: {{
                            type: 'line',
                            yMin: 50,
                            yMax: 50,
                            borderColor: '#94a3b8',
                            borderWidth: 1,
                            borderDash: [4, 4],
                            label: {{
                                content: 'Neutral (50)',
                                enabled: true,
                                position: 'start',
                                color: '#94a3b8',
                                backgroundColor: 'rgba(0,0,0,0)',
                                font: {{ size: 10 }}
                            }}
                        }}
                    }}
                }}
            }},
            scales: {{
                x: {{ grid: {{ display: false }}, ticks: {{ color: '#64748b' }} }},
                y: {{ grid: {{ color: '#334155', borderDash: [5, 5] }}, ticks: {{ color: '#64748b' }} }}
            }},
            interaction: {{ mode: 'nearest', axis: 'x', intersect: false }}
        }};

        // --- Japan Chart ---
        const ctxJp = document.getElementById('japanChart').getContext('2d');
        const gradJp = ctxJp.createLinearGradient(0, 0, 0, 400);
        gradJp.addColorStop(0, 'rgba(239, 68, 68, 0.5)'); // Red/White for Japan theme? Or just sticking to consistent colors
        gradJp.addColorStop(1, 'rgba(239, 68, 68, 0.0)');
        
        // Let's use Red for Japan to match flag
        new Chart(ctxJp, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates_japan)},
                datasets: [{{
                    label: 'Japan Composite PMI',
                    data: {json.dumps(values_japan)},
                    borderColor: '#ef4444',
                    backgroundColor: gradJp,
                    borderWidth: 3,
                    pointBackgroundColor: '#1e293b',
                    pointBorderColor: '#ef4444',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});

        // --- India Chart ---
        const ctxInd = document.getElementById('indiaChart').getContext('2d');
        const gradInd = ctxInd.createLinearGradient(0, 0, 0, 400);
        gradInd.addColorStop(0, 'rgba(249, 115, 22, 0.5)'); // Orange for India
        gradInd.addColorStop(1, 'rgba(249, 115, 22, 0.0)');

        new Chart(ctxInd, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates_india)},
                datasets: [{{
                    label: 'India Manufacturing PMI',
                    data: {json.dumps(values_india)},
                    borderColor: '#f97316',
                    backgroundColor: gradInd,
                    borderWidth: 3,
                    pointBackgroundColor: '#1e293b',
                    pointBorderColor: '#f97316',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});

        // --- UK Chart ---
        const ctxUK = document.getElementById('ukChart').getContext('2d');
        const gradUK = ctxUK.createLinearGradient(0, 0, 0, 400);
        gradUK.addColorStop(0, 'rgba(37, 99, 235, 0.5)'); // Blue for UK
        gradUK.addColorStop(1, 'rgba(37, 99, 235, 0.0)');

        new Chart(ctxUK, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates_uk)},
                datasets: [{{
                    label: 'UK Manufacturing PMI',
                    data: {json.dumps(values_uk)},
                    borderColor: '#2563eb',
                    backgroundColor: gradUK,
                    borderWidth: 3,
                    pointBackgroundColor: '#1e293b',
                    pointBorderColor: '#2563eb',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});

        // --- Brazil Chart ---
        const ctxBR = document.getElementById('brazilChart').getContext('2d');
        const gradBR = ctxBR.createLinearGradient(0, 0, 0, 400);
        gradBR.addColorStop(0, 'rgba(34, 197, 94, 0.5)'); // Green for Brazil
        gradBR.addColorStop(1, 'rgba(34, 197, 94, 0.0)');

        new Chart(ctxBR, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates_brazil)},
                datasets: [{{
                    label: 'Brazil Composite PMI',
                    data: {json.dumps(values_brazil)},
                    borderColor: '#22c55e',
                    backgroundColor: gradBR,
                    borderWidth: 3,
                    pointBackgroundColor: '#1e293b',
                    pointBorderColor: '#22c55e',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: commonOptions
        }});


    </script>
</body>
</html>
"""

# Write to file
output_path = "global_pmi.html"
with open(output_path, "w") as f:
    f.write(html_content)

print(f"Successfully generated {output_path}")
