"""
Listing Assistant API Routes

AI-powered assistant for generating platform-specific listing content.
Helps users post to platforms without APIs by generating optimized,
ready-to-copy content.
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import openai
from auth import get_current_user
from db import get_typed_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not set. AI features will not work.")

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
db = get_typed_db()


# ============================================================================
# Models
# ============================================================================


class ListingInput(BaseModel):
    """Input for generating listing content."""

    title: str = Field(..., description="Product title", max_length=200)
    description: str | None = Field(None, description="Product description")
    price: float = Field(..., description="Price in USD", gt=0)
    category: str | None = Field(None, description="Product category")
    condition: str = Field(default="new", description="new, used, refurbished")
    brand: str | None = Field(None, description="Brand name")
    images: List[str] = Field(default=[], description="Image URLs")
    tags: List[str] = Field(default=[], description="Keywords/tags")


class PlatformRequirements(BaseModel):
    """Platform-specific requirements and constraints."""

    platform: str = Field(..., description="Platform name")
    title_max_length: int = Field(default=80)
    description_max_length: int = Field(default=5000)
    description_style: str = Field(
        default="conversational",
        description="formal, conversational, bullet-points",
    )
    required_fields: List[str] = Field(default=[])
    emoji_allowed: bool = Field(default=True)
    html_allowed: bool = Field(default=False)


class GeneratedContent(BaseModel):
    """Generated content ready for copy/paste."""

    platform: str
    title: str
    description: str
    price_formatted: str
    suggested_tags: List[str]
    seo_keywords: List[str]
    character_counts: Dict[str, int]
    tips: List[str]
    suggestions: List[str] = Field(default_factory=list)
    issues: List["AssistantIssue"] = Field(default_factory=list)
    processing_time_ms: int | None = Field(default=None)


class AssistantIssue(BaseModel):
    """Issues or warnings detected while preparing content."""

    severity: str = Field(default="info", description="info|warning|critical")
    field: str | None = None
    message: str
    recommendation: str | None = None


class BulkGenerateRequest(BaseModel):
    """Request to generate content for multiple platforms."""

    listing: ListingInput
    platforms: List[str] = Field(
        default=["offerup", "poshmark", "facebook", "craigslist"],
        description="Platforms to generate for",
    )


# ============================================================================
# Platform Configurations
# ============================================================================

PLATFORM_CONFIGS = {
    "offerup": PlatformRequirements(
        platform="OfferUp",
        title_max_length=80,
        description_max_length=1000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "category"],
    ),
    "poshmark": PlatformRequirements(
        platform="Poshmark",
        title_max_length=80,
        description_max_length=500,
        description_style="bullet-points",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "brand", "size"],
    ),
    "facebook": PlatformRequirements(
        platform="Facebook Marketplace",
        title_max_length=100,
        description_max_length=10000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "location"],
    ),
    "craigslist": PlatformRequirements(
        platform="Craigslist",
        title_max_length=70,
        description_max_length=4096,
        description_style="formal",
        emoji_allowed=False,
        html_allowed=True,
        required_fields=["title", "price"],
    ),
    "mercari": PlatformRequirements(
        platform="Mercari",
        title_max_length=80,
        description_max_length=1000,
        description_style="conversational",
        emoji_allowed=True,
        html_allowed=False,
        required_fields=["title", "price", "category", "brand"],
    ),
    "ebay": PlatformRequirements(
        platform="eBay",
        title_max_length=80,
        description_max_length=32000,
        description_style="formal",
        emoji_allowed=False,
        html_allowed=True,
        required_fields=["title", "price", "category"],
    ),
}

TRENDING_CACHE_TTL_SECONDS = 300
_TRENDING_CACHE: Dict[Tuple[str, int], Tuple[float, Dict[str, Any], List[str]]] = {}
SUPABASE_QUERY_TIMEOUT_SECONDS = float(os.getenv("SUPABASE_QUERY_TIMEOUT", "8"))


# ============================================================================
# AI Generation Functions
# ============================================================================


async def generate_optimized_title(
    original_title: str,
    platform_config: PlatformRequirements,
    brand: str | None = None,
    tags: List[str] | None = None,
) -> str:
    """Generate platform-optimized title using AI."""

    if not openai.api_key:
        # Fallback: Simple truncation
        return original_title[: platform_config.title_max_length]

    max_length = platform_config.title_max_length
    platform = platform_config.platform

    prompt = f"""Generate an optimized product title for {platform}.

Original title: {original_title}
Brand: {brand or "N/A"}
Tags: {", ".join(tags or [])}

