# Copilot Instructions - CrossPostMe

## Architecture Overview

**Multi-service monorepo** with two primary backend implementations and shared frontend:

- `app/backend/` — Production FastAPI backend (**Supabase PostgreSQL primary** + MongoDB fallback for legacy support)
- `app/frontend/` — React frontend (CRA + CRACO, Tailwind, Radix UI/shadcn)
- `CrossPostMe/` — Alternative FastAPI backend (MongoDB-only, legacy/experimental)
- `Android/`, `IOS/` — Mobile app scaffolding (not yet implemented)

**✅ Database Migration Complete**: Backend now uses **Supabase as the primary database** with MongoDB as fallback. Feature flags: `USE_SUPABASE=true` (default), `PARALLEL_WRITE=true` (keeps MongoDB in sync during transition). All 45+ endpoints migrated and production-ready.

## Essential Development Patterns

### Backend Route Pattern (`app/backend/routes/*.py`)

All route modules must:
1. Export `router = APIRouter(prefix="/api/...", tags=["..."])`
2. Be included in `server.py` via `app.include_router(module.router)` (after `startup_event`)
3. **Use Supabase-first with MongoDB fallback** (see `ads.py` example):

```python
# Feature flags for Supabase (both default to "true")
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

# ✅ SUPABASE PRIMARY - MongoDB as fallback
if USE_SUPABASE:
    result = await supabase_db.get_ads(user_id)  # Primary read
    if PARALLEL_WRITE:
        await db.ads.insert_one(...)  # Keep MongoDB in sync during transition
else:
    # Legacy fallback path (if USE_SUPABASE=false)
    result = await db.ads.find(...).to_list(1000)
```

### Authentication Patterns

**Protected routes** require authentication via FastAPI dependency injection:
```python
from auth import get_current_user

@router.post("/")
async def create_resource(
    data: ResourceCreate,
    current_user: dict = Depends(get_current_user)  # Enforces JWT auth
) -> Resource:
    # current_user contains {"user_id": "...", "email": "...", etc.}
    pass
```

**Optional auth** for public endpoints with user-specific features:
```python
from auth import get_optional_current_user

@router.get("/")
async def list_resources(
    current_user: dict | None = Depends(get_optional_current_user)
):
    # Returns None if no auth header, otherwise validates and returns user
    user_id = current_user["user_id"] if current_user else None
```

**Admin-only routes** use `get_current_user_with_fallback` which checks `is_admin` flag

### Database Access

**Supabase** (PostgreSQL - **PRIMARY DATABASE**):
- Import from `supabase_db.py`: `from supabase_db import db as supabase_db`
- Wrapper methods handle common operations (CRUD, analytics)
- RLS policies enforced at database level
- All 45+ endpoints migrated and production-ready

**MongoDB** (Motor async client - **FALLBACK/LEGACY**):
- Singleton client in `server.py` attached to `app.state.db`
- Access via `db = get_typed_db()` from `db.py`
- DateTime serialization: Convert to ISO strings before insert, deserialize on read
- Pagination: `.to_list(1000)` then map to Pydantic models
- Used for parallel writes during transition (`PARALLEL_WRITE=true`)
- See `MIGRATION_STATUS.md` for migration completion details

### Secrets Management

**Vault-based system** (`secrets_vault/`, see `SECRETS_VAULT_README.md`):
- AES-256 encrypted secrets in `secrets_vault/*.enc`
- Master key in `secrets_vault/master.key` (NEVER commit)
- Usage: `from vault import get_secret; api_key = get_secret('openai_api_key')`
- Graceful fallback to environment variables if vault unavailable
- Pattern: Always try vault first, catch exceptions, fall back to `os.getenv()`

**Environment variables** (.env files):
- Backend: `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`, `SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- Frontend: `REACT_APP_API_URL`
- Migration flags: `USE_SUPABASE` (default: true), `PARALLEL_WRITE` (default: true)
- See `app/backend/ENVIRONMENT_VARS.md` for complete list

### Frontend Architecture

- **CRACO config** (`craco.config.js`) customizes CRA webpack/postcss/tailwind
- **Package manager**: Yarn v1 (`yarn install`, `yarn start`, `yarn build`)
- **Component library**: Radix UI + shadcn/ui components
- **Styling**: Tailwind CSS with custom config
- **Routing**: React Router v6

## Critical Developer Workflows

### Local Development (PowerShell)

```powershell
# Backend
cd app/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .

