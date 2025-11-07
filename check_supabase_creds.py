"""
Verify Supabase Credentials
Check if credentials are valid and properly configured
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / 'app' / 'backend' / '.env'
load_dotenv(env_path)

print("=" * 70)
print("SUPABASE CREDENTIALS CHECK")
print("=" * 70)

# Get credentials
url = os.getenv('SUPABASE_URL')
anon_key = os.getenv('SUPABASE_ANON_KEY')
service_key = os.getenv('SUPABASE_SERVICE_KEY')

print("\n📋 Environment File:", env_path)
print("   Exists:", env_path.exists())

print("\n🔍 Credentials Found:")
print(f"   SUPABASE_URL: {'✅ Set' if url else '❌ Missing'}")
if url:
    print(f"     Value: {url}")

print(f"\n   SUPABASE_ANON_KEY: {'✅ Set' if anon_key else '❌ Missing'}")
if anon_key:
    print(f"     Length: {len(anon_key)} characters")
    print(f"     Preview: {anon_key[:50]}...")

print(f"\n   SUPABASE_SERVICE_KEY: {'✅ Set' if service_key else '❌ Missing'}")
if service_key:
    print(f"     Length: {len(service_key)} characters")
    print(f"     Preview: {service_key[:50]}...")

# Parse URL to check project ID
if url:
    project_id = url.replace('https://', '').replace('.supabase.co', '')
    print(f"\n🎯 Project ID: {project_id}")
    print(f"   Dashboard: https://supabase.com/dashboard/project/{project_id}")

print("\n" + "=" * 70)

# Test import
try:
    from supabase import create_client
    print("✅ Supabase library imported successfully")

    if url and service_key:
        print("\n🔌 Attempting to create client...")
        try:
            client = create_client(url, service_key)
            print("✅ Client created successfully")

            # Try a simple query
            print("\n📊 Testing database query...")
            try:
                response = client.table("users").select("count", count="exact").execute()
                print(f"✅ Query successful!")
                print(f"   User count: {response.count}")
            except Exception as e:
                print(f"❌ Query failed: {e}")
                print("\n💡 This might mean:")
                print("   1. Tables haven't been created yet (run SQL in dashboard)")
                print("   2. RLS policies are blocking access")
                print("   3. API key doesn't have proper permissions")

        except Exception as e:
            print(f"❌ Client creation failed: {e}")

except ImportError as e:
    print(f"❌ Failed to import supabase: {e}")

print("\n" + "=" * 70)
