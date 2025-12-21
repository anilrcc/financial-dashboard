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

## Updating Data automatically
Since your dashboard uses Python scripts (`update_yields.py`, `update_ism.py`) to fetch data:

1.  **Run Locally**:
    ```bash
    cd /Users/anilgungadeen/.gemini/antigravity/scratch/financial_dashboard_dist
    python3 update_yields.py
    python3 update_ism.py
    ```
2.  **Commit & Push**:
    ```bash
    git add .
    git commit -m "Daily data update"
    git push
    ```
    Your site will automatically update within minutes.
