# CrossPostMe - GitHub Copilot Instructions

## Project Overview

CrossPostMe is a multi-platform local listings automation tool that helps users manage and cross-post advertisements across multiple platforms (eBay, Facebook, Craigslist, etc.). The application consists of a FastAPI backend and a React frontend with a modern, clean architecture.

**Purpose**: Automate ad posting and management across multiple marketplace platforms  
**Target Users**: Small businesses and individuals managing local marketplace listings  
**Key Features**: Ad creation/management, platform integrations, user authentication, credential encryption

## Tech Stack

### Backend (`app/backend/`)
- **Language**: Python 3.11.9
- **Framework**: FastAPI 0.110.1
- **Database**: MongoDB (async via Motor 3.6.0)
- **Authentication**: JWT (PyJWT, python-jose)
- **Security**: Bcrypt for passwords, Cryptography for credential encryption
- **Server**: Uvicorn (dev), Gunicorn (production)
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, isort, flake8, mypy, ruff

### Frontend (`app/frontend/`)
- **Language**: JavaScript
- **Framework**: React 19.0.0
- **Build Tool**: Vite 7.1.12 (migrated from Create React App)
- **UI Libraries**: 
  - Radix UI components
  - Tailwind CSS 3.4.17
  - shadcn/ui patterns
  - Lucide icons
- **Routing**: React Router DOM 7.5.1
- **State Management**: React hooks
- **Form Handling**: React Hook Form with Zod validation
- **Testing**: Playwright (E2E), Vitest (unit tests)
- **Package Manager**: Yarn 1.22.22

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Database**: MongoDB
- **Deployment**: Render (backend), Hostinger (frontend)

## Quick Setup

### Backend Setup

```bash
# Navigate to backend
cd app/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (IMPORTANT!)
cp .env.example .env
# Edit .env and add:
# - MONGO_URL
# - DB_NAME
# - CREDENTIAL_ENCRYPTION_KEY (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# - JWT_SECRET_KEY
# - CORS_ORIGINS

# Run development server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd app/frontend

# Install dependencies
yarn install

# Set up environment variables
cp .env.example .env
# Edit .env and add:
# - VITE_API_URL (typically http://localhost:8000)

# Run development server
yarn start
# OR
yarn dev
```

### Docker Setup (Full Stack)

```bash
# From repository root
docker-compose up --build
```

## Architecture & Directory Structure

```
CrossPostMe_MR/
├── .github/
│   ├── copilot-instructions.md     # This file
│   ├── workflows/                  # GitHub Actions
│   └── dependabot.yml
├── app/
│   ├── backend/                    # FastAPI backend
│   │   ├── server.py              # Main application entry point
│   │   ├── models.py              # Pydantic models
│   │   ├── auth.py                # Authentication logic
│   │   ├── db.py                  # Database utilities
│   │   ├── routes/                # API route modules
│   │   │   ├── ads.py            # Ad management endpoints
│   │   │   ├── platforms.py      # Platform integration endpoints
│   │   │   ├── ai.py             # AI-powered features
│   │   │   └── ...
│   │   ├── services/              # Business logic layer
│   │   ├── automation/            # Platform automation scripts
│   │   ├── tests/                 # Backend tests
│   │   ├── requirements.txt       # Python dependencies
│   │   └── Dockerfile
│   ├── frontend/                  # React frontend
│   │   ├── src/
│   │   │   ├── components/       # Reusable UI components
│   │   │   ├── pages/            # Page components
│   │   │   ├── App.jsx           # Main app component
│   │   │   └── index.jsx         # Entry point
│   │   ├── public/               # Static assets
│   │   ├── playwright-tests/     # E2E tests
│   │   ├── vite.config.js        # Vite configuration
│   │   ├── tailwind.config.js    # Tailwind configuration
│   │   ├── package.json
│   │   └── Dockerfile
│   └── landing/                   # Landing page (separate Vite project)
├── docs/                          # Additional documentation
├── docker-compose.yml
└── [Various documentation files].md
```

## Coding Standards & Conventions

### Backend (Python)

**Route Structure**:
- Each route module exports an `APIRouter` instance
- Routes are registered in `server.py` using `app.include_router()`
- Use `prefix` and `tags` in APIRouter for organization

```python
# Example route module pattern
from fastapi import APIRouter, HTTPException
from models import YourModel

router = APIRouter(prefix="/api/resource", tags=["resource"])

@router.get("/")
async def list_resources():
    # Implementation
    pass
```

**Database Patterns**:
- Prefer reusing the shared Motor client from `server.py`
- Avoid creating multiple MongoDB clients per route
- Use `.to_list(1000)` for queries, then map to Pydantic models
- Serialize datetimes to ISO strings before MongoDB insert
- Use `ConfigDict(extra="ignore")` in Pydantic models to ignore MongoDB `_id`

```python
# Example database pattern
@router.get("/", response_model=List[Model])
async def list_items():
    db = get_db()  # Get database connection
    items = await db.collection.find({}).to_list(1000)
    return [Model(**item) for item in items]
```

**Error Handling**:
- Use `HTTPException` for HTTP errors
- Include appropriate status codes (404, 400, 401, etc.)

**Security**:
- Never commit secrets or API keys
- Use environment variables for all credentials
- Encrypt sensitive platform credentials before storing in DB
- Use the `CREDENTIAL_ENCRYPTION_KEY` for Fernet encryption

**Code Quality**:
- Run `black .` for formatting
- Run `isort .` for import sorting
- Run `flake8 .` for linting
- Run `mypy .` for type checking
- Run `ruff check . --fix` for comprehensive linting

### Frontend (JavaScript/React)

**Component Patterns**:
- Use functional components with hooks
- Follow React 19 best practices
- Use PascalCase for component names
- Keep components small and focused

