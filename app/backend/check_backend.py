import asyncio
import sys
from pathlib import Path

# Ensure parent directory is on sys.path so the top-level 'backend' package
# can be imported when running this script from inside the package folder.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

try:
    from backend.server import app  # noqa: F401
except Exception:
    pass  # continue to try DB ping even if import fails

try:
    from backend.db import get_typed_db

    db = get_typed_db()
    ok = asyncio.run(db.validate_connection())
    if not ok:
        sys.exit(1)
except Exception:
    sys.exit(1)
