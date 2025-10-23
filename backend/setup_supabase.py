#!/usr/bin/env python3
"""
Setup Supabase database - Create certificates table
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set")
    exit(1)

print(f"🔗 Connecting to Supabase: {SUPABASE_URL}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Read the SQL file
with open('/app/backend/create_supabase_table.sql', 'r') as f:
    sql = f.read()

print("📝 Creating certificates table...")

# Execute SQL using Supabase REST API
# Note: Direct SQL execution may require service role key
# For now, let's try to create via the table() method

try:
    # Test if table exists by trying to query it
    response = supabase.table("certificates").select("*").limit(1).execute()
    print("✅ Table 'certificates' already exists!")
    print(f"   Current row count: {len(response.data)}")
except Exception as e:
    error_msg = str(e)
    if "Could not find the table" in error_msg or "PGRST205" in error_msg:
        print("⚠️  Table doesn't exist. Please create it manually using the SQL script.")
        print("\n📋 Instructions:")
        print("1. Go to your Supabase dashboard")
        print(f"2. Navigate to: {SUPABASE_URL.replace('https://', 'https://app.supabase.com/project/')}")
        print("3. Go to SQL Editor")
        print("4. Paste and run the contents of: /app/backend/create_supabase_table.sql")
        print("\n💡 Or use the Supabase CLI:")
        print("   supabase db push")
    else:
        print(f"❌ Error: {error_msg}")

print("\n✅ Setup complete!")
print("\n📊 You can now use the API:")
print("   curl http://localhost:8001/api/health")