Requirements:
- Maximum {max_length} characters
- Include brand if provided
- Include key selling points
- SEO-friendly
- No emoji: {not platform_config.emoji_allowed}

Return ONLY the optimized title, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )

        generated_title = str(response.choices[0].message.content).strip()
        return str(generated_title[: platform_config.title_max_length])

    except Exception as e:
        logger.error(f"AI title generation failed: {e}")
        return original_title[: platform_config.title_max_length]


async def generate_optimized_description(
    title: str,
    original_description: str | None,
    platform_config: PlatformRequirements,
    condition: str = "new",
    brand: str | None = None,
    price: float = 0,
) -> str:
    """Generate platform-optimized description using AI."""

    if not openai.api_key:
        # Fallback: Return original or placeholder
        return original_description or f"For sale: {title}. Price: ${price:.2f}"

    max_length = platform_config.description_max_length
    platform = platform_config.platform
    style = platform_config.description_style

    prompt = f"""Generate a compelling product description for {platform}.

Product: {title}
Brand: {brand or "Generic"}
Condition: {condition}
Price: ${price:.2f}
Original description: {original_description or "None provided"}

Requirements:

Return ONLY the description, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8,
        )

        generated_desc = str(response.choices[0].message.content).strip()
        return str(generated_desc[: platform_config.description_max_length])

    except Exception as e:
        logger.error(f"AI description generation failed: {e}")
        return (original_description or f"For sale: {title}")[
            : platform_config.description_max_length
        ]


async def generate_tags(
    title: str, description: str | None, category: str | None
) -> List[str]:
    """Generate SEO tags using AI."""

    if not openai.api_key:
        # Fallback: Extract from title
        return title.lower().split()[:10]

    prompt = f"""Generate 10-15 SEO-friendly tags/keywords for this product:

Title: {title}
Description: {description or "N/A"}
Category: {category or "N/A"}

Requirements:
- Relevant search terms
- Mix of general and specific
- Include brand/model if applicable
- Common misspellings if relevant
- Lowercase, comma-separated

Return ONLY the tags, nothing else."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.6,
        )

        tags_text = response.choices[0].message.content.strip()
        tags = [tag.strip() for tag in tags_text.split(",")]
        return tags[:15]

    except Exception as e:
        logger.error(f"AI tag generation failed: {e}")
        return title.lower().split()[:10]


def format_price_for_platform(price: float, platform: str) -> str:
    """Format price according to platform conventions."""

    price_map = {
        "offerup": f"${price:.0f}",  # No decimals
        "poshmark": f"${price:.2f}",
        "facebook": f"${price:.0f}",
        "craigslist": f"${price:.0f}",
        "mercari": f"${price:.2f}",
        "ebay": f"${price:.2f}",
    }

    return price_map.get(platform, f"${price:.2f}")


def generate_platform_tips(platform: str, listing: ListingInput) -> List[str]:
    """Generate platform-specific posting tips."""

    tips_map = {
        "offerup": [
            "✅ Post during peak hours (6-9 PM local time)",
            "📸 Use well-lit photos with plain background",
            "💬 Respond to messages within 1 hour",
            "📍 Set accurate location for local pickup",
            "🏷️ Mark 'Firm on Price' if not negotiable",
        ],
        "poshmark": [
            "👗 Include brand name in title",
            "📏 List exact measurements (not just size)",
            "🏷️ Tag with brand, size, color, style",
            "📦 Offer bundle discounts",
            "🎉 Share to parties for visibility",
        ],
        "facebook": [
            "📍 List in relevant Buy & Sell groups",
            "✅ Mark availability: 'Available' or 'Pending'",
            "📞 Enable messaging for quick responses",
            "🚗 Specify if shipping or local only",
            "⭐ Link to your FB profile (builds trust)",
        ],
        "craigslist": [
            "🔒 Never share personal email in listing",
            "💰 State 'Cash only' if preferred",
            "🏪 Meet in public place for safety",
            "📅 Repost every 48 hours for visibility",
            "❌ Watch out for scams (fake checks)",
        ],
    }

    return tips_map.get(platform, ["✅ Take clear photos", "💬 Respond quickly"])


