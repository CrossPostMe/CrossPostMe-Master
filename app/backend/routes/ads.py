def deserialize_datetime_fields(
    doc: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    """Convert ISO strings back to datetime objects."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            try:
                doc[field] = datetime.fromisoformat(doc[field])
            except ValueError:
                # Handle invalid ISO format - set to current time for fallback
                if field == "created_at" or field == "posted_at":
                    doc[field] = datetime.now(timezone.utc)
    return doc
def normalize_posted_ad_dict(doc: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow-copied dict with fields coerced to the types
    expected by the PostedAd model (datetime for posted_at, ints for
    views/clicks/leads, strings or None for platform_ad_id/post_url).
    This keeps runtime semantics identical while satisfying static typing.
    """
    d: dict[str, Any] = dict(doc or {})
db = get_db()

import logging
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.db import get_db
from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_optional_current_user
from backend.models import Ad, AdAnalytics, AdCreate, AdUpdate, DashboardStats, PostedAd

logger = logging.getLogger(__name__)

# Feature flags for Supabase migration
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/ads", tags=["ads"])


# Helper functions for datetime serialization/deserialization
def serialize_datetime_fields(doc: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Convert datetime objects to ISO strings for MongoDB storage."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], datetime):
            doc[field] = doc[field].isoformat()
    return doc


def deserialize_datetime_fields(
    doc: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    """Convert ISO strings back to datetime objects."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            try:
                doc[field] = datetime.fromisoformat(doc[field])
            except ValueError:
                # Handle invalid ISO format - set to current time for fallback
                if field == "created_at" or field == "posted_at":
                    doc[field] = datetime.now(timezone.utc)
    return doc


# Helpers to normalize posted ad documents before constructing PostedAd
def normalize_posted_ad_dict(doc: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow-copied dict with fields coerced to the types
    expected by the PostedAd model (datetime for posted_at, ints for
    views/clicks/leads, strings or None for platform_ad_id/post_url).
    This keeps runtime semantics identical while satisfying static typing.
    """
    d: dict[str, Any] = dict(doc or {})

    # posted_at -> datetime
    if "posted_at" in d and d["posted_at"] is not None:
        v = d["posted_at"]
        if isinstance(v, str):
            try:
                d["posted_at"] = datetime.fromisoformat(v)
            except Exception:
                d["posted_at"] = datetime.now(timezone.utc)
    else:
        d["posted_at"] = datetime.now(timezone.utc)

    # Optional string fields
    for key in ("platform_ad_id", "post_url"):
        if key in d and d[key] is not None:
            d[key] = str(d[key])
        else:
            d[key] = None

    # Numeric counters
    for key in ("views", "clicks", "leads"):
        try:
            d[key] = int(d.get(key, 0)) if d.get(key) is not None else 0
        except Exception:
            d[key] = 0

    return d


# Typed database wrapper
db = get_db()


# Create Ad
@router.post("/", response_model=Ad)
async def create_ad(ad: AdCreate) -> Ad:
    ad_dict = ad.model_dump()
    ad_obj = Ad(**ad_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = ad_obj.model_dump()
    serialize_datetime_fields(doc, ["created_at", "scheduled_time"])

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from backend.supabase_db import get_supabase

            client = get_supabase()
            if client:
                # Insert into Supabase listings table
                listing_data = {
                    "id": doc["id"],
                    "user_id": doc.get("user_id"),
                    "title": doc["title"],
                    "description": doc.get("description"),
                    "price": float(doc["price"]) if doc.get("price") else None,
                    "category": doc.get("category"),
                    "condition": doc.get("condition"),
                    "images": doc.get("images", []),
                    "location": doc.get("location"),
                    "status": doc.get("status", "draft"),
                    "platforms": doc.get("platforms", {}),
                    "metadata": {
                        "scheduled_time": doc.get("scheduled_time"),
                        "original_doc": doc,  # Store full doc for compatibility
                    },
                }
                client.table("listings").insert(listing_data).execute()
                logger.info(f"Ad created in Supabase: {doc['id']}")

                # PARALLEL WRITE: Also write to MongoDB
                if PARALLEL_WRITE:
                    try:
                        await db["ads"].insert_one(doc)
                        logger.info(
                            f"✅ Parallel write to MongoDB successful for ad: {doc['id']}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"⚠️  Parallel MongoDB write failed for ad {doc['id']}: {e}"
                        )
        except Exception as e:
            logger.error(f"Ad creation failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to create ad")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        await db["ads"].insert_one(doc)
        logger.info(f"Ad created in MongoDB: {doc['id']}")

    return ad_obj

...existing code...
