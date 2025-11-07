"""
Credential management for platform automations
Handles secure storage and retrieval of platform credentials
"""

import os
from datetime import datetime, timezone
from typing import List, Optional

from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorClient

from .base import PlatformCredentials


class CredentialManager:
    """Secure credential management for platform automations"""

    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.environ.get(
            "CREDENTIAL_ENCRYPTION_KEY"
        )
        if not self.encryption_key:
            # Generate a new key if none provided (store this securely!)
            self.encryption_key = Fernet.generate_key().decode()

        self.cipher = Fernet(self.encryption_key.encode())

        # Database connection
        mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.environ.get("DB_NAME", "crosspostme")
        client = AsyncIOMotorClient(mongo_url)
        self.db = client[db_name]

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    async def store_credentials(
        self, user_id: str, platform: str, credentials: PlatformCredentials
    ) -> bool:
        """Store encrypted platform credentials"""
        try:
            # Encrypt sensitive data
            encrypted_password = self.encrypt_data(credentials.password)

            credential_doc = {
                "user_id": user_id,
                "platform": platform,
                "username": credentials.username,
                "encrypted_password": encrypted_password,
                "email": credentials.email,
                "phone": credentials.phone,
                "additional_data": credentials.additional_data or {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }

            # Upsert the credentials
            await self.db.secure_credentials.update_one(
                {"user_id": user_id, "platform": platform},
                {"$set": credential_doc},
                upsert=True,
            )

            return True

        except Exception as e:
            print(f"Error storing credentials: {e}")
            return False

    async def get_credentials(
        self, user_id: str, platform: str
    ) -> Optional[PlatformCredentials]:
        """Retrieve and decrypt platform credentials"""
        try:
            credential_doc = await self.db.secure_credentials.find_one(
                {"user_id": user_id, "platform": platform}, {"_id": 0}
            )

            if not credential_doc:
                return None

            # Decrypt password
            decrypted_password = self.decrypt_data(credential_doc["encrypted_password"])

            return PlatformCredentials(
                username=credential_doc["username"],
                password=decrypted_password,
                email=credential_doc.get("email"),
                phone=credential_doc.get("phone"),
                additional_data=credential_doc.get("additional_data", {}),
            )

        except Exception as e:
            print(f"Error retrieving credentials: {e}")
            return None

    async def delete_credentials(self, user_id: str, platform: str) -> bool:
        """Delete stored credentials"""
        try:
            result = await self.db.secure_credentials.delete_one(
                {"user_id": user_id, "platform": platform}
            )
            return result.deleted_count > 0

        except Exception as e:
            print(f"Error deleting credentials: {e}")
            return False

    async def list_user_platforms(self, user_id: str) -> List[str]:
        """List platforms for which user has credentials"""
        try:
            cursor = self.db.secure_credentials.find(
                {"user_id": user_id}, {"platform": 1, "_id": 0}
            )

            platforms = [doc["platform"] async for doc in cursor]
            return platforms

        except Exception as e:
            print(f"Error listing platforms: {e}")
            return []

    async def validate_platform_credentials(self, user_id: str, platform: str) -> bool:
        """Validate stored credentials by testing them"""
        try:
            credentials = await self.get_credentials(user_id, platform)
            if not credentials:
                return False

            # Use automation manager to validate
            from . import automation_manager

            return await automation_manager.platforms[platform].validate_credentials(
                credentials
            )

        except Exception as e:
            print(f"Error validating credentials: {e}")
            return False


# Global credential manager instance
credential_manager = CredentialManager()