**Styling**:
- Use Tailwind CSS utility classes
- Follow shadcn/ui patterns for components
- Use Radix UI primitives for accessible components

**Routing**:
- React Router DOM v7 for routing
- Use lazy loading for code splitting where appropriate

**State Management**:
- React hooks (useState, useEffect, useContext) for state
- React Hook Form for form state
- Zod for form validation schemas

**API Calls**:
- Use axios for HTTP requests
- Base URL configured via environment variables (VITE_API_URL)

**Code Quality**:
- Run `eslint` for linting (configured in project)
- Follow existing code patterns in components/

## Testing

### Backend Tests (pytest)

```bash
cd app/backend
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest tests/test_routes.py     # Run specific test file
```

**Test Structure**:
- Tests located in `app/backend/tests/`
- Use `pytest-asyncio` for async tests
- Fixtures defined in `conftest.py`

### Frontend Tests

**E2E Tests (Playwright)**:
```bash
cd app/frontend
yarn test:e2e              # Run all E2E tests
yarn test:e2e:ui           # Run with UI mode
yarn test:e2e:debug        # Run in debug mode
```

**Unit Tests (Vitest)**:
```bash
yarn test                  # Run unit tests
```

**Test Structure**:
- E2E tests in `app/frontend/playwright-tests/`
- Key test files:
  - `auth.spec.js` - Authentication flows
  - `navbar.spec.js` - Navigation testing
  - `login.spec.js` - Login functionality
  - `form.spec.js` - Form validation

## Build & Validation

### Backend

```bash
cd app/backend

# Lint and format
black .
isort .
flake8 .
mypy .
ruff check . --fix

# Run tests
pytest

# Start server
uvicorn server:app --reload
```

### Frontend

```bash
cd app/frontend

# Install dependencies
yarn install

# Development server
yarn dev

# Build for production
yarn build

# Preview production build
yarn preview

# Run tests
yarn test:e2e
```

## Environment Variables

### Backend Required Variables

```bash
# Database
MONGO_URL=mongodb://localhost:27017/
DB_NAME=crosspostme

# Security
CREDENTIAL_ENCRYPTION_KEY=<generate-with-cryptography-fernet>
JWT_SECRET_KEY=<your-secret-key>

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Platform API Keys (as needed)
EBAY_CLIENT_ID=
EBAY_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
```

### Frontend Required Variables

```bash
VITE_API_URL=http://localhost:8000
```

## Key Files to Inspect

When working on specific areas, check these files first:

**Backend Entry & Configuration**:
- `app/backend/server.py` - App entry, router mounting, CORS, DB lifecycle
- `app/backend/models.py` - Pydantic models
- `app/backend/auth.py` - Authentication logic

**Backend Routes**:
- `app/backend/routes/ads.py` - Ad management
- `app/backend/routes/platforms.py` - Platform integrations
- `app/backend/routes/ai.py` - AI features

**Frontend Configuration**:
- `app/frontend/vite.config.js` - Vite build config
- `app/frontend/tailwind.config.js` - Tailwind config
- `app/frontend/playwright.config.js` - E2E test config
- `app/frontend/src/App.jsx` - Main app component

**Documentation**:
- `START_HERE.md` - Quick start guide
- `PROJECT_OVERVIEW.md` - Project context
- `PROJECT_STATUS.md` - Current status
- `app/README.md` - Main project docs

## Common Development Tasks

### Adding a New Backend Route

1. Create route module in `app/backend/routes/your_route.py`
2. Export an `APIRouter` with prefix and tags
3. Add route to `server.py`: `app.include_router(your_route.router)`
4. Add Pydantic models to `models.py` if needed
5. Test with pytest

### Adding a New Frontend Component

1. Create component in `app/frontend/src/components/`
2. Use Tailwind CSS for styling
3. Follow existing shadcn/ui patterns
4. Import and use in page component
5. Add E2E test if it's a major feature

### Updating Dependencies

**Backend**:
```bash
pip install <package>
pip freeze > requirements.txt
```

**Frontend**:
```bash
yarn add <package>
# package.json is updated automatically
```

## CI/CD

- Backend: Auto-deploys to Render on push to main
- Frontend: Manual upload to Hostinger via scripts
- GitHub Actions workflows in `.github/workflows/`

## Deployment Notes

**Backend** (Render):
- Auto-deploys from main branch
- Environment variables configured in Render dashboard
- Uses `gunicorn` for production server

**Frontend** (Hostinger):
- Build locally: `yarn build`
- Upload via FTP script: `./scripts/upload-to-hostinger.ps1`

## Security Reminders

⚠️ **CRITICAL SECURITY PRACTICES**:
- Never commit `.env` files or secrets
- Always encrypt platform credentials before storing
- Use secrets manager for production (AWS Secrets Manager, HashiCorp Vault)
- Rotate credentials immediately if exposed
- Review `.gitignore` to ensure sensitive files are excluded

## Getting Help

- **Primary Contact**: crosspostme@gmail.com | 623-777-9969
- **Documentation**: Check `START_HERE.md`, `PROJECT_STATUS.md`, `QUICK_REFERENCE.md`
- **Daily Log**: `DAILY_LOG.md` tracks recent work
- **TODO List**: `app/backend/TODO.md` for technical tasks

## Additional Context

- The project recently migrated from Create React App to Vite
- Frontend uses shadcn/ui design patterns with Radix UI primitives
- Backend uses async MongoDB operations via Motor
- E2E test suite using Playwright covers critical user journeys
- Docker setup available for containerized development
- Comprehensive documentation in various .md files at root level

---

**Last Updated**: 2025-11-05  
**Copilot Instructions Version**: 1.0
