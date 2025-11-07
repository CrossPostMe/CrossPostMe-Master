import random
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_optional_current_user
from backend.db import get_db
from backend.models import Ad, AdAnalytics, AdCreate, AdUpdate, DashboardStats, PostedAd

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

    await db["ads"].insert_one(doc)
    return ad_obj


# Get All Ads
@router.get("/", response_model=list[Ad])
async def get_ads(
    status: str | None = None,
    platform: str | None = None,
) -> list[Ad]:
    query: dict[str, Any] = {}
    if status:
        query["status"] = status
    if platform:
        query["platforms"] = platform

    ads = await db["ads"].find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)

    # Convert ISO string timestamps back to datetime objects
    for ad in ads:
        deserialize_datetime_fields(ad, ["created_at", "scheduled_time"])

    return [Ad(**ad) for ad in ads]


# Get Ad by ID
@router.get("/{ad_id}", response_model=Ad)
async def get_ad(ad_id: str) -> Ad:
    ad = await db["ads"].find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return Ad(**ad)


# Update Ad
@router.put("/{ad_id}", response_model=Ad)
async def update_ad(ad_id: str, ad_update: AdUpdate) -> Ad:
    ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    update_data = ad_update.model_dump(exclude_unset=True)

    # Convert datetime fields to ISO strings for MongoDB
    serialize_datetime_fields(update_data, ["scheduled_time"])

    if update_data:
        await db["ads"].update_one({"id": ad_id}, {"$set": update_data})

    updated_ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})

    # Convert ISO string timestamps back to datetime objects
    deserialize_datetime_fields(updated_ad, ["created_at", "scheduled_time"])

    return Ad(**updated_ad)


# Delete Ad
@router.delete("/{ad_id}")
async def delete_ad(ad_id: str) -> dict[str, str]:
    result = await db["ads"].delete_one({"id": ad_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ad not found")
    return {"message": "Ad deleted successfully"}


# Post Ad to Platform (Real Integration)
@router.post("/{ad_id}/post", response_model=PostedAd)
async def post_ad(
    ad_id: str,
    platform: str,
    user_id: str = Depends(get_optional_current_user),
) -> PostedAd:
    from backend.automation import AdData, PostStatus, automation_manager

    ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Get platform credentials for this user/platform using secure credential manager
    from backend.automation.credentials import credential_manager

    credentials = await credential_manager.get_credentials(user_id, platform)

    if not credentials:
        raise HTTPException(
            status_code=400,
            detail=f"No credentials found for {platform}. Please connect your account first.",
        )

    # Get platform account info for contact details
    platform_account = await db["platform_accounts"].find_one(
        {
            "platform": platform,
            "status": "active",
            "user_id": ad.get("user_id", user_id),
        },
        {"_id": 0},
    )

    # Convert ad data to automation format
    contact_info = {}
    email = credentials.email or (
        platform_account.get("account_email") if platform_account else None
    )
    phone = credentials.phone or (
        platform_account.get("phone") if platform_account else None
    )
    if email is not None:
        contact_info["email"] = str(email)
    if phone is not None:
        contact_info["phone"] = str(phone)
    ad_data = AdData(
        title=ad["title"],
        description=ad["description"],
        price=ad["price"],
        category=ad["category"],
        location=ad["location"],
        images=ad.get("images", []),
        contact_info=contact_info if contact_info else None,
    )

    try:
        # Use real platform automation
        result = await automation_manager.post_to_platform(
            platform,
            ad_data,
            credentials,
        )

        if result.status == PostStatus.SUCCESS:
            # Create successful posted ad record
            posted_ad_dict = {
                "ad_id": ad_id,
                "platform": platform,
                "platform_ad_id": result.platform_ad_id,
                "post_url": result.post_url,
                "status": "active",
            }
            posted_ad = PostedAd(**normalize_posted_ad_dict(posted_ad_dict))

            # Save to database
            doc = posted_ad.model_dump()
            serialize_datetime_fields(doc, ["posted_at"])
            await db["posted_ads"].insert_one(doc)

            # Update ad status
            await db["ads"].update_one({"id": ad_id}, {"$set": {"status": "posted"}})

            return posted_ad

        # Handle posting failure
        error_message = f"Failed to post to {platform}: {result.message}"

        if result.status == PostStatus.RATE_LIMITED:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limited. Try again in {result.retry_after} seconds.",
            )
        if result.status == PostStatus.LOGIN_REQUIRED:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed for {platform}. Please check your credentials.",
            )
        if result.status == PostStatus.CAPTCHA_REQUIRED:
            raise HTTPException(
                status_code=423,
                detail=f"CAPTCHA required for {platform}. Manual intervention needed.",
            )
        raise HTTPException(status_code=400, detail=error_message)

    except Exception as e:
        # Log error and return HTTP exception
        import logging

        logger = logging.getLogger("ads.post")
        logger.error(f"Error posting to {platform}: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal error posting to {platform}: {e!s}",
        ) from e


