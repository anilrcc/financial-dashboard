# How to Publish Your Financial Dashboard

## Option 1: GitHub Pages (Recommended)
This is the easiest way to host your static HTML dashboard for free, and it fits your current setup perfectly.

1.  **Initialize Git**:
    - Open your terminal.
    - Navigate to the distribution folder:
      ```bash
      cd /Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist
      ```
    - Run: `git init`

2.  **Push to GitHub**:
    - Create a new repository on GitHub (e.g., `financial-dashboard`).
    - Run the following commands (replace `YOUR_USERNAME` and `YOUR_REPO`):
      ```bash
      git add .
      git commit -m "Initial commit"
      git branch -M main
      git remote add origin https://github.com/YOUR_USERNAME/financial-dashboard.git
      git push -u origin main
      ```

3.  **Enable Pages**:
    - Go to your repository settings on GitHub.
    - Scroll down to "Pages".
    - Select `main` branch as the source.
    - Your site will be live at `https://YOUR_USERNAME.github.io/financial-dashboard/`.

## Option 2: Wix (Free Plan)
Wix is strictly a website builder and does not support uploading a folder of raw HTML/CSS/JS files directly to host them as a standalone site in the way you might expect.

**Workaround: Embedding**
1.  Create a Blank Page on your Wix site.
2.  Add an **HTML Code** element (Embed > Custom Embeds > Embed a Site).
3.  You would need to host your HTML files somewhere else (like GitHub Pages above) and embed them, OR copy-paste the code from each HTML file into an "HTML Box" on Wix.
    - *Note*: Copy-pasting code into Wix HTML boxes is tedious and often breaks styling because Wix isolates code in iframes.

**Conclusion**: For this project, **GitHub Pages** is the superior choice.

## Keeping Data Fresh

I've created two separate scripts for your different schedules:

### 1. Daily: Refresh Yields
-   **File**: `refresh_daily_yields.command`
-   **Run this**: Every day.
-   **What it does**: Updates the Treasury Yield Curve and pushes changes to the site.

### 2. Monthly: Refresh ISM
-   **File**: `refresh_monthly_ism.command`
-   **Run this**: Once a month (when new ISM data is released).
-   **What it does**: Scrapes the latest ISM report, updates the Heatmap and Comments, and pushes changes.

**How to run**: Just double-click the file. It handles the Git upload automatically.
