# CrossPostMe AI Agent Instructions

This document provides authoritative, actionable guidance for AI agents working in the CrossPostMe repository.

## Repository Layout

- `app/backend/`: The primary FastAPI backend. The main entry point is `server.py`. It includes `routes/` for API endpoints and `models.py` for data models.
- `app/frontend/`: The React frontend, built with Create React App and customized with `craco`. It uses Tailwind CSS and shadcn/ui.
- `Android/` and `IOS/`: Starter templates for mobile clients. These reference the backend models and services but are not fully implemented applications.
- `CrossPostMe/`: Contains a legacy or related backend application. For current development, focus on `app/backend/`.

## Architecture & Data Flow

- The backend has been migrated from MongoDB to **Supabase**. When working on the backend, prioritize Supabase-related logic and ignore any remaining MongoDB code unless specifically tasked with maintaining legacy endpoints.
- The main backend application is initialized in `app/backend/server.py`. This file mounts the API routers from the `routes/` directory and manages the database client lifecycle.
- Environment variables are loaded from an `.env` file in the `app/backend/` directory. Refer to `.env.example` for the required variables.
- API routes are defined in `app/backend/routes/`. Each file in this directory exports an `APIRouter` instance that is included in `app/backend/server.py`.
- Data models are defined in `app/backend/models.py` using Pydantic.

## Developer Workflows

### Backend

To set up and run the backend development server:

```powershell
# Create a virtual environment and activate it
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r .\app\backend\requirements.txt

# Run the development server
uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .\app\backend
```

- **Tests**: Run backend tests using `pytest`. The tests are located in `app/backend/tests/`. Refer to `app/backend/tests/README.md` for details on test markers and structure.

### Frontend

To set up and run the frontend development server:

```powershell
# Navigate to the frontend directory
cd .\app\frontend

# Install dependencies
yarn install

# Run the development server
yarn start
```

- **API Calls**: The frontend uses a helper in `src/lib/api.js` for making API calls. This helper manages cookie-based authentication and handles token refreshing.
- **UI Components**: The UI is composed of components from `src/components/` and `src/components/ui/` (which follows the shadcn/ui pattern).
- **E2E Tests**: End-to-end tests are written with Playwright and can be run with `yarn test:e2e`. Refer to `app/frontend/playwright-tests/README.md` for more details.

## Security & Environment

- Before running the application, copy `app/backend/.env.example` to `app/backend/.env`.
- Generate a new encryption key and update it in your `.env` file as described in `app/README.md`.
- **Never commit secrets to version control.** For production, use a secrets manager like AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets.

## Deployment

- The repository includes `Dockerfile` and `docker-compose.yml` for containerized deployments.
- The backend loads environment variables from the `.env` file using `python-dotenv` in `server.py`.
