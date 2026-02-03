# ISM Manufacturing PMI Update - Automation Guide

## Overview

The ISM Manufacturing PMI data can be updated in three ways:

1. **🤖 Automated Browser Update** (Recommended) - Handles disclaimer modal automatically
2. **🌐 Standard HTTP Update** - Fast but may fail due to website security
3. **✋ Manual Update** - For when automation fails

---

## Method 1: Automated Browser Update (Recommended)

### One-Time Setup

Install Playwright and browser binaries:

```bash
bash setup_ism_automation.sh
```

This will:
- Install the Playwright Python library
- Download Chromium browser binaries
- Configure the environment for automated updates

### Running the Update

After setup, you can run automated updates with:

```bash
python3 update_ism_browser.py
```

Or use the refresh command (which auto-detects Playwright):

```bash
./refresh_monthly_ism.command
```

### How It Works

- Uses headless Chromium browser to navigate to ISM website
- Automatically accepts the disclaimer modal
- Extracts all PMI data, industry rankings, and comments
- Updates both `industry_heatmap.html` and `industry_comments.html`
- Only adds new months (won't duplicate existing data)

### Advantages

✅ Handles disclaimer modal automatically  
✅ Works reliably with ISM website security  
✅ Fully automated - no manual intervention needed  
✅ Extracts complete data including comments  

### Requirements

- Python 3.7+
- Playwright library (`pip install playwright`)
- Chromium browser binaries (installed via `playwright install chromium`)
- ~200MB disk space for browser binaries

---

## Method 2: Standard HTTP Update

### Running the Update

```bash
python3 update_ism.py
```

### How It Works

- Uses Python `requests` library to fetch ISM reports
- Falls back to `curl` if requests fails
- Attempts direct URL guessing if landing page is blocked

### Advantages

✅ Fast (no browser overhead)  
✅ No additional dependencies  
✅ Works if ISM removes disclaimer modal  

### Limitations

❌ Fails when disclaimer modal is present  
❌ May be blocked by CAPTCHA or security measures  
❌ Less reliable than browser method  

---

## Method 3: Manual Update

### When to Use

Use this method when:
- Automated methods fail
- You want to verify data before updating
- You need to update a specific month manually

### Running a Manual Update

1. **Extract data from browser** (already done for January 2026):
   - Navigate to ISM website in your browser
   - Accept disclaimer manually
   - Copy the data you need

2. **Create/edit manual update script**:
   ```bash
   # Edit the script with your data
   nano manual_update_january_2026.py
   ```

3. **Run the update**:
   ```bash
   python3 manual_update_january_2026.py
   ```

### Advantages

✅ Always works (manual browser access)  
✅ Allows data verification before updating  
✅ Can handle edge cases  

### Limitations

❌ Requires manual data extraction  
❌ Time-consuming  
❌ Prone to human error  

---

## Troubleshooting

### "Playwright not installed" Error

Run the setup script:
```bash
bash setup_ism_automation.sh
```

### "Browser not found" Error

Reinstall browser binaries:
```bash
python3 -m playwright install chromium
```

### "Connection aborted" or "503 Error"

The ISM website may be temporarily down or blocking requests. Try:
1. Wait a few minutes and retry
2. Use the browser-based method instead
3. Use manual update as last resort

### Data Already Exists

The scripts automatically check for existing data and won't duplicate months. If you see:
```
ℹ  Jan 2026 already exists, skipping...
```

This is normal - the data is already up to date.

---

## File Structure

```
update_ism_browser.py          # Automated browser-based update (recommended)
update_ism.py                  # Standard HTTP-based update (legacy)
manual_update_january_2026.py # Manual update template
setup_ism_automation.sh        # One-time setup for browser automation
refresh_monthly_ism.command    # Master refresh command (auto-detects method)
```

---

## Recommended Workflow

### First Time Setup

```bash
# 1. Run setup (one-time)
bash setup_ism_automation.sh

# 2. Test the automated update
python3 update_ism_browser.py
```

### Monthly Updates

```bash
# Just run the refresh command
./refresh_monthly_ism.command
```

The refresh command will:
1. Auto-detect if Playwright is available
2. Use browser automation if available, otherwise fall back to HTTP
3. Regenerate key insights
4. Update executive summary
5. Commit and push to GitHub

---

## Data Validation

After any update, verify:

1. **Check the months array** in `industry_heatmap.html`:
   ```bash
   grep "const months =" industry_heatmap.html
   ```

2. **Verify PMI data** was added:
   ```bash
   grep "Jan 2026" industry_heatmap.html
   ```

3. **View the page** in a browser to confirm visual display

---

## Support

If you encounter issues:

1. Check this README for troubleshooting steps
2. Try the browser-based method if HTTP fails
3. Use manual update as last resort
4. Check ISM website directly: https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/

---

**Last Updated**: February 2026  
**Automation Status**: ✅ Fully Automated (with Playwright)
