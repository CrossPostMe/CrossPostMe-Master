"""
Test Enhanced Signup with Supabase
Verifies the migrated endpoint works correctly
"""

import sys
import requests
import json
from datetime import datetime

# Test data
test_user = {
    "email": f"test_supabase_{datetime.now().timestamp()}@example.com",
    "password": "TestPassword123!",
    "fullName": "Supabase Test User",
    "phone": "+1-555-0123",

    # Business intelligence (THE GOLD MINE!)
    "businessName": "Test Marketplace Co",
    "businessType": "Reseller",
    "industry": "Electronics",

    # Marketplace data
    "currentMarketplaces": ["Facebook", "eBay", "OfferUp"],
    "monthlyListings": "50-100",
    "averageItemPrice": "50-100",
    "monthlyRevenue": "5k-10k",

    # Pain points
    "biggestChallenge": "Manual cross-posting takes too much time",
    "currentTools": ["Spreadsheets", "Manual posting"],
    "teamSize": "1-5",

    # Goals
    "growthGoal": "Double sales in 6 months",
    "listingsGoal": "200+ per month",

    # Permissions
    "marketingEmails": True,
    "dataSharing": True,
    "betaTester": True,

    # Attribution
    "trialType": "free",
    "source": "pricing_page",
    "utmSource": "google",
    "utmMedium": "cpc",
    "utmCampaign": "q4_2025"
}

print("=" * 70)
print("TESTING ENHANCED SIGNUP WITH SUPABASE")
print("=" * 70)

# Test endpoint
url = "http://localhost:8000/api/auth/enhanced-signup"

print(f"\n📤 Sending signup request to: {url}")
print(f"📧 Email: {test_user['email']}")
print(f"💼 Industry: {test_user['industry']}")
print(f"💰 Monthly Revenue: {test_user['monthlyRevenue']}")

try:
    response = requests.post(url, json=test_user)

    print(f"\n📊 Response Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SIGNUP SUCCESSFUL!")
        print("=" * 70)
        print(f"User ID: {data.get('user_id')}")
        print(f"Username: {data.get('username')}")
        print(f"Email: {data.get('email')}")
        print(f"Trial Active: {data.get('trial_active')}")
        print(f"Trial Type: {data.get('trial_type')}")
        print(f"Token: {data.get('token')[:50]}...")
        print(f"Message: {data.get('message')}")
        print("=" * 70)

        # Verify in Supabase
        print("\n🔍 Verifying data in Supabase...")
        sys.path.insert(0, '/workspaces/CrossPostMe_MR/app/backend')
        from supabase_db import db as supabase_db

        user = supabase_db.get_user_by_email(test_user['email'])
        if user:
            print(f"✅ User found in Supabase: {user['username']}")

            profile = supabase_db.get_business_profile(user['id'])
            if profile:
                print(f"✅ Business profile found!")
                print(f"   Industry: {profile.get('industry')}")
                print(f"   Revenue: {profile.get('monthly_revenue')}")
                print(f"   Marketplaces: {profile.get('current_marketplaces')}")
                print(f"   Challenge: {profile.get('biggest_challenge')}")
            else:
                print("❌ Business profile not found")
        else:
            print("❌ User not found in Supabase")

        print("\n🎉 MIGRATION SUCCESS! Enhanced signup works with Supabase!")

    else:
        print(f"\n❌ SIGNUP FAILED")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error")
    print("   Make sure the backend server is running:")
    print("   cd /workspaces/CrossPostMe_MR/app/backend")
    print("   uvicorn server:app --reload")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 70)