# Post Ad to Multiple Platforms
@router.post("/{ad_id}/post-multiple")
async def post_ad_multiple_platforms(
    ad_id: str,
    platforms: list[str],
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    from backend.automation import AdData, automation_manager

    ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Get credentials for all requested platforms using secure credential manager
    from backend.automation.credentials import credential_manager

    credentials_map = {}

    for platform in platforms:
        credentials = await credential_manager.get_credentials(user_id, platform)
        if credentials:
            credentials_map[platform] = credentials

    if not credentials_map:
        raise HTTPException(
            status_code=400,
            detail="No active platform accounts found for the requested platforms",
        )

    # Convert ad data
    ad_data = AdData(
        title=ad["title"],
        description=ad["description"],
        price=ad["price"],
        category=ad["category"],
        location=ad["location"],
        images=ad.get("images", []),
    )

    # Post to multiple platforms concurrently
    results = await automation_manager.post_to_multiple_platforms(
        list(credentials_map.keys()),
        ad_data,
        credentials_map,
    )

    # Process results and save successful posts
    successful_posts = []
    failed_posts = []

    for platform, result in results.items():
        if result.status.value == "success":
            # Save successful post
            posted_ad_dict = {
                "ad_id": ad_id,
                "platform": platform,
                "platform_ad_id": result.platform_ad_id,
                "post_url": result.post_url,
                "status": "active",
            }
            posted_ad = PostedAd(**normalize_posted_ad_dict(posted_ad_dict))

            doc = posted_ad.model_dump()
            serialize_datetime_fields(doc, ["posted_at"])
            await db["posted_ads"].insert_one(doc)

            successful_posts.append(
                {
                    "platform": platform,
                    "status": "success",
                    "post_url": result.post_url,
                    "platform_ad_id": result.platform_ad_id,
                },
            )
        else:
            failed_posts.append(
                {
                    "platform": platform,
                    "status": result.status.value,
                    "message": result.message,
                    "retry_after": result.retry_after,
                },
            )

    # Update ad status if any posts were successful
    if successful_posts:
        await db["ads"].update_one({"id": ad_id}, {"$set": {"status": "posted"}})

    return {
        "ad_id": ad_id,
        "successful_posts": successful_posts,
        "failed_posts": failed_posts,
        "total_requested": len(platforms),
        "total_successful": len(successful_posts),
        "total_failed": len(failed_posts),
    }


# Get Posted Ads
@router.get("/{ad_id}/posts", response_model=list[PostedAd])
async def get_posted_ads(ad_id: str) -> list[PostedAd]:
    posted_ads = await db["posted_ads"].find({"ad_id": ad_id}, {"_id": 0}).to_list(1000)

    # Convert ISO string timestamps back to datetime objects and coerce types
    for pa in posted_ads:
        deserialize_datetime_fields(pa, ["posted_at"])

    return [PostedAd(**normalize_posted_ad_dict(pa)) for pa in posted_ads]


# Get All Posted Ads
@router.get("/posted/all", response_model=list[PostedAd])
async def get_all_posted_ads(platform: str | None = None) -> list[PostedAd]:
    query: dict[str, Any] = {}
    if platform:
        query["platform"] = platform

    posted_ads = (
        await db["posted_ads"]
        .find(query, {"_id": 0})
        .sort("posted_at", -1)
        .to_list(1000)
    )

    # Convert ISO string timestamps back to datetime objects and coerce types
    for pa in posted_ads:
        deserialize_datetime_fields(pa, ["posted_at"])

    return [PostedAd(**normalize_posted_ad_dict(pa)) for pa in posted_ads]


# Get Dashboard Stats
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    total_ads = await db["ads"].count_documents({})
    active_ads = await db["ads"].count_documents({"status": "posted"})
    total_posts = await db["posted_ads"].count_documents({})

    # Calculate total views and leads
    posted_ads = await db["posted_ads"].find({}).to_list(1000)
    total_views = sum(pa.get("views", 0) for pa in posted_ads)
    total_leads = sum(pa.get("leads", 0) for pa in posted_ads)

    # Count unique platforms
    platforms = await db["platform_accounts"].distinct("platform")
    platforms_connected = len(platforms)

    return DashboardStats(
        total_ads=total_ads,
        active_ads=active_ads,
        total_posts=total_posts,
        total_views=total_views,
        total_leads=total_leads,
        platforms_connected=platforms_connected,
    )


# Get Ad Analytics
@router.get("/{ad_id}/analytics", response_model=list[AdAnalytics])
async def get_ad_analytics(ad_id: str, days: int = 7) -> list[AdAnalytics]:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    posted_ads = (
        await db["posted_ads"]
        .find({"ad_id": ad_id, "posted_at": {"$gte": start_date}})
        .to_list(1000)
    )

    analytics = []
    for pa in posted_ads:
        analytics.append(
            AdAnalytics(
                ad_id=ad_id,
                platform=pa.get("platform"),
                views=pa.get("views", random.randint(50, 500)),
                clicks=pa.get("clicks", random.randint(10, 100)),
                leads=pa.get("leads", random.randint(1, 20)),
                messages=pa.get("messages", random.randint(1, 15)),
                conversion_rate=round(random.uniform(2.0, 8.0), 2),
                date=pa.get("posted_at"),
            ),
        )

    return analytics
