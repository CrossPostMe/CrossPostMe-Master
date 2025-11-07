#!/bin/bash

# ============================================
# SUPABASE SCHEMA SETUP - ONE COMMAND
# ============================================

echo "🚀 CROSSPOSTME - SUPABASE SCHEMA SETUP"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if SQL file exists
if [ ! -f "supabase_schema.sql" ]; then
    echo -e "${RED}❌ supabase_schema.sql not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found supabase_schema.sql${NC}"
echo ""

# Copy SQL to clipboard (if possible)
if command -v xclip &> /dev/null; then
    cat supabase_schema.sql | xclip -selection clipboard
    echo -e "${GREEN}✅ SQL copied to clipboard!${NC}"
elif command -v pbcopy &> /dev/null; then
    cat supabase_schema.sql | pbcopy
    echo -e "${GREEN}✅ SQL copied to clipboard!${NC}"
else
    echo -e "${YELLOW}⚠️  Clipboard tool not found (install xclip or pbcopy)${NC}"
    echo -e "   SQL file ready at: ${BLUE}supabase_schema.sql${NC}"
fi

echo ""
echo "========================================================================"
echo -e "${BLUE}📋 MANUAL STEPS REQUIRED:${NC}"
echo "========================================================================"
echo ""
echo "1️⃣  Open Supabase Dashboard:"
echo -e "    ${BLUE}https://supabase.com/dashboard/project/toehrbdycbtgfhmrloee${NC}"
echo ""
echo "2️⃣  Click 'SQL Editor' in the left sidebar"
echo ""
echo "3️⃣  Click 'New Query'"
echo ""
echo "4️⃣  Paste the SQL (already in clipboard if xclip/pbcopy installed)"
echo "    OR copy from: supabase_schema.sql"
echo ""
echo "5️⃣  Click 'Run' ▶️"
echo ""
echo "6️⃣  Wait for 'Success. No rows returned'"
echo ""
echo "7️⃣  Verify tables created:"
echo "    - Click 'Table Editor'"
echo "    - Should see: users, listings, business_intelligence, etc."
echo ""
echo "========================================================================"
echo -e "${GREEN}✅ THEN TEST CONNECTION:${NC}"
echo "========================================================================"
echo ""
echo "    cd app/backend && python3 test_supabase.py"
echo ""
echo "========================================================================"
echo ""

# Try to open browser (optional)
PROJECT_URL="https://supabase.com/dashboard/project/toehrbdycbtgfhmrloee/editor"

if [ -n "$BROWSER" ]; then
    echo -e "${BLUE}🌐 Opening browser...${NC}"
    $BROWSER "$PROJECT_URL" 2>/dev/null &
elif command -v xdg-open &> /dev/null; then
    echo -e "${BLUE}🌐 Opening browser...${NC}"
    xdg-open "$PROJECT_URL" 2>/dev/null &
elif command -v open &> /dev/null; then
    echo -e "${BLUE}🌐 Opening browser...${NC}"
    open "$PROJECT_URL" 2>/dev/null &
else
    echo -e "${YELLOW}💡 Manually open:${NC}"
    echo -e "   ${BLUE}$PROJECT_URL${NC}"
fi

echo ""
echo -e "${GREEN}Ready to go! Follow the steps above.${NC}"
echo ""