def detect_listing_issues(
    listing: ListingInput, config: PlatformRequirements
) -> List[AssistantIssue]:
    """Surface potential blockers or optimizations before generating content."""

    issues: List[AssistantIssue] = []

    for required in config.required_fields:
        value = getattr(listing, required, None)
        if value in (None, "", [], 0):
            issues.append(
                AssistantIssue(
                    severity="warning",
                    field=required,
                    message=f"{required.title()} is required for {config.platform}",
                    recommendation=f"Add {required} before publishing to {config.platform}.",
                )
            )

    if listing.description and len(listing.description) > config.description_max_length:
        issues.append(
            AssistantIssue(
                severity="warning",
                field="description",
                message="Description exceeds platform character limit",
                recommendation=f"Trim description to under {config.description_max_length} characters.",
            )
        )

    if len(listing.images) < 2:
        issues.append(
            AssistantIssue(
                severity="info",
                field="images",
                message="Adding more images improves conversion",
                recommendation="Upload at least 3 well-lit photos",
            )
        )

    if listing.price <= 0:
        issues.append(
            AssistantIssue(
                severity="critical",
                field="price",
                message="Price must be greater than zero",
                recommendation="Set a realistic price before publishing",
            )
        )

    return issues


def build_dynamic_suggestions(listing: ListingInput, platform_key: str) -> List[str]:
    """Generate lightweight, human-readable suggestions."""

    suggestions: List[str] = []

    if listing.brand:
        suggestions.append(
            f"Lead with {listing.brand} in the first sentence for trust."
        )

    if listing.condition.lower() != "new":
        suggestions.append("Clarify wear/tear details to pre-empt buyer questions.")

    if platform_key in {"facebook", "offerup"} and not listing.tags:
        suggestions.append("Add at least 5 tags so local buyers can discover the item.")

    if len(listing.images) < 3:
        suggestions.append("Upload 3-5 photos: front, back, close-up, and scale shot.")

    if listing.category and listing.category.lower() in {"electronics", "appliances"}:
        suggestions.append(
            "Mention warranty status or receipts for high-value electronics."
        )

    return suggestions


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


def _get_cached_trending(
    user_id: str, days: int
) -> Tuple[Dict[str, Any], List[str]] | None:
    key = (user_id, days)
    entry = _TRENDING_CACHE.get(key)
    if not entry:
        return None
    timestamp, insights, issues = entry
    if (time.time() - timestamp) > TRENDING_CACHE_TTL_SECONDS:
        _TRENDING_CACHE.pop(key, None)
        return None
    return copy.deepcopy(insights), copy.deepcopy(issues)


def _set_cached_trending(
    user_id: str, days: int, insights: Dict[str, Any], issues: List[str]
) -> None:
    _TRENDING_CACHE[(user_id, days)] = (
        time.time(),
        copy.deepcopy(insights),
        copy.deepcopy(issues),
    )


