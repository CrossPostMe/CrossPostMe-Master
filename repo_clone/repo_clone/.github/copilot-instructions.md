# Crosspostme AI Instructions

## Architecture Overview
Crosspostme is a multi-platform marketplace automation tool with separate **backend** (FastAPI + MongoDB) and **frontend** (React + shadcn/ui) services. The app enables users to create ads and post them across multiple platforms (Facebook, Craigslist, OfferUp, Nextdoor).

### Key Components
- **Backend**: FastAPI server (`backend/server.py`) with modular routes (`routes/ads.py`, `routes/platforms.py`, `routes/ai.py`)
- **Frontend**: React SPA with marketplace pages (`pages/Dashboard.jsx`, `CreateAd.jsx`, `MyAds.jsx`, `Platforms.jsx`)
- **Database**: MongoDB with Motor async driver, models defined in `backend/models.py`
- **UI System**: shadcn/ui components with custom Tailwind config and CRACO build setup

## Development Workflows

### Backend Development
```bash
# Navigate to backend directory
cd backend
# Install dependencies (use requirements.txt)
pip install -r requirements.txt
# Run server (requires MONGO_URL and DB_NAME environment variables)
uvicorn server:app --reload
```

### Frontend Development  
```bash
# Navigate to frontend directory
cd frontend
# Install dependencies
yarn install
# Start dev server with CRACO
yarn start
```

### Environment Setup
- Backend requires `.env` file with `MONGO_URL`, `DB_NAME`, `CORS_ORIGINS`
- Frontend uses `REACT_APP_BACKEND_URL` for API communication
- API routes are prefixed with `/api` (defined in `server.py` router)

## Code Patterns & Conventions

### Backend Patterns
- **Route Structure**: Modular routers with prefix patterns (`/api/ads`, `/api/platforms`, `/api/ai`)
- **Database Access**: Each route file implements `get_db()` function for MongoDB connection
- **Model Pattern**: Pydantic models with separate Create/Update variants (see `models.py`)
- **Error Handling**: Use FastAPI's `HTTPException` with specific status codes

### Frontend Patterns
- **Component Structure**: Pages in `pages/`, reusable components in `components/`, UI primitives in `components/ui/`
- **State Management**: Local React state with `useState`/`useEffect`, axios for API calls
- **Routing**: React Router with `/marketplace/*` routes for dashboard functionality
- **Styling**: Tailwind CSS with shadcn/ui component system and CSS variables

### Data Flow Examples
```javascript
// Frontend API pattern
const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const response = await axios.get(`${API}/ads/dashboard/stats`);

// Backend MongoDB pattern  
await db.ads.find(query).sort("created_at", -1).to_list(1000)
```

## Testing & Quality Assurance

### Test Structure
- Test coordination via `test_result.md` with structured YAML format
- Backend tests in `tests/` directory (pytest framework expected)
- Frontend testing through Create React App test runner

### Debugging & Monitoring
- Backend logging configured in `server.py` with structured format
- Frontend error boundaries and loading states in dashboard components
- CORS middleware configured for cross-origin requests

## Integration Points

### API Communication
- All API endpoints follow REST conventions with proper HTTP methods
- Async/await patterns throughout backend with Motor MongoDB driver
- Frontend components use environment-based API URL configuration

### External Dependencies
- **UI Components**: shadcn/ui with Radix UI primitives and Lucide icons
- **Build Tools**: CRACO for webpack customization, supports path aliases (`@/components`)
- **Database**: MongoDB with async operations, datetime handling for UTC timestamps

## Project-Specific Notes

### AI Features
- Mock AI ad generation in `routes/ai.py` with tone-based title generation
- Structured response format for suggested categories and keywords
- Optimization suggestions with scoring system

### Platform Integration
- Abstract platform model supports multiple marketplaces
- Account management with status tracking (active/suspended/flagged)
- Posted ads tracking with platform-specific IDs and URLs

### Performance Considerations
- Hot reload can be disabled via `DISABLE_HOT_RELOAD=true` environment variable
- Webpack watch optimization ignores common build directories
- MongoDB queries limited to 1000 documents with proper sorting

When working on this codebase, always check existing patterns in similar files before implementing new features. The modular structure allows for easy extension of both platforms and AI capabilities.