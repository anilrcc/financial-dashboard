
import os

HTML_FILE = 'eurozone_pmi.html'

html_content = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eurozone Economic Indicators</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 20px;
        }

        /* Header & Nav */
        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f1f5f9;
        }

        .back-link {
            text-decoration: none;
            color: #64748b;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95rem;
            transition: color 0.2s;
            padding: 5px 0;
            margin-bottom: 15px;
            /* Spacing from title */
        }

        .back-link:hover {
            color: #1e293b;
        }

        .page-title {
            font-size: 2.5rem;
            font-weight: 900;
            margin: 0;
            background-image: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Region Tabs */
        .region-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 10px;
            overflow-x: auto;
        }

        .region-tab {
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            color: #64748b;
            transition: all 0.2s;
            border: 1px solid transparent;
        }

        .region-tab:hover {
            background-color: #e2e8f0;
            color: #1e293b;
        }

        .region-tab.active {
            background-color: #eff6ff;
            color: #2563eb;
            border-color: #bfdbfe;
        }

        /* Summary Box */
        .summary-box {
            background: white;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .summary-box h3 {
            margin-top: 0;
            font-size: 1.1rem;
            color: #334155;
            margin-bottom: 15px;
            font-weight: 700;
        }

        .summary-box p {
            margin: 0 0 10px 0;
            color: #475569;
            line-height: 1.6;
        }

        .summary-box p:last-child {
            margin-bottom: 0;
        }

        /* Charts Grid */
        .charts-section {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            /* Enforce 2 columns */
            gap: 25px;
            margin-bottom: 50px;
        }

        /* Make first chart big (ESI) */
        .chart-card:nth-child(1) {
            grid-column: 1 / -1;
            height: 500px;
        }

        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            height: 400px;
            /* Default height for others */
            position: relative;
        }

        canvas {
            width: 100% !important;
            height: 100% !important;
        }

        /* Chart Controls */
        .chart-controls {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 15px;
            gap: 8px;
        }

        .time-btn {
            background: white;
            border: 1px solid #cbd5e1;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #64748b;
            cursor: pointer;
            transition: all 0.2s;
        }

        .time-btn:hover {
            border-color: #94a3b8;
            color: #334155;
        }

        .time-btn.active {
            background: #1e293b;
            color: white;
            border-color: #1e293b;
        }


        /* Aesthetic Table */
        .table-container {
            overflow-x: auto;
            background: white;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
            margin-bottom: 50px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
            font-size: 0.9rem;
        }

        th,
        td {
            padding: 16px 24px;
            text-align: center;
            border-bottom: 1px solid #f1f5f9;
            font-feature-settings: "tnum";
            color: #475569;
            white-space: nowrap;
        }

        th {
            text-align: center;
            background-color: #f8fafc;
            font-weight: 600;
            color: #475569;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            z-index: 10;
            border-bottom: 1px solid #e2e8f0;
        }

        /* Sticky First Column */
        td:first-child,
        th:first-child {
            text-align: left;
            position: sticky;
            left: 0;
            z-index: 20;
            background-color: white;
            border-right: 1px solid #f1f5f9;
        }

        th:first-child {
            background-color: #f8fafc;
            z-index: 30;
        }

        /* Row Hover & Alternating */
        tbody tr {
            transition: background-color 0.15s ease;
        }

        tbody tr:hover {
            background-color: #f8fafc;
        }

        tbody tr:hover td:first-child {
            background-color: #f8fafc;
        }

        /* Metric Name Column Styling */
        td:first-child {
            font-weight: 600;
            color: #1e293b;
        }

        /* Last row border adjustments */
        tr:last-child td {
            border-bottom: none;
        }

        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 0.85rem;
            color: #94a3b8;
            padding-bottom: 20px;
        }
    </style>
</head>

