#!/usr/bin/env python3
"""
Script to run database migrations for Sentrix backend.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to run migrations."""
    print("🚀 Starting Sentrix Database Migration")

    # Check if alembic.ini exists
    if not Path("alembic.ini").exists():
        print("❌ alembic.ini not found. Make sure you're in the backend directory.")
        sys.exit(1)

    # Check current migration status
    print("\n📋 Checking current migration status...")
    run_command("alembic current", "Check current revision")

    # Show migration history
    print("\n📚 Showing migration history...")
    run_command("alembic history --verbose", "Show migration history")

    # Run migrations
    if run_command("alembic upgrade head", "Run migrations"):
        print("\n🎉 All migrations completed successfully!")
        print("\n📊 Database schema is now up to date with:")
        print("  - PostGIS extension enabled")
        print("  - user_profiles table")
        print("  - analyses table with GPS support")
        print("  - detections table with geospatial data")
        print("  - All necessary indexes and triggers")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()