async def _calculate_trending_insights(
    user_id: str, days: int = 14
) -> Tuple[Dict[str, Any], List[str]]:
    cached = _get_cached_trending(user_id, days)
    if cached:
        return cached

    lookback = datetime.utcnow() - timedelta(days=days)
    category_stats: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "views": 0, "leads": 0, "platforms": defaultdict(int)}
    )
    hour_stats: Dict[int, Dict[str, float]] = defaultdict(
        lambda: {"count": 0, "leads": 0}
    )
    platform_stats: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"count": 0, "views": 0, "leads": 0}
    )
    issues: List[str] = []

    client = get_supabase()
    listings_data: List[Dict[str, Any]] = []
    posted_ads: List[Dict[str, Any]] = []

    if client:
        try:
            listings_resp = await _run_supabase_query(
                lambda: (
                    client.table("listings")
                    .select("*")
                    .eq("user_id", user_id)
                    .gte("created_at", lookback.isoformat())
                    .limit(500)
                    .execute()
                ),
                "Listings lookup",
            )
            listings_data = listings_resp.data or []
        except TimeoutError as exc:
            issues.append(str(exc))
        except Exception as exc:
            issues.append(f"Unable to load listings from Supabase: {exc}")

        try:
            posted_resp = await _run_supabase_query(
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
            posted_ads = posted_resp.data or []
        except TimeoutError as exc:
            issues.append(str(exc))
        except Exception as exc:
            issues.append(f"Unable to load posted ads: {exc}")
    else:
        issues.append(
            "Supabase client not configured; returning heuristic recommendations."
        )

    for listing in listings_data:
        category = (listing.get("category") or "uncategorized").lower()
        category_stats[category]["count"] += 1
        platform_hint = (
            listing.get("platform")
            or listing.get("platform_hint")
            or listing.get("primary_platform")
            or "unspecified"
        )
        category_stats[category]["platforms"][platform_hint] += 1
        created_at = _parse_datetime(listing.get("created_at"))
        if created_at and created_at >= lookback:
            hour_stats[created_at.hour]["count"] += 1

    for posted in posted_ads:
        category = (
            posted.get("category")
            or posted.get("listing_category")
            or posted.get("tags_category")
            or "uncategorized"
        ).lower()
        platform = (posted.get("platform") or "unspecified").lower()
        views = float(posted.get("views", 0) or 0)
        leads = float(posted.get("leads", 0) or 0)

        category_stats[category]["views"] += views
        category_stats[category]["leads"] += leads
        category_stats[category]["platforms"][platform] += 1
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["views"] += views
        platform_stats[platform]["leads"] += leads

        created_at = _parse_datetime(posted.get("created_at"))
        if created_at and created_at >= lookback:
            hour_stats[created_at.hour]["leads"] += leads or 0
            hour_stats[created_at.hour]["count"] += 1

    if not category_stats:
        # provide generic insights if no data
        default_categories = [cfg.platform for cfg in PLATFORM_CONFIGS.values()]
        insights = {
            "category_trends": [
                {
                    "category": name,
                    "share_of_posts": round(1 / len(default_categories), 3),
                    "demand_score": 0.5,
                    "recommendation": "Post consistently to gather performance data.",
                }
                for name in default_categories
            ],
            "peak_activity": [{"hour": 20, "label": "8 PM", "confidence": "low"}],
            "platform_mix": [
                {
                    "platform": key,
                    "share": round(1 / len(PLATFORM_CONFIGS), 3),
                    "conversion_rate": 0.0,
                }
                for key in PLATFORM_CONFIGS.keys()
            ],
            "growth_actions": [
                "Connect your marketplaces to unlock personalized recommendations.",
                "Import historical listings so we can calculate momentum trends.",
            ],
        }
        _set_cached_trending(user_id, days, insights, issues)
        return insights, issues

    total_posts = sum(stat["count"] for stat in category_stats.values()) or 1
    category_trends = []
    for category, stat in category_stats.items():
        conversion = (stat["leads"] + 1) / (stat["views"] + 1)
        demand_score = round(
            ((stat["count"] / total_posts) * 0.6) + (conversion * 0.4), 3
        )
        recommendation = (
            "Double down on this category; it converts above average."
            if conversion >= 0.08
            else "Improve photos & pricing to raise conversion."
        )
        category_trends.append(
            {
                "category": category.title(),
                "share_of_posts": round(stat["count"] / total_posts, 3),
                "demand_score": demand_score,
                "conversion_rate": round(conversion, 3),
                "leading_platforms": sorted(
                    stat["platforms"].keys(),
                    key=lambda key: stat["platforms"][key],
                    reverse=True,
                )[:3],
                "recommendation": recommendation,
            }
        )

    category_trends.sort(key=lambda item: item["demand_score"], reverse=True)

    peak_activity = []
    for hour, stat in sorted(
        hour_stats.items(), key=lambda kv: kv[1]["leads"], reverse=True
    )[:4]:
        label = f"{hour:02d}:00"
        confidence = (
            "high" if stat["leads"] >= 5 else "medium" if stat["leads"] >= 2 else "low"
        )
        peak_activity.append({"hour": hour, "label": label, "confidence": confidence})

    platform_mix = []
    total_platform_posts = sum(stat["count"] for stat in platform_stats.values()) or 1
    for platform, stat in platform_stats.items():
        conversion = (stat["leads"] + 1) / (stat["views"] + 1)
        platform_mix.append(
            {
                "platform": platform,
                "share": round(stat["count"] / total_platform_posts, 3),
                "conversion_rate": round(conversion, 3),
            }
        )

    platform_mix.sort(key=lambda item: item["conversion_rate"], reverse=True)

    growth_actions: List[str] = []
    if category_trends:
        best = category_trends[0]
        growth_actions.append(
            f"Create 3 new {best['category']} listings this week; demand score {best['demand_score']}."
        )
    if peak_activity:
        slot = peak_activity[0]
        growth_actions.append(
            f"Schedule posts around {slot['label']} when buyers are most active ({slot['confidence']} confidence)."
        )
    underperformers = [p for p in platform_mix if p["conversion_rate"] < 0.05]
    if underperformers:
        names = ", ".join(p["platform"].title() for p in underperformers[:3])
        growth_actions.append(
            f"Refresh copy & pricing on {names}; conversion is lagging below 5%."
        )

    insights = {
        "category_trends": category_trends,
        "peak_activity": peak_activity,
        "platform_mix": platform_mix,
        "growth_actions": growth_actions,
    }
    _set_cached_trending(user_id, days, insights, issues)
    return insights, issues


# ============================================================================
# API Endpoints
# ============================================================================


async def _generate_content_for_platform(
    platform: str, listing: ListingInput
) -> GeneratedContent:
    platform_key = platform.lower()
    if platform_key not in PLATFORM_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform '{platform}' not supported. Available: {list(PLATFORM_CONFIGS.keys())}",
        )

    config = PLATFORM_CONFIGS[platform_key]
    start_time = time.perf_counter()

    issues = detect_listing_issues(listing, config)
    suggestions = build_dynamic_suggestions(listing, platform_key)

    title = await generate_optimized_title(
        listing.title, config, listing.brand, listing.tags
    )

    description = await generate_optimized_description(
        title,
        listing.description,
        config,
        listing.condition,
        listing.brand,
        listing.price,
    )

    tags = await generate_tags(title, description, listing.category)
    price_formatted = format_price_for_platform(listing.price, platform_key)
    tips = generate_platform_tips(platform_key, listing)

    processing_ms = int((time.perf_counter() - start_time) * 1000)

    return GeneratedContent(
        platform=config.platform,
        title=title,
        description=description,
        price_formatted=price_formatted,
        suggested_tags=tags[:10],
        seo_keywords=tags,
        character_counts={
            "title": len(title),
            "description": len(description),
            "title_max": config.title_max_length,
            "description_max": config.description_max_length,
        },
        tips=tips,
        suggestions=suggestions,
        issues=issues,
        processing_time_ms=processing_ms,
    )


