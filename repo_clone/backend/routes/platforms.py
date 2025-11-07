import logging
from typing import Any, Dict, List, Optional

from auth import get_optional_current_user
from db import get_typed_db
from fastapi import APIRouter, Depends, HTTPException
from models import PlatformAccount, PlatformAccountCreate
from pydantic import BaseModel

# Import datetime helpers from ads module
from .ads import deserialize_datetime_fields, serialize_datetime_fields

logger = logging.getLogger("platforms")

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


# Request models for credential management
class PlatformCredentialsRequest(BaseModel):
    platform: str
    username: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    additional_data: Optional[Dict[str, str]] = None


class CredentialTestRequest(BaseModel):
    platform: str
    username: str
    password: str
    additional_data: Optional[Dict[str, str]] = None


db = get_typed_db()


# Create Platform Account
@router.post("/accounts", response_model=PlatformAccount)
async def create_platform_account(
    account: PlatformAccountCreate, user_id: str = Depends(get_optional_current_user)
) -> PlatformAccount:
    account_dict = account.model_dump()
    account_dict["user_id"] = user_id  # Add user_id for multi-tenant support
    account_obj = PlatformAccount(**account_dict)

    # Serialize datetime fields for MongoDB storage
    doc = account_obj.model_dump()
    serialize_datetime_fields(doc, ["created_at", "last_used"])

    await db["platform_accounts"].insert_one(doc)
    return account_obj


# Get All Platform Accounts
@router.get("/accounts", response_model=List[PlatformAccount])
async def get_platform_accounts(
    platform: Optional[str] = None, user_id: str = Depends(get_optional_current_user)
) -> List[PlatformAccount]:
    query: dict[str, Any] = {"user_id": user_id}  # Scope by user for security
    if platform:
        query["platform"] = platform

    accounts = await db["platform_accounts"].find(query, {"_id": 0}).to_list(1000)

    # Convert ISO string timestamps back to datetime objects
    for account in accounts:
        deserialize_datetime_fields(account, ["created_at", "last_used"])

    return [PlatformAccount(**acc) for acc in accounts]


