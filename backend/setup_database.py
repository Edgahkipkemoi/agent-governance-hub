#!/usr/bin/env python3
"""
Database Setup Script

This script creates the logs table in Supabase using the service role key.
Run this once to set up your database.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Create the logs table in Supabase."""
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
        return False
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Read migration SQL
        with open('migrations/001_create_logs_table.sql', 'r') as f:
            sql = f.read()
        
        print("📝 Creating logs table...")
        
        # Execute the SQL using Supabase's RPC or direct SQL execution
        # Note: Supabase Python client doesn't have direct SQL execution
        # We'll use the REST API to execute SQL
        
        print("\n⚠️  Manual Step Required:")
        print("=" * 60)
        print("The Supabase Python client doesn't support direct SQL execution.")
        print("Please follow these steps:")
        print()
        print("1. Go to: https://supabase.com/dashboard/project/_/sql/new")
        print(f"2. Select your project: {supabase_url.split('//')[1].split('.')[0]}")
        print("3. Copy and paste this SQL:")
        print()
        print("-" * 60)
        print(sql)
        print("-" * 60)
        print()
        print("4. Click 'Run' to execute the SQL")
        print("5. Enable replication: Database → Replication → Enable for 'logs' table")
        print("=" * 60)
        
        # Test connection by trying to query (will fail if table doesn't exist yet)
        try:
            result = supabase.table('logs').select('*').limit(1).execute()
            print("\n✅ Success! The 'logs' table already exists and is accessible.")
            return True
        except Exception as e:
            if "does not exist" in str(e) or "not found" in str(e):
                print("\n⏳ Waiting for you to create the table using the SQL above...")
                return False
            else:
                print(f"\n❌ Error checking table: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Agent Audit System - Database Setup")
    print()
    setup_database()
