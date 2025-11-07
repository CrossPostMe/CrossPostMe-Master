"""
Cleanup test data from LeadService tests
"""

import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def cleanup():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.crosspostme

    try:
        # Delete test leads
        result = await db.leads.delete_many({"user_id": "user_test"})
        print(f"✅ Deleted {result.deleted_count} test leads")

        # Verify deletion
        remaining = await db.leads.count_documents({"user_id": "user_test"})
        print(f"✅ Remaining test leads: {remaining}")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        client.close()
        print("👋 Cleanup complete")


if __name__ == "__main__":
    asyncio.run(cleanup())