# Frontend
cd app/frontend
yarn install
yarn start

# Full stack via Docker
docker-compose up --build
```

### Database Initialization

Backend validates MongoDB connection on startup with **exponential backoff retry logic**:
- Default: 5 attempts with 3s base delay
- Configure via env vars: `MONGO_STARTUP_MAX_RETRIES`, `MONGO_STARTUP_RETRY_DELAY_SECONDS`
- Fails fast if exhausted to surface issues in production logs
- After validation, runs `initialize_auth_indexes()` to create DB indexes

### Testing

```powershell
# Backend tests (pytest with coverage)
.\app\run-backend-tests.ps1

# Frontend tests (CRA test runner)
.\app\run-frontend-tests.ps1

# E2E tests (Playwright)
.\app\run-playwright-tests.ps1
```

### Deployment

- **Backend**: Auto-deploys to Render on push to `main`
- **Frontend**: Deploy via `.\scripts\upload-to-hostinger.ps1`
- **Health checks**: `/api/health` (comprehensive), `/api/ready` (readiness probe)
- **Rollback**: Toggle `USE_SUPABASE=false` for instant MongoDB-only fallback

## Project-Specific Conventions

### Pydantic Models
- Use `ConfigDict(extra="ignore")` to ignore MongoDB `_id` fields
- DateTime fields: UTC timezone-aware, serialize to ISO strings for MongoDB

### Route Error Handling
- Raise `HTTPException(status_code=404)` for not-found resources
- Log errors before returning to client
- Graceful degradation when Supabase unavailable

### CORS Configuration
- Loaded from `CORS_ORIGINS` env var (comma-separated)
- Validated at startup via `config.py` (no wildcards in production)
- Applied via `CORSMiddleware` in `server.py`

### Code Quality
- Backend: `black` formatting, `pytest` tests, type hints required
- Frontend: ESLint via devDependencies
- Run tests before pushing (CI not yet configured)

## Key Files to Reference

| File | Purpose |
|------|---------|
| `app/backend/server.py` | App entry, router mounting, DB lifecycle, CORS |
| `app/backend/auth.py` | JWT auth, password hashing, user dependencies |
| `app/backend/routes/ads.py` | Dual-database pattern example |
| `app/backend/db.py` | MongoDB client with TLS config |
| `app/backend/supabase_db.py` | Supabase wrapper methods |
| `app/frontend/package.json` | Frontend scripts and dependencies |
| `MIGRATION_STATUS.md` | Current Supabase migration progress |
| `QUICK_REFERENCE.md` | Command cheatsheet |

## Adding New Features

### New Backend Route
1. Create `app/backend/routes/feature.py` with `router = APIRouter(...)`
2. Implement dual-database pattern if data persistence needed
3. Add Pydantic models to `app/backend/models.py`
4. Include router in `app/backend/server.py`: `app.include_router(feature.router)`
5. Add tests in `app/backend/tests/test_feature.py`

### New Frontend Component
1. Create component in `app/frontend/src/components/`
2. Use existing shadcn/ui components from `components/ui/`
3. Follow Tailwind styling patterns
4. Add route in React Router if needed

## Common Pitfalls

❌ **Don't create duplicate MongoDB clients** — reuse `get_typed_db()`  
❌ **Don't commit secrets** — use vault or .env (both gitignored)  
❌ **Don't forget feature flags** — check `USE_SUPABASE` for new data operations  
❌ **Don't skip datetime serialization** — MongoDB requires ISO strings  
❌ **Don't use `npm`** — frontend uses Yarn v1 exclusively

## Getting Unstuck

1. Check `QUICK_REFERENCE.md` for commands
2. Review `START_HERE.md` for onboarding guide
3. Check health endpoints: `curl https://www.crosspostme.com/api/health`
4. Verify environment variables in `.env` files
5. Contact: crosspostme@gmail.com or 623-777-9969
