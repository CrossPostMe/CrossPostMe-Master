# Copilot instructions (canonical)

Repository layout (high signal):

Quick checks to run first:

Project conventions you must follow:

Short dev commands (PowerShell):

```powershell
# Backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r app/backend/requirements.txt
uvicorn server:app --reload --app-dir app/backend

# Frontend
cd app/frontend
yarn install
yarn start
```

Tests & quality tools:

Deployment & infra:

Where to look for concrete examples:

If you add CI: create `.github/workflows/` entries that run `pip install -r app/backend/requirements.txt && pytest` and `cd app/frontend && yarn install && yarn test --ci`.

If something is unclear (deployment target, DB credentials, CI expectations), stop and ask a maintainer — include which manifests you inspected and a short plan for the change.


## CrossPostMe AI Agent Instructions

Concise, actionable guidance for AI agents working in this repository. Focus on current architecture, workflows, and conventions. If anything is unclear, stop and ask a maintainer, referencing which manifests you inspected and your plan.

## Architecture Overview

- **Backend**: FastAPI app (`app/backend/`)
  - Entry: `server.py` (mounts routers, sets up Motor MongoDB client, loads env vars via `dotenv`)
  - Routes: `routes/*.py` (each exports `router = APIRouter(...)`, included in `server.py`)
  - Models: `models.py` (Pydantic models, datetimes as ISO strings, `model_config = ConfigDict(extra="ignore")` for MongoDB `_id`)
  - DB: Use shared Motor client from `server.py`; avoid duplicating clients via local `get_db()`
  - Health/readiness: `/api/ready` (probe), `/api/health` (diagnostics)
- **Frontend**: React app (`app/frontend/`)
  - Bootstrapped with CRA, uses CRACO for config overrides
  - Styling: Tailwind, shadcn/ui
  - Entry/config: `package.json`, `craco.config.js`

## Developer Workflows

- **Backend setup**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r app/backend/requirements.txt
  uvicorn server:app --reload --app-dir app/backend
  ```
- **Frontend setup**:
  ```bash
  cd app/frontend
  yarn install
  yarn start
  ```
- **Testing**:
  - Backend: `pytest` (see `pytest.ini` for config), run with `app/run-backend-tests.sh`
  - Frontend: `yarn test` or `app/run-frontend-tests.sh`
- **Formatting & linting**:
  - Backend: `black .`, `flake8`, `mypy`, `isort` (see `requirements.txt`)
  - Frontend: ESLint via devDependencies
- **Docker/Compose**:
  - Use `docker-compose.yml` for local dev (Mongo, backend, frontend)
  - Backend env vars: `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS` (see `ENVIRONMENT_VARS.md`)
  - Frontend env vars: `REACT_APP_API_URL`

## Security & Secrets

- Never commit real credentials. Use `.env.example` for templates.
- If secrets are exposed, rotate immediately (see `CREDENTIAL_ROTATION_CHECKLIST.md`, `SECURITY_NOTICE.md`).
- Backend loads `.env` via `dotenv` in `server.py`.
- For production, use platform secrets (Render, Railway, GitHub Secrets).

## Dependency Management

- All dependencies have upper bounds in `setup.py` and `requirements.txt` (see `DEPENDENCY_CONSTRAINTS_UPDATE.md`).
- Python 3.9+ required.
- Use `pip check` after install to verify no conflicts.

## Database Setup

- MongoDB indexes and content hash for deduplication (see `DATABASE_SETUP.md`).
- Run setup script: `python scripts/setup_db.py` from `app/backend`.

## Health & Probes

- `/api/ready`: readiness probe (HTTP 200 if DB reachable, 503 if not)
- `/api/health`: diagnostics (JSON, includes debug info if `HEALTH_DEBUG=true`)
- See `PROBES.md` for platform probe config and troubleshooting.

## Concrete Examples

- Router + DB: `app/backend/routes/ads.py`, `platforms.py`, `ai.py`
- App entry, CORS, DB: `app/backend/server.py`
- Frontend structure: `app/frontend/package.json`, `craco.config.js`, `frontend/src/`

## CI/CD

- If adding CI, use `.github/workflows/` to run:
  - `pip install -r app/backend/requirements.txt && pytest`
  - `cd app/frontend && yarn install && yarn test --ci`

## If Unclear

- Stop and ask a maintainer. Reference which manifests you inspected and your plan for the change.