<body>

    <div class="header-section">
        <div style="flex: 1;">
            <a href="index.html" class="back-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" class="feather">
                    <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
                Back to Dashboard
            </a>
        </div>
        <div style="flex: 2; text-align: center;">
            <h1 class="page-title">All Eurozone</h1>
        </div>
        <div style="flex: 1; text-align: right;">
            <div style="font-size: 0.85rem; color: #64748b; font-weight: 500;">Last Updated</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #334155;"><span id="last-updated-date">Dec 20,
                    2025</span></div>
        </div>
    </div>

    <!-- Region Tabs -->
    <div class="region-tabs">
        <div class="region-tab active" onclick="switchRegion('EA')">All Eurozone</div>
        <div class="region-tab" onclick="switchRegion('DE')">Germany</div>
        <div class="region-tab" onclick="switchRegion('FR')">France</div>
        <div class="region-tab" onclick="switchRegion('IT')">Italy</div>
        <div class="region-tab" onclick="switchRegion('ES')">Spain</div>
        <div class="region-tab" onclick="switchRegion('NL')">Netherlands</div>
    </div>

    <div id="euro-pmi-survey-insights" class="summary-box">
        <h3>Eurozone Overview</h3>
        <p>Loading...</p>
    </div>

    <!-- Chart Controls -->
    <div class="chart-controls">
        <button class="time-btn active" data-range="ALL">ALL</button>
        <button class="time-btn" data-range="5Y">5Y</button>
        <button class="time-btn" data-range="1Y">1Y</button>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
        <!-- Main Indicators -->
        <div class="chart-card">
            <canvas id="esiChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="eeiChart"></canvas>
        </div>

        <!-- Sector Confidence -->
        <div class="chart-card">
            <canvas id="manuChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="servChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="consChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="retaChart"></canvas>
        </div>
        <div class="chart-card">
            <canvas id="builChart"></canvas>
        </div>
    </div>

    <div class="table-container">
        <table id="euroPmiTable">
            <thead>
                <tr id="euroPmiHeaderRow">
                    <th class="industry-col">Metric</th>
                    <!-- Months will be populated by JS -->
                </tr>
            </thead>
            <tbody id="euroPmiBody"></tbody>
        </table>
    </div>

    <div class="footer">
        <p>Source: S&P Global / Hamburg Commercial Bank (HCOB)</p>
        <p>Last Updated: <span id="last-updated-date">Dec 28, 2025</span></p>
    </div>

    <script>
        // Placeholder Data Structure for future integration
        // We will likely want to track: Headline PMI, Output, New Orders, Employment, etc.


        const euroPmiMetrics = [
            { key: 'esi', label: 'Economic Sentiment (ESI)' },
            { key: 'headlinePmi', label: 'Manufacturing Confidence' },
            { key: 'servicesPmi', label: 'Services Confidence' },
            { key: 'consumerConf', label: 'Consumer Confidence' },
            { key: 'retailConf', label: 'Retail Confidence' },
            { key: 'buildingConf', label: 'Construction Confidence' },
            { key: 'eei', label: 'Employment Expectations (EEI)' }
        ];

        const allRegionData = {};
        let currentRegion = 'EA';
        let euroPmiData = [];
        let euroHistoryData = { dates: [], esi: [] };

        const euroPmiHeaderRow = document.getElementById('euroPmiHeaderRow');
        const euroPmiBody = document.getElementById('euroPmiBody');

        // Data comes in descending order (newest first).
        
        const populateTable = () => {
            if (!euroPmiData || !euroPmiData.length) return;
            // Create a shallow copy and reverse it for display
            const displayData = [...euroPmiData].reverse();
            
            euroPmiHeaderRow.innerHTML = '<th class="industry-col">Metric</th>';
            euroPmiBody.innerHTML = '';
    
            // Populate Headers
            displayData.forEach(d => {
                const th = document.createElement('th');
                th.textContent = d.date;
                euroPmiHeaderRow.appendChild(th);
            });
    
            // Populate Rows
            euroPmiMetrics.forEach(metric => {
                const tr = document.createElement('tr');
    
                const nameTd = document.createElement('td');
                nameTd.className = 'industry-col';
                nameTd.textContent = metric.label;
                tr.appendChild(nameTd);
    
                displayData.forEach(d => {
                    const td = document.createElement('td');
                    const val = d[metric.key];
    
                    if (val !== null && val !== undefined) {
                        td.textContent = val.toFixed(1);
    
                        // Color Logic
                        if (metric.key === 'esi' || metric.key === 'eei') {
                            if (val >= 100) {
                                const intensity = Math.min((val - 100) / 10, 1);
                                td.style.backgroundColor = `rgba(46, 204, 113, ${0.2 + (0.6 * intensity)})`;
                            } else {
                                const intensity = Math.min((100 - val) / 10, 1);
                                td.style.backgroundColor = `rgba(231, 76, 60, ${0.2 + (0.6 * intensity)})`;
                            }
                        } else {
                            if (val >= 0) {
                                const intensity = Math.min(val / 10, 1);
                                td.style.backgroundColor = `rgba(46, 204, 113, ${0.2 + (0.6 * intensity)})`;
                            } else {
                                const intensity = Math.min(Math.abs(val) / 10, 1);
                                td.style.backgroundColor = `rgba(231, 76, 60, ${0.2 + (0.6 * intensity)})`;
                            }
                        }
                    } else {
                        td.textContent = "-";
                        td.style.backgroundColor = "#fefefe";
                    }
    
                    tr.appendChild(td);
                });
    
                euroPmiBody.appendChild(tr);
            });
        };


        // --- Charts Initialization ---
        
            let chartInstances = {}; // Track all charts

            const createChart = (canvasId, label, dates, data, stats, title, color) => {
                const ctx = document.getElementById(canvasId).getContext('2d');

                // Destroy existing if re-rendering
                if (chartInstances[canvasId]) {
                    chartInstances[canvasId].destroy();
                }

                // Lines for stats
                const meanLine = Array(dates.length).fill(stats.mean);
                const peakLine = Array(dates.length).fill(stats.avgPeak);
                const troughLine = Array(dates.length).fill(stats.avgTrough);

                chartInstances[canvasId] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [
                            {
                                label: label,
                                data: data,
                                borderColor: color,
                                backgroundColor: color + '1A', // 10% opacity hex
                                borderWidth: 2,
                                fill: true,
                                tension: 0.1,
                                order: 1
                            },
                            {
                                label: `Mean (${stats.mean.toFixed(1)})`,
                                data: meanLine,
                                borderColor: '#333',
                                borderWidth: 1,
                                borderDash: [2, 2],
                                pointRadius: 0,
                                fill: false,
                                tension: 0,
                                order: 2
                            },
                            {
                                label: `Avg Peak (${stats.avgPeak.toFixed(1)})`,
                                data: peakLine,
                                borderColor: '#10b981',
                                borderWidth: 1,
                                borderDash: [4, 4],
                                pointRadius: 0,
                                fill: false,
                                tension: 0,
                                order: 3
                            },
                            {
                                label: `Avg Trough (${stats.avgTrough.toFixed(1)})`,
                                data: troughLine,
                                borderColor: '#ef4444',
                                borderWidth: 1,
                                borderDash: [4, 4],
                                pointRadius: 0,
                                fill: false,
                                tension: 0,
                                order: 4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        elements: { point: { radius: 0, hoverRadius: 4 } },
                        scales: {
                            x: { ticks: { maxTicksLimit: 10 } },
                            y: { beginAtZero: false }
                        },
                        plugins: {
                            legend: { display: true, position: 'top', labels: { boxWidth: 10, font: { size: 10 } } },
                            tooltip: { mode: 'index', intersect: false },
                            title: { display: true, text: title }
                        },
                        interaction: { mode: 'nearest', axis: 'x', intersect: false }
                    }
                });
            };

            const renderCharts = (range) => {
                if (!euroHistoryData || !euroHistoryData.dates) return;
                
                // Determine slice index
                let sliceIdx = 0;
                
                // Fetch fresh data based on currentRegion to ensure accuracy
                const histData = allRegionData[currentRegion].history;
                let filteredDates = [...histData.dates];

                if (range === '5Y') {
                    sliceIdx = Math.max(0, filteredDates.length - 60);
                } else if (range === '1Y') {
                    sliceIdx = Math.max(0, filteredDates.length - 12);
                }

                filteredDates = filteredDates.slice(sliceIdx);

                const getSlicedData = (key) => histData[key].slice(sliceIdx);
                const regionName = allRegionData[currentRegion].name;

                // 1. ESI (Blue)
                const esiStats = calculateLevels(histData.esi, histData.dates, 'index');
                createChart('esiChart', 'ESI', filteredDates, getSlicedData('esi'), esiStats, `${regionName} Economic Sentiment (ESI)`, '#2563eb');

                // 2. EEI (Green)
                const eeiStats = calculateLevels(histData.eei, histData.dates, 'index');
                createChart('eeiChart', 'EEI', filteredDates, getSlicedData('eei'), eeiStats, `${regionName} Employment Expectations (EEI)`, '#16a34a');

                // 3. Manufacturing (Purple)
                const manuStats = calculateLevels(histData.headlinePmi, histData.dates, 'balance');
                createChart('manuChart', 'Manufacturing', filteredDates, getSlicedData('headlinePmi'), manuStats, `${regionName} Manufacturing Confidence`, '#8b5cf6');

                // 4. Services (Orange)
                const servStats = calculateLevels(histData.servicesPmi, histData.dates, 'balance');
                createChart('servChart', 'Services', filteredDates, getSlicedData('servicesPmi'), servStats, `${regionName} Services Confidence`, '#f97316');

                // 5. Consumer (Yellow/Amber)
                const consStats = calculateLevels(histData.consumerConf, histData.dates, 'balance');
                createChart('consChart', 'Consumer', filteredDates, getSlicedData('consumerConf'), consStats, `${regionName} Consumer Confidence`, '#f59e0b');

                // 6. Retail (Pink)
                const retaStats = calculateLevels(histData.retailConf, histData.dates, 'balance');
                createChart('retaChart', 'Retail', filteredDates, getSlicedData('retailConf'), retaStats, `${regionName} Retail Confidence`, '#ec4899');

                // 7. Construction (Teal)
                const builStats = calculateLevels(histData.buildingConf, histData.dates, 'balance');
                createChart('builChart', 'Construction', filteredDates, getSlicedData('buildingConf'), builStats, `${regionName} Construction Confidence`, '#14b8a6');
            };
            
            // Region Switching Logic
            window.switchRegion = (regionCode) => {
                const data = allRegionData[regionCode];
                if (!data) return;
                
                currentRegion = regionCode;
                euroPmiData = data.table_data;
                euroHistoryData = data.history;
                
                // Update UI: Title (Use "All Eurozone" for EA, otherwise Name)
                const titleEl = document.querySelector('.page-title');
                if (titleEl) {
                    titleEl.innerText = (regionCode === 'EA') ? "All Eurozone" : data.name;
                }
                
                // Update UI: Insights
                const insightsEl = document.getElementById('euro-pmi-survey-insights');
                if (insightsEl && data.insight) {
                    insightsEl.innerHTML = data.insight;
                }

                // Update UI Tabs
                const map = { 'EA': 0, 'DE': 1, 'FR': 2, 'IT': 3, 'ES': 4, 'NL': 5 };
                const tabs = document.querySelectorAll('.region-tab');
                tabs.forEach(t => t.classList.remove('active'));
                if (tabs[map[regionCode]]) tabs[map[regionCode]].classList.add('active');

                // Re-render Table
                populateTable();
                
                // Re-render Charts (keep current time range)
                const currentRangeBtn = document.querySelector('.time-btn.active');
                const range = currentRangeBtn ? currentRangeBtn.innerText : 'ALL';
                renderCharts(range);
            };

            // Helper to compute statistics: Mean, Avg Peak, Avg Trough
            // type: 'index' (ESI/EEI, mean=100) or 'balance' (Conf, mean=calculated)
            const calculateLevels = (data, dates, type = 'index') => {
                const vals = data.filter(d => d !== null);
                if (!vals.length) return { mean: type === 'index' ? 100 : 0, avgPeak: 0, avgTrough: 0 };

                let mean = 0;
                let avgPeak = 0;
                let avgTrough = 0;

                if (type === 'index') {
                    mean = 100; // Fixed at 100 for ESI/EEI

                    // Average Peak: User specified 1989, 2000, 2017, 2021
                    const peakYears = ['1989', '2000', '2017', '2021'];
                    let yearMaxs = [];
                    peakYears.forEach(year => {
                        let maxInYear = -Infinity;
                        let found = false;
                        dates.forEach((d, i) => {
                            if (d.startsWith(year) && data[i] !== null) {
                                if (data[i] > maxInYear) { maxInYear = data[i]; found = true; }
                            }
                        });
                        if (found) yearMaxs.push(maxInYear);
                    });
                    avgPeak = yearMaxs.length ? yearMaxs.reduce((a, b) => a + b, 0) / yearMaxs.length : Math.max(...vals);

                    // Average Trough: User specified 1993, 2009, 2019
                    const troughYears = ['1993', '2009', '2019'];
                    let yearMins = [];
                    troughYears.forEach(year => {
                        let minInYear = Infinity;
                        let found = false;
                        dates.forEach((d, i) => {
                            if (d.startsWith(year) && data[i] !== null) {
                                if (data[i] < minInYear) { minInYear = data[i]; found = true; }
                            }
                        });
                        if (found) yearMins.push(minInYear);
                    });
                    avgTrough = yearMins.length ? yearMins.reduce((a, b) => a + b, 0) / yearMins.length : Math.min(...vals);

                } else {
                    // Balance Indicators: User requested calculated Mean
                    mean = vals.reduce((a, b) => a + b, 0) / vals.length;

                    vals.sort((a, b) => a - b);
                    const top10pct = vals.slice(Math.floor(vals.length * 0.9));
                    const bottom10pct = vals.slice(0, Math.ceil(vals.length * 0.1));

                    avgPeak = top10pct.length ? top10pct.reduce((a, b) => a + b, 0) / top10pct.length : Math.max(...vals);
                    avgTrough = bottom10pct.length ? bottom10pct.reduce((a, b) => a + b, 0) / bottom10pct.length : Math.min(...vals);
                }

                return { mean, avgPeak, avgTrough };
            };
            
            // Event Listeners for Buttons
            document.querySelectorAll('.time-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    renderCharts(e.target.dataset.range);
                });
            });

            // Initial Render handled by update script injection or call here if data present
            // We rely on the injected block to set allRegionData and call renderCharts
            
            // But we must safely call it only if data exists.
            if (Object.keys(allRegionData).length > 0) {
                 populateTable();
                 renderCharts('ALL');
            }

    </script>
</body>

</html>
"""

with open(HTML_FILE, 'w') as f:
    f.write(html_content)

print(f"{HTML_FILE} has been reset.")
