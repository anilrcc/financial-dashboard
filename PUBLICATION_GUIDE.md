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

## Your Daily Workflow Guide

### Step 1: Locate the Folder
Since these files are in a hidden folder, the easiest way to find them is:
1.  Open **Finder**.
2.  Press `Cmd + Shift + G` (or go to **Go > Go to Folder** in the menu bar).
3.  Paste this exact path and press Enter:
    `/Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist`
4.  **Tip**: Drag this folder to your Finder Sidebar ("Favorites") so you can click it easily tomorrow!

### Step 2: Refresh the Website
Once you are in the folder:

*   **Every Morning**: Double-click `refresh_daily_yields.command`.
    *   A terminal window will pop up, run some text, and close itself after saying "SUCCESS".
    *   Your live website will verify the new 10Y/2Y yields in about 1 minute.

*   **Once a Month**: Double-click `refresh_monthly_ism.command`.
    *   Run this only when new ISM data is released (usually the 1st business day of the month).