@router.post("/generate/{platform}", response_model=GeneratedContent)
async def generate_for_platform(
    platform: str,
    listing: ListingInput,
    current_user: str = Depends(get_current_user),
) -> GeneratedContent:
    """
    Generate optimized listing content for a specific platform.

    Uses AI to create platform-specific titles, descriptions, and tags
    that are ready to copy and paste.
    """

    return await _generate_content_for_platform(platform, listing)


@router.post("/generate/bulk", response_model=List[GeneratedContent])
async def generate_bulk(
    request: BulkGenerateRequest,
    current_user: str = Depends(get_current_user),
) -> List[GeneratedContent]:
    """
    Generate optimized content for multiple platforms at once.

    Perfect for cross-posting - generates all listings in one API call.
    """

    async def _task(platform: str):
        return await _generate_content_for_platform(platform, request.listing)

    tasks = [_task(platform) for platform in request.platforms]
    results: List[GeneratedContent] = []

    for outcome in await asyncio.gather(*tasks, return_exceptions=True):
        if isinstance(outcome, GeneratedContent):
            results.append(outcome)
        elif isinstance(outcome, HTTPException):
            continue
        elif isinstance(outcome, Exception):
            logger.error(f"Bulk generation task failed: {outcome}")
            continue

    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate content for any platform",
        )

    return results


@router.get("/trending")
async def get_trending_recommendations(
    days: int = 14,
    force_refresh: bool = Query(
        False, description="Bypass cache and recompute trending insights"
    ),
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return trending categories, peak posting windows, and growth actions."""

    if force_refresh:
        _TRENDING_CACHE.pop((current_user, days), None)
    insights, issues = await _calculate_trending_insights(current_user, days)
    insights.update(
        {
            "timeframe_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "data_issues": issues,
        }
    )
    return insights


@router.get("/platforms")
async def get_supported_platforms() -> Dict[str, Any]:
    """
    Get list of supported platforms and their requirements.
    """

    platforms = {}
    for key, config in PLATFORM_CONFIGS.items():
        platforms[key] = {
            "name": config.platform,
            "title_max_length": config.title_max_length,
            "description_max_length": config.description_max_length,
            "description_style": config.description_style,
            "emoji_allowed": config.emoji_allowed,
            "html_allowed": config.html_allowed,
            "required_fields": config.required_fields,
        }

    return {"platforms": platforms, "total": len(platforms)}


@router.post("/optimize-price")
async def optimize_price(
    title: str,
    current_price: float,
    category: str | None = None,
    condition: str = "new",
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get AI-powered pricing suggestions based on market data.
    """

    if not openai.api_key:
        return {
            "suggested_price": current_price,
            "confidence": "low",
            "reason": "AI not configured",
        }

    prompt = f"""Analyze this product and suggest optimal pricing:

Product: {title}
Category: {category or "General"}
Condition: {condition}
Current Price: ${current_price:.2f}

Provide:
1. Suggested price (be realistic)
2. Price range (min-max)
3. Reasoning

Format as JSON."""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.5,
        )

        # Parse AI response (simplified - would need better parsing)
        suggestion_text = response.choices[0].message.content

        return {
            "current_price": current_price,
            "suggestion": suggestion_text,
            "confidence": "medium",
        }

    except Exception as e:
        logger.error(f"Price optimization failed: {e}")
        return {
            "suggested_price": current_price,
            "confidence": "low",
            "error": str(e),
        }