# Get Platform Account by ID
@router.get("/accounts/{account_id}", response_model=PlatformAccount)
async def get_platform_account(
    account_id: str, user_id: str = Depends(get_optional_current_user)
) -> PlatformAccount:
    account = await db["platform_accounts"].find_one(
        {"id": account_id, "user_id": user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Convert ISO string timestamps back to datetime objects
    deserialize_datetime_fields(account, ["created_at", "last_used"])

    return PlatformAccount(**account)


# Update Platform Account Status
@router.put("/accounts/{account_id}/status")
async def update_account_status(
    account_id: str, status: str, user_id: str = Depends(get_optional_current_user)
) -> PlatformAccount:
    account = await db["platform_accounts"].find_one(
        {"id": account_id, "user_id": user_id}, {"_id": 0}
    )
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    await db["platform_accounts"].update_one(
        {"id": account_id, "user_id": user_id}, {"$set": {"status": status}}
    )

    updated_account = await db["platform_accounts"].find_one(
        {"id": account_id, "user_id": user_id}, {"_id": 0}
    )

    # Convert ISO string timestamps back to datetime objects
    deserialize_datetime_fields(updated_account, ["created_at", "last_used"])

    return PlatformAccount(**updated_account)


# Delete Platform Account
@router.delete("/accounts/{account_id}")
async def delete_platform_account(
    account_id: str, user_id: str = "default"  # In production, get from JWT token
) -> dict[str, str]:
    result = await db["platform_accounts"].delete_one(
        {"id": account_id, "user_id": user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


# Get Available Platforms
@router.get("/available")
async def get_available_platforms() -> List[dict[str, str]]:
    return [
        {
            "id": "facebook",
            "name": "Facebook Marketplace",
            "icon": "facebook",
            "description": "Post to Facebook Marketplace with 1B+ users",
        },
        {
            "id": "craigslist",
            "name": "Craigslist",
            "icon": "list",
            "description": "Reach local buyers on America's #1 classifieds site",
        },
        {
            "id": "offerup",
            "name": "OfferUp",
            "icon": "shopping-bag",
            "description": "Mobile-first marketplace with 20M+ monthly users",
        },
        {
            "id": "ebay",
            "name": "eBay",
            "icon": "shopping-cart",
            "description": "World's largest online marketplace with global reach",
        },
    ]


# Store Platform Credentials (Secure)
@router.post("/credentials")
async def store_platform_credentials(
    credentials_request: PlatformCredentialsRequest,
    user_id: str = "default",  # In production, get from JWT token
) -> Dict[str, Any]:
    """Store encrypted platform credentials for a user"""
    try:
        from automation.base import PlatformCredentials
        from automation.credentials import credential_manager

        credentials = PlatformCredentials(
            username=credentials_request.username,
            password=credentials_request.password,
            email=credentials_request.email,
            phone=credentials_request.phone,
            additional_data=credentials_request.additional_data,
        )

        success = await credential_manager.store_credentials(
            user_id, credentials_request.platform, credentials
        )

        if success:
            # Also create/update the platform account record
            account_obj = PlatformAccount(
                platform=credentials_request.platform,
                account_name=credentials_request.username,
                account_email=credentials_request.email or credentials_request.username,
                status="active",
                user_id=user_id,  # Add user_id for multi-tenant support
            )

            # Serialize datetime fields for MongoDB storage
            doc = account_obj.model_dump()
            serialize_datetime_fields(doc, ["created_at", "last_used"])

            await db["platform_accounts"].update_one(
                {
                    "platform": credentials_request.platform,
                    "account_email": account_obj.account_email,
                    "user_id": user_id,
                },
                {"$set": doc},
                upsert=True,
            )

            return {
                "success": True,
                "message": f"Credentials stored for {credentials_request.platform}",
                "platform": credentials_request.platform,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store credentials")

    except Exception as e:
        logger.exception("Error storing platform credentials")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Test Platform Credentials
@router.post("/test-credentials")
async def test_platform_credentials(
    test_request: CredentialTestRequest, user_id: str = "default"
) -> Dict[str, Any]:
    """Test platform credentials by attempting authentication"""
    try:
        from automation import automation_manager
        from automation.base import PlatformCredentials

        if test_request.platform not in automation_manager.platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Platform {test_request.platform} not supported",
            )

        credentials = PlatformCredentials(
            username=test_request.username,
            password=test_request.password,
            additional_data=test_request.additional_data,
        )

        platform = automation_manager.platforms[test_request.platform]
        is_valid = await platform.validate_credentials(credentials)

        return {
            "success": is_valid,
            "platform": test_request.platform,
            "message": "Credentials valid" if is_valid else "Credentials invalid",
        }

    except Exception as e:
        return {
            "success": False,
            "platform": test_request.platform,
            "message": f"Error testing credentials: {str(e)}",
        }


# Get User's Platform Status
@router.get("/status/{user_id}")
async def get_user_platform_status(user_id: str = "default") -> Dict[str, Any]:
    """Get the status of all platforms for a user"""
    try:
        from automation.credentials import credential_manager

        platforms = await credential_manager.list_user_platforms(user_id)

        platform_status = []
        for platform in platforms:
            is_valid = await credential_manager.validate_platform_credentials(
                user_id, platform
            )
            platform_status.append(
                {
                    "platform": platform,
                    "has_credentials": True,
                    "credentials_valid": is_valid,
                    "status": "active" if is_valid else "needs_attention",
                }
            )

        return {
            "user_id": user_id,
            "platforms": platform_status,
            "total_platforms": len(platform_status),
            "active_platforms": sum(
                1 for p in platform_status if p["credentials_valid"]
            ),
        }

    except Exception as e:
        logger.exception(f"Error getting platform status for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e)) from e
