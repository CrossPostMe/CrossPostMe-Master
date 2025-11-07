"""
Run Supabase Schema - Execute SQL directly from Python
This will create all tables, indexes, views, and policies
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'backend'))

from supabase_db import get_supabase

def run_schema():
    """Execute the Supabase schema SQL"""
    print("🚀 CROSSPOSTME - SUPABASE SCHEMA SETUP")
    print("=" * 60)

    # Get Supabase client
    print("\n📡 Connecting to Supabase...")
    client = get_supabase()

    if not client:
        print("❌ Failed to connect to Supabase")
        print("   Check your SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return False

    print("✅ Connected to Supabase")

    # Read SQL file
    sql_file = Path(__file__).parent / "supabase_schema.sql"

    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False

    print(f"\n📄 Reading SQL file: {sql_file}")
    with open(sql_file, 'r') as f:
        sql_content = f.read()

    print(f"   SQL file size: {len(sql_content)} characters")
    print(f"   SQL file lines: {len(sql_content.splitlines())} lines")

    # Split SQL into individual statements
    print("\n⚙️  Parsing SQL statements...")
    statements = []
    current_statement = []
    in_function = False

    for line in sql_content.splitlines():
        stripped = line.strip()

        # Track if we're inside a function definition
        if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
            in_function = True

        # Skip comments and empty lines
        if not stripped or stripped.startswith('--'):
            continue

        current_statement.append(line)

        # End of statement
        if in_function:
            # Functions end with $$ language
            if '$$' in line and 'language' in line.lower():
                statements.append('\n'.join(current_statement))
                current_statement = []
                in_function = False
        else:
            # Regular statements end with semicolon
            if stripped.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []

    print(f"   Found {len(statements)} SQL statements")

    # Execute each statement
    print("\n🔨 Executing SQL statements...")
    print("-" * 60)

    success_count = 0
    error_count = 0

    for i, statement in enumerate(statements, 1):
        # Get statement type for display
        first_words = statement.strip().split()[:3]
        stmt_type = ' '.join(first_words) if first_words else 'SQL'

        try:
            # Execute via Supabase's RPC (raw SQL)
            # Note: Supabase Python client doesn't have direct SQL execution
            # We'll need to use the REST API directly

            print(f"   [{i}/{len(statements)}] {stmt_type[:50]}...", end=' ')

            # For now, skip and show what would be executed
            print("📝 (Manual execution required)")

        except Exception as e:
            error_count += 1
            print(f"❌")
            print(f"      Error: {e}")

    print("-" * 60)

    print("\n" + "=" * 60)
    print("⚠️  MANUAL EXECUTION REQUIRED")
    print("=" * 60)
    print("\nThe Supabase Python client doesn't support direct SQL execution.")
    print("You need to run the SQL manually in the Supabase dashboard.\n")

    print("📋 Steps:")
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project: toehrbdycbtgfhmrloee")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy the contents of: supabase_schema.sql")
    print("6. Paste into the SQL Editor")
    print("7. Click 'Run' (▶️ button)")
    print("8. Wait for 'Success. No rows returned'")
    print("\n✅ Then run: python3 test_supabase.py")

    print("\n" + "=" * 60)

    return False

if __name__ == "__main__":
    run_schema()
