"""
Direct PostgreSQL Schema Setup using psycopg2
Connects directly to Supabase PostgreSQL and runs the schema
"""

import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / 'app' / 'backend' / '.env')

def get_postgres_connection_string():
    """Build PostgreSQL connection string from Supabase URL"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')

    if not supabase_url:
        return None

    # Extract project ref from URL: https://xxxxx.supabase.co
    project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

    # Supabase PostgreSQL connection format
    # postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

    # Note: We need the database password, not the API key
    # This is different from SUPABASE_SERVICE_KEY

    return None  # Will need database password

def run_schema_direct():
    """Run schema using direct PostgreSQL connection"""
    print("🚀 CROSSPOSTME - SUPABASE SCHEMA SETUP (DIRECT)")
    print("=" * 70)

    if not HAS_PSYCOPG2:
        print("\n❌ psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        print("\n💡 Alternative: Use Supabase Dashboard SQL Editor")
        return False

    # Get connection string
    conn_string = get_postgres_connection_string()

    if not conn_string:
        print("\n⚠️  Direct PostgreSQL connection requires database password")
        print("   API keys (SUPABASE_SERVICE_KEY) won't work for direct connection")
        print("\n📋 EASIEST METHOD: Use Supabase Dashboard")
        print("-" * 70)
        print("\n✅ Steps to run the schema:")
        print("   1. Open: https://supabase.com/dashboard/project/toehrbdycbtgfhmrloee")
        print("   2. Click: 'SQL Editor' (left sidebar)")
        print("   3. Click: 'New Query'")
        print("   4. Copy contents of: supabase_schema.sql")
        print("   5. Paste into SQL Editor")
        print("   6. Click: 'Run' ▶️")
        print("   7. Wait for: 'Success. No rows returned'")
        print("\n   Then test: python3 app/backend/test_supabase.py")
        print("\n" + "=" * 70)
        return False

if __name__ == "__main__":
    run_schema_direct()
