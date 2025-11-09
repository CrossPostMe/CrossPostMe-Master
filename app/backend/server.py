import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.cors import CORSMiddleware

from .db import get_typed_db

# Import route modules
from .routes import ads, ai, auth, diagrams, platform_oauth, platforms

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# DEBUG: Print MONGO_URL at startup to help diagnose Render env issues
print("DEBUG: MONGO_URL at startup:", os.environ.get("MONGO_URL"))

# Use typed database wrapper
db = get_typed_db()
# Flag to indicate test mode when running CI or unit tests locally. When
# TESTING=true we avoid real DB connections and use an in-memory store to
# keep the endpoints fast and deterministic in CI/test environments.
TESTING = os.getenv("TESTING", "false").lower() in ("1", "true", "yes")
# Module-level in-memory store used during tests when TESTING=True. We use a
# module variable instead of app.state to ensure it's available even before
# the FastAPI lifespan handler runs (tests may import `app` at module load).
_TEST_STATUS_CHECKS: list[dict] = []


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    from backend.routes.auth import initialize_auth_indexes

    # Startup: In testing mode we skip DB validation and use an in-memory
    # store for lightweight, deterministic unit tests.
    if TESTING:
        logging.info(
            "TESTING mode enabled - skipping MongoDB validation and using in-memory stores"
        )
        yield
        return

    # Production/startup: Validate DB connectivity and initialize indexes
    max_attempts = int(os.environ.get("MONGO_STARTUP_MAX_RETRIES", "5"))
    base_delay = float(os.environ.get("MONGO_STARTUP_RETRY_DELAY_SECONDS", "3"))

    attempt = 0
    while attempt < max_attempts:
        attempt += 1
        try:
            ok = await db.validate_connection()
        except Exception as exc:
            logging.warning(
                "Attempt %d/%d - unexpected error while validating DB connection: %s",
                attempt,
                max_attempts,
                exc,
            )
            ok = False

        if ok:
            logging.info("MongoDB validated on attempt %d/%d", attempt, max_attempts)
            break

        delay = base_delay * attempt
        logging.warning(
            "MongoDB not reachable (attempt %d/%d). Retrying in %.1fs...",
            attempt,
            max_attempts,
            delay,
        )
        await asyncio.sleep(delay)

    else:
        logging.error(
            "Failed to validate MongoDB connection after %d attempts. Aborting startup.",
            max_attempts,
        )
        raise RuntimeError("Failed to validate MongoDB connection during startup")

    # Initialize indexes once DB connectivity is confirmed
    await initialize_auth_indexes()

    yield  # App runs here

    # Shutdown: Close database connection
    db.close()


# Create the main app with lifespan handler
app = FastAPI(lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(status_check_in: StatusCheckCreate) -> StatusCheck:
    # Explicit local typing to satisfy mypy about generic dict types
    status_dict: Dict[str, Any] = status_check_in.model_dump()
    status_obj = StatusCheck(**status_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    # In testing mode we keep status checks in-memory to avoid motor/loop
    # interactions that can fail under the test client. Production uses MongoDB.
    if TESTING:
        _TEST_STATUS_CHECKS.append(doc)
    else:
        _ = await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=list[StatusCheck])
async def get_status_checks() -> list[StatusCheck]:
    # Exclude MongoDB's _id field from the query results. When running
    # tests we read from the in-memory store populated by create_status_check.
    if TESTING:
        status_checks: List[Dict[str, Any]] = list(_TEST_STATUS_CHECKS)
    else:
        status_checks: List[Dict[str, Any]] = await db.status_checks.find(
            {}, {"_id": 0}
        ).to_list(1000)

    # Convert ISO string timestamps back to datetime objects and map to models
    for check in status_checks:
        if isinstance(check["timestamp"], str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])

    return [StatusCheck(**check) for check in status_checks]


@api_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Readiness/liveness health endpoint.

    Returns basic application status and performs a quick DB connectivity
    check via db.validate_connection(). This endpoint is safe to call from
    a load balancer or platform readiness probe.
    """
    from datetime import datetime, timezone

    # Perform a lightweight DB connectivity check. db.validate_connection()
    # already emits helpful warnings on failure; here we return a JSON
    # payload for human/monitoring consumption. When HEALTH_DEBUG=true is
    # set in the environment we include additional TLS/SSL diagnostic info.
    # Validate_connection should return a bool-like value
    db_ok: bool = await db.validate_connection()

    payload: Dict[str, Any] = {
        "status": "ok" if db_ok else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_connected": bool(db_ok),
    }

    # Optional debug info included only when explicitly enabled via env var
    # to avoid leaking internal cert paths in production logs.
    try:
        debug_enabled = os.getenv("HEALTH_DEBUG", "false").lower() in (
            "1",
            "true",
            "yes",
        )
    except Exception:
        debug_enabled = False

    if debug_enabled:
        import ssl

        try:
            import certifi

            cert_path = certifi.where()
        except Exception:
            cert_path = None

        payload["debug"] = {
            "openssl": getattr(ssl, "OPENSSL_VERSION", "unknown"),
            "certifi_where": cert_path,
        }

    return payload


@api_router.get("/ready")
async def readiness_probe() -> Response:
    """Simple readiness endpoint suitable for platform probes.

    Returns HTTP 200 when the application is ready (DB ping successful).
    Returns HTTP 503 when the DB is unreachable.
    """
    db_ok = await db.validate_connection()
    if db_ok:
        return Response(content="ready", status_code=200)
    # Unhealthy
    raise HTTPException(status_code=503, detail="unavailable")


# Include the router in the main app
app.include_router(api_router)

# Include marketplace system routers
app.include_router(auth.router)
app.include_router(ads.router)
app.include_router(platforms.router)
app.include_router(platform_oauth.router)
app.include_router(ai.router)
app.include_router(diagrams.router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
