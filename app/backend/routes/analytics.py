"""
Analytics Routes

Provides analytics and reporting endpoints for user data, listings performance,
and platform metrics.
"""

import asyncio
import copy
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Tuple

from auth import get_current_user
from db import get_typed_db
from fastapi import APIRouter, Depends, HTTPException, Query

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

RECOMMENDATIONS_CACHE_TTL_SECONDS = 300
_RECOMMENDATIONS_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
SUPABASE_QUERY_TIMEOUT_SECONDS = float(os.getenv("SUPABASE_QUERY_TIMEOUT", "8"))


# Dashboard Stats (already implemented in ads.py, but adding here for completeness)
@router.get("/dashboard")
async def get_dashboard_analytics(
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard analytics for the user.
    This is a duplicate of the ads.py endpoint for API consistency.
    """
    # Redirect to ads.py implementation or implement here
    # For now, return basic structure
    return {
        "total_listings": 0,
        "active_listings": 0,
        "total_posts": 0,
        "total_views": 0,
        "total_leads": 0,
        "platforms_connected": 0,
        "revenue": 0,
        "conversion_rate": 0.0,
        "period": "30d",
    }


@router.get("/listings")
async def get_listing_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    platform: str = Query(None, description="Filter by platform"),
    user_id: str = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get detailed analytics for user's listings.
    """
    db = get_typed_db()

    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    analytics = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase

            client = get_supabase()
            if client:
                # Get listings for user
                listings_result = (
                    client.table("listings")
                    .select("*")
                    .eq("user_id", user_id)
                    .execute()
                )

                for listing in listings_result.data:
                    listing_id = listing["id"]

                    # Get posted ads for this listing
                    posted_result = (
                        client.table("posted_ads")
                        .select("*")
                        .eq("ad_id", listing_id)
                        .execute()
                    )

                    # Get analytics data from posted_ads (simplified)
                    total_views = 0
                    total_clicks = 0
                    total_leads = 0

                    for posted in posted_result.data:
                        total_views += posted.get("views", 0)
                        total_clicks += posted.get("clicks", 0)
                        total_leads += posted.get("leads", 0)

                    analytics.append(
                        {
                            "listing_id": listing_id,
                            "title": listing.get("title", ""),
                            "platform": platform or "all",
                            "views": total_views,
                            "clicks": total_clicks,
                            "leads": total_leads,
                            "conversion_rate": (total_clicks / total_views * 100)
                            if total_views > 0
                            else 0,
                            "status": listing.get("status", "draft"),
                            "created_at": listing.get("created_at"),
                        }
                    )

                logger.info(
                    f"Retrieved listing analytics for {len(analytics)} listings from Supabase"
                )
        except Exception as e:
            logger.error(f"Failed to get listing analytics from Supabase: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get listing analytics"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        # Get listings from MongoDB
        query = {"user_id": user_id}
        if platform:
            query["platforms"] = {"$in": [platform]}

        listings = await db["ads"].find(query).to_list(1000)

        for listing in listings:
            listing_id = listing["id"]

            # Get posted ads analytics
            posted_ads = await db["posted_ads"].find({"ad_id": listing_id}).to_list(100)

            total_views = sum(pa.get("views", 0) for pa in posted_ads)
            total_clicks = sum(pa.get("clicks", 0) for pa in posted_ads)
            total_leads = sum(pa.get("leads", 0) for pa in posted_ads)

            analytics.append(
                {
                    "listing_id": listing_id,
                    "title": listing.get("title", ""),
                    "platform": platform or "all",
                    "views": total_views,
                    "clicks": total_clicks,
                    "leads": total_leads,
                    "conversion_rate": (total_clicks / total_views * 100)
                    if total_views > 0
                    else 0,
                    "status": listing.get("status", "draft"),
                    "created_at": listing.get("created_at"),
                }
            )

    return analytics


@router.get("/platforms")
async def get_platform_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get analytics broken down by platform.
    """
    db = get_typed_db()

    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    platform_stats = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase

            client = get_supabase()
            if client:
                # Get all posted ads for user and group by platform
                posted_result = client.table("posted_ads").select("*").execute()

                # Group by platform
                platform_data = {}
                for posted in posted_result.data:
                    platform = posted["platform"]
                    if platform not in platform_data:
                        platform_data[platform] = {
                            "platform": platform,
                            "total_posts": 0,
                            "total_views": 0,
                            "total_clicks": 0,
                            "total_leads": 0,
                            "success_rate": 0.0,
                        }

                    platform_data[platform]["total_posts"] += 1
                    platform_data[platform]["total_views"] += posted.get("views", 0)
                    platform_data[platform]["total_clicks"] += posted.get("clicks", 0)
                    platform_data[platform]["total_leads"] += posted.get("leads", 0)

                # Calculate success rates and convert to list
                for platform, data in platform_data.items():
                    data["success_rate"] = (
                        (data["total_leads"] / data["total_posts"] * 100)
                        if data["total_posts"] > 0
                        else 0
                    )
                    platform_stats.append(data)

                logger.info(
                    f"Retrieved platform analytics for {len(platform_stats)} platforms from Supabase"
                )
        except Exception as e:
            logger.error(f"Failed to get platform analytics from Supabase: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get platform analytics"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        # Aggregate posted ads by platform
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$platform",
                    "total_posts": {"$sum": 1},
                    "total_views": {"$sum": "$views"},
                    "total_clicks": {"$sum": "$clicks"},
                    "total_leads": {"$sum": "$leads"},
                }
            },
            {"$sort": {"total_posts": -1}},
        ]

        results = await db["posted_ads"].aggregate(pipeline).to_list(20)

        for result in results:
            platform_stats.append(
                {
                    "platform": result["_id"],
                    "total_posts": result["total_posts"],
                    "total_views": result.get("total_views", 0),
                    "total_clicks": result.get("total_clicks", 0),
                    "total_leads": result.get("total_leads", 0),
                    "success_rate": (
                        result.get("total_leads", 0) / result["total_posts"] * 100
                    )
                    if result["total_posts"] > 0
                    else 0,
                }
            )

    return platform_stats


@router.get("/revenue")
async def get_revenue_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get revenue analytics (from Stripe data).
    """
    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    # For now, return mock data since revenue tracking would need additional tables
    # In production, this would aggregate from Stripe webhook data stored in database
    return {
        "total_revenue": 0.0,
        "monthly_recurring": 0.0,
        "one_time_payments": 0.0,
        "refunds": 0.0,
        "currency": "USD",
        "period": f"{start_date} to {end_date}",
        "note": "Revenue tracking requires additional database schema for Stripe data",
    }


@router.get("/performance")
async def get_performance_metrics(
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get overall performance metrics for the user.
    """
    return {
        "account_age_days": 0,
        "total_listings_created": 0,
        "average_listing_lifetime": 0,
        "platform_diversity_score": 0.0,
        "response_time_avg": 0,
        "conversion_funnel": {
            "listings_created": 0,
            "listings_posted": 0,
            "leads_generated": 0,
            "conversions": 0,
        },
        "trends": {
            "listings_growth": 0.0,
            "engagement_growth": 0.0,
            "revenue_growth": 0.0,
        },
    }


@router.get("/recommendations")
async def get_growth_recommendations(
    user_id: str = Depends(get_current_user),
    force_refresh: bool = Query(
        False, description="Bypass cache and recompute recommendations"
    ),
) -> Dict[str, Any]:
    """Return actionable growth strategies based on recent performance."""

    if force_refresh:
        _RECOMMENDATIONS_CACHE.pop(user_id, None)
    else:
        cached = _get_cached_recommendations(user_id)
        if cached:
            return cached

    data = await _build_growth_recommendations(user_id)
    _set_cached_recommendations(user_id, data)
    return data


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        text = str(value)
        if text.endswith("Z"):
            text = text.replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _get_cached_recommendations(user_id: str) -> Dict[str, Any] | None:
    entry = _RECOMMENDATIONS_CACHE.get(user_id)
    if not entry:
        return None
    timestamp, payload = entry
    if (time.time() - timestamp) > RECOMMENDATIONS_CACHE_TTL_SECONDS:
        _RECOMMENDATIONS_CACHE.pop(user_id, None)
        return None
    return copy.deepcopy(payload)


def _set_cached_recommendations(user_id: str, payload: Dict[str, Any]) -> None:
    _RECOMMENDATIONS_CACHE[user_id] = (
        time.time(),
        copy.deepcopy(payload),
    )


async def _run_supabase_query(func: Callable[[], Any], description: str) -> Any:
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, func), SUPABASE_QUERY_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError as exc:
        raise TimeoutError(
            f"{description} timed out after {SUPABASE_QUERY_TIMEOUT_SECONDS}s"
        ) from exc


async def _build_growth_recommendations(user_id: str) -> Dict[str, Any]:
    from supabase_db import get_supabase

    diagnostics: List[str] = []
    recommendations: List[Dict[str, Any]] = []
    timeframe_days = 30
    lookback = datetime.utcnow() - timedelta(days=timeframe_days)

    client = get_supabase()
    posted_ads: List[Dict[str, Any]] = []
    listings: List[Dict[str, Any]] = []

    if client:
        try:
            posted_ads_resp = await _run_supabase_query(
                lambda: (
                    client.table("posted_ads")
                    .select("*")
                    .eq("user_id", user_id)
                    .gte("created_at", lookback.isoformat())
                    .limit(1000)
                    .execute()
                ),
                "Posted ads lookup",
            )
            posted_ads = posted_ads_resp.data or []
        except TimeoutError as exc:
            diagnostics.append(str(exc))
        except Exception as exc:
            diagnostics.append(f"Unable to load posted ads: {exc}")

        try:
            listings_resp = await _run_supabase_query(
                lambda: (
                    client.table("listings")
                    .select("*")
                    .eq("user_id", user_id)
                    .limit(500)
                    .execute()
                ),
                "Listings metadata lookup",
            )
            listings = listings_resp.data or []
        except TimeoutError as exc:
            diagnostics.append(str(exc))
        except Exception as exc:
            diagnostics.append(f"Unable to load listings metadata: {exc}")
    else:
        diagnostics.append(
            "Supabase not configured; returning generic recommendations."
        )

    platform_stats = defaultdict(
        lambda: {"count": 0, "views": 0.0, "leads": 0.0, "clicks": 0.0}
    )
    stale_listings = 0
    days_since_last_post: List[int] = []

    for item in posted_ads:
        platform = (item.get("platform") or "unspecified").lower()
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["views"] += float(item.get("views", 0) or 0)
        platform_stats[platform]["leads"] += float(item.get("leads", 0) or 0)
        platform_stats[platform]["clicks"] += float(item.get("clicks", 0) or 0)

        created_at = _parse_datetime(item.get("created_at"))
        if created_at:
            delta_days = max(0, (datetime.utcnow() - created_at).days)
            days_since_last_post.append(delta_days)
            if delta_days > 10 and (item.get("leads") in (0, None)):
                stale_listings += 1

    total_posts = sum(stat["count"] for stat in platform_stats.values())
    avg_conversion = 0.0
    if total_posts:
        avg_conversion = (
            sum(
                ((stat["leads"] + 1) / (stat["views"] + 1)) * stat["count"]
                for stat in platform_stats.values()
            )
            / total_posts
        )

    if total_posts == 0:
        recommendations.append(
            {
                "priority": "high",
                "title": "Publish at least 3 listings",
                "detail": "No recent posting activity detected in the last 30 days.",
                "action": "Create new listings or import existing ones to unlock analytics.",
            }
        )
    else:
        slow_platforms = []
        strong_platforms = []
        for platform, stat in platform_stats.items():
            conversion = (stat["leads"] + 1) / (stat["views"] + 1)
            entry = {
                "platform": platform,
                "conversion": round(conversion, 3),
                "posts": stat["count"],
            }
            if conversion < 0.03 and stat["views"] >= 20:
                slow_platforms.append(entry)
            if conversion >= 0.1 and stat["count"] >= 3:
                strong_platforms.append(entry)

        if slow_platforms:
            slow_platforms.sort(key=lambda item: item["conversion"])
            target = slow_platforms[0]
            recommendations.append(
                {
                    "priority": "high",
                    "title": f"Improve conversion on {target['platform'].title()}",
                    "detail": f"Conversion is {target['conversion'] * 100:.1f}% with {target['posts']} posts.",
                    "action": "Refresh photos, tighten pricing, and respond faster to leads on this platform.",
                }
            )

        if strong_platforms:
            strong_platforms.sort(key=lambda item: item["conversion"], reverse=True)
            hero = strong_platforms[0]
            recommendations.append(
                {
                    "priority": "medium",
                    "title": f"Scale {hero['platform'].title()} listings",
                    "detail": f"This channel converts at {hero['conversion'] * 100:.1f}% across {hero['posts']} posts.",
                    "action": "Clone top-performing templates and double the weekly volume.",
                }
            )

    if stale_listings:
        recommendations.append(
            {
                "priority": "medium",
                "title": "Refresh stale inventory",
                "detail": f"{stale_listings} posts have no leads after 10 days.",
                "action": "Update photos, lower prices, or mark as sold to maintain trust signals.",
            }
        )

    if listings:
        categories = defaultdict(int)
        for listing in listings:
            category = (listing.get("category") or "uncategorized").lower()
            categories[category] += 1
        if len(categories) == 1:
            sole = next(iter(categories))
            recommendations.append(
                {
                    "priority": "medium",
                    "title": "Diversify catalog",
                    "detail": f"Only {sole} listings detected; adding complementary categories increases buyer reach.",
                    "action": "Import at least one new category to improve discovery algorithms.",
                }
            )

    posting_cadence = min(days_since_last_post) if days_since_last_post else None
    if posting_cadence and posting_cadence > 3:
        recommendations.append(
            {
                "priority": "low",
                "title": "Increase posting cadence",
                "detail": f"Average gap between posts is {posting_cadence} days.",
                "action": "Schedule daily micro-posts or republish top listings automatically.",
            }
        )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "timeframe_days": timeframe_days,
        "summary": {
            "total_posts": total_posts,
            "avg_conversion": round(avg_conversion, 3),
            "active_platforms": len(platform_stats),
            "stale_listings": stale_listings,
        },
        "recommendations": recommendations,
        "diagnostics": diagnostics,
    }
