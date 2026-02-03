#!/bin/bash
# Setup script for automated ISM PMI updates using browser automation

echo "=================================================="
echo "ISM PMI Browser Automation Setup"
echo "=================================================="
echo ""

# Check if playwright is installed
if python3 -c "import playwright" 2>/dev/null; then
    echo "✓ Playwright is already installed"
else
    echo "Installing Playwright..."
    pip3 install playwright
    
    if [ $? -eq 0 ]; then
        echo "✓ Playwright installed successfully"
    else
        echo "✗ Failed to install Playwright"
        exit 1
    fi
fi

# Install browser binaries
echo ""
echo "Installing Chromium browser..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================="
    echo "✅ Setup Complete!"
    echo "=================================================="
    echo ""
    echo "You can now run automated ISM updates with:"
    echo "  python3 update_ism_browser.py"
    echo ""
    echo "Or use the refresh command:"
    echo "  ./refresh_monthly_ism.command"
    echo ""
else
    echo "✗ Failed to install browser"
    exit 1
fi
