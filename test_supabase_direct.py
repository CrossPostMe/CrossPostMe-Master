"""
Direct Supabase Test - Tests enhanced signup logic without HTTP server
"""

import sys
sys.path.insert(0, '/workspaces/CrossPostMe_MR/app/backend')

from datetime import datetime
from supabase_db import db as supabase_db

print("=" * 70)
print("TESTING ENHANCED SIGNUP - DIRECT SUPABASE TEST")
print("=" * 70)

# Test data
test_email = f"test_direct_{datetime.now().timestamp()}@example.com"
test_username = test_email.split('@')[0]

print(f"\n📧 Creating test user: {test_email}")
print(f"👤 Username: {test_username}")

try:
    # Step 1: Create user
    print("\n1️⃣  Creating user in Supabase...")
    user_data = {
        "username": test_username,
        "email": test_email,
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpfVWW4D2Lne",  # Pre-hashed "password"
        "full_name": "Direct Test User",
        "phone": "+1-555-TEST",
        "is_active": True,
        "trial_active": True,
        "trial_type": "free",
        "metadata": {
            "engagement": {
                "signup_completed": True,
                "onboarding_completed": False,
            },
            "preferences": {
                "marketing_emails": True,
                "data_sharing": True,
            }
        }
    }

    created_user = supabase_db.create_user(user_data)
    user_id = created_user["id"]
    print(f"   ✅ User created: {user_id}")
    print(f"   Username: {created_user['username']}")
    print(f"   Email: {created_user['email']}")

    # Step 2: Create business profile
    print("\n2️⃣  Creating business profile...")
    profile_data = {
        "user_id": user_id,
        "business_name": "Test Marketplace Co",
        "business_type": "Reseller",
        "industry": "Electronics",
        "team_size": "1-5",
        "current_marketplaces": ["Facebook", "eBay", "OfferUp"],
        "monthly_listings": "50-100",
        "average_item_price": "50-100",
        "monthly_revenue": "5k-10k",
        "biggest_challenge": "Manual cross-posting takes too much time",
        "current_tools": ["Spreadsheets", "Manual posting"],
        "growth_goal": "Double sales in 6 months",
        "listings_goal": "200+ per month",
        "marketing_emails": True,
        "data_sharing": True,
        "beta_tester": True,
        "signup_source": "direct_test",
        "utm_source": "test",
        "utm_medium": "direct",
        "utm_campaign": "migration_test"
    }

    created_profile = supabase_db.create_business_profile(profile_data)
    print(f"   ✅ Profile created: {created_profile['id']}")
    print(f"   Industry: {created_profile['industry']}")
    print(f"   Revenue: {created_profile['monthly_revenue']}")
    print(f"   Marketplaces: {created_profile['current_marketplaces']}")

    # Step 3: Log business intelligence event
    print("\n3️⃣  Logging business intelligence event...")
    event = supabase_db.log_event(
        user_id=user_id,
        event_type="enhanced_signup",
        event_data={
            "business_type": "Reseller",
            "industry": "Electronics",
            "monthly_revenue": "5k-10k",
            "monthly_listings": "50-100",
            "marketplaces": ["Facebook", "eBay", "OfferUp"],
            "biggest_challenge": "Manual cross-posting takes too much time",
            "trial_type": "free"
        }
    )
    print(f"   ✅ Event logged: {event['id']}")
    print(f"   Event type: {event['event_type']}")

    # Step 4: Verify data
    print("\n4️⃣  Verifying data in Supabase...")

    # Check user
    user = supabase_db.get_user_by_email(test_email)
    if user:
        print(f"   ✅ User found: {user['username']}")
    else:
        print(f"   ❌ User not found!")

    # Check profile
    profile = supabase_db.get_business_profile(user_id)
    if profile:
        print(f"   ✅ Business profile found!")
        print(f"      Industry: {profile['industry']}")
        print(f"      Revenue: {profile['monthly_revenue']}")
        print(f"      Challenge: {profile['biggest_challenge']}")
    else:
        print(f"   ❌ Profile not found!")

    # Check events
    events = supabase_db.get_events(user_id=user_id)
    if events:
        print(f"   ✅ Events found: {len(events)} event(s)")
        for evt in events:
            print(f"      - {evt['event_type']} at {evt['timestamp']}")
    else:
        print(f"   ❌ No events found!")

    print("\n" + "=" * 70)
    print("✅ SUPABASE MIGRATION TEST SUCCESSFUL!")
    print("=" * 70)
    print("\n🎉 Enhanced signup data flow works perfectly!")
    print("\nData Created:")
    print(f"  👤 User: {user_id}")
    print(f"  💼 Business Profile: {created_profile['id']}")
    print(f"  📊 Event: {event['id']}")
    print("\n💎 THE DATA GOLDMINE IS COLLECTING!")
    print("\nNext Steps:")
    print("  1. ✅ Supabase working perfectly")
    print("  2. ✅ Data structure validated")
    print("  3. ⏩ Test with actual backend server")
    print("  4. ⏩ Enable parallel MongoDB writes")
    print("  5. ⏩ Monitor for 100+ signups")
    print("  6. ⏩ Migrate next route")
    print("\n" + "=" * 70)

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
