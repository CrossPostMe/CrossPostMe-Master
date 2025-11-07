#!/bin/bash
# Fix all relative imports in backend routes

echo "Fixing relative imports in backend routes..."

cd /workspaces/CrossPostMe_MR/app/backend/routes

# Fix ..auth imports
find . -name "*.py" -exec sed -i 's/from \.\.auth import/from auth import/g' {} \;
find . -name "*.py" -exec sed -i 's/from backend\.auth import/from auth import/g' {} \;

# Fix ..db imports
find . -name "*.py" -exec sed -i 's/from \.\.db import/from db import/g' {} \;
find . -name "*.py" -exec sed -i 's/from backend\.db import/from db import/g' {} \;

# Fix ..models imports
find . -name "*.py" -exec sed -i 's/from \.\.models import/from models import/g' {} \;
find . -name "*.py" -exec sed -i 's/from backend\.models import/from models import/g' {} \;

# Fix ..services imports
find . -name "*.py" -exec sed -i 's/from \.\.services import/from services import/g' {} \;
find . -name "*.py" -exec sed -i 's/from \.\.services\./from services./g' {} \;
find . -name "*.py" -exec sed -i 's/from backend\.services import/from services import/g' {} \;
find . -name "*.py" -exec sed -i 's/from backend\.services\./from services./g' {} \;

# Fix supabase_db imports
find . -name "*.py" -exec sed -i 's/from backend\.supabase_db import/from supabase_db import/g' {} \;

echo "✅ Fixed all relative imports!"
echo "Files updated:"
find . -name "*.py" -exec echo "  - {}" \;
