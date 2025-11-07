#!/bin/bash

# CrossPostMe Frontend Testing Script
# This script starts the frontend in development mode for testing

echo "🧪 CrossPostMe - Starting Frontend for Testing"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "app/frontend" ]; then
    echo "❌ Error: app/frontend directory not found"
    echo "Please run this script from the project root"
    exit 1
fi

cd app/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "✅ Starting development server..."
echo ""
echo "📝 Testing Checklist:"
echo "  1. Dashboard - http://localhost:5173/marketplace/dashboard"
echo "  2. Create Ad - http://localhost:5173/marketplace/create-ad"
echo "  3. My Ads - http://localhost:5173/marketplace/my-ads"
echo "  4. Edit Ad - http://localhost:5173/marketplace/edit-ad/:id"
echo "  5. Platforms - http://localhost:5173/marketplace/platforms"
echo "  6. Analytics - http://localhost:5173/marketplace/analytics"
echo "  7. Pricing - http://localhost:5173/marketplace/pricing"
echo "  8. Settings - http://localhost:5173/marketplace/settings"
echo "  9. Leads - http://localhost:5173/marketplace/leads"
echo " 10. Notifications - Click bell icon in navbar"
echo ""
echo "🔥 Press Ctrl+C to stop the server"
echo "=============================================="
echo ""

# Start the dev server
npm run dev
