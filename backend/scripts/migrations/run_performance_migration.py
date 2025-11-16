#!/usr/bin/env python3
"""
Script to run performance optimization migration (006_add_performance_indexes)
Adds database indexes to improve query performance from 2.8s to <500ms
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.config import get_settings
from src.logging_config import get_logger

logger = get_logger(__name__)

# Try to import psycopg2 for direct PostgreSQL connection
try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def run_migration_with_psycopg2():
    """Execute migration using direct PostgreSQL connection"""
    settings = get_settings()

    # Parse Supabase URL to get connection params
    supabase_url = settings.supabase_url
    supabase_key = settings.supabase_key

    # For direct PostgreSQL connection, we need the database URL
    # Format: postgresql://postgres:[password]@[host]:5432/postgres

    print("[WARNING] Direct PostgreSQL connection required")
    print()
    print("To run this migration, you need:")
    print("  1. Your Supabase database password")
    print("  2. Database host (from Supabase dashboard → Settings → Database)")
    print()

    # Prompt for connection details
    print("Enter your Supabase database details:")
    db_host = input("  Host (e.g., db.xxx.supabase.co): ").strip()
    db_password = input("  Password: ").strip()
    db_name = input("  Database name [postgres]: ").strip() or "postgres"
    db_user = input("  Username [postgres]: ").strip() or "postgres"
    db_port = input("  Port [5432]: ").strip() or "5432"

    print()
    print(f"[INFO] Connecting to {db_host}...")

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("   [OK] Connected successfully")
        print()

        # Read migration file
        migration_file = backend_dir / "src" / "database" / "migrations" / "006_add_performance_indexes.sql"

        print(f"[INFO] Reading migration: {migration_file.name}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print(f"   Lines: {len(migration_sql.splitlines())}")
        print()

        # Execute migration
        print("[INFO] Executing migration...")
        print("   Creating performance indexes...")

        cursor.execute(migration_sql)

        print("   [OK] Migration executed successfully!")
        print()

        # Verify indexes were created
        print("[INFO] Verifying indexes...")
        verify_sql = """
        SELECT
            tablename,
            indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND (indexname LIKE 'idx_analyses_%' OR indexname LIKE 'idx_detections_%')
        ORDER BY tablename, indexname;
        """

        cursor.execute(verify_sql)
        indexes = cursor.fetchall()

        if indexes:
            print(f"   [OK] Found {len(indexes)} performance indexes:")
            for tablename, indexname in indexes:
                print(f"      - {tablename}.{indexname}")
        else:
            print("   [WARNING] No indexes found (might need manual check)")

        cursor.close()
        conn.close()

        print()
        print("=" * 60)
        print("[OK] MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Expected improvements:")
        print("  • Analysis list queries: 2.8s → <500ms (5-6x faster)")
        print("  • Heatmap queries: Significant improvement")
        print("  • User-specific queries: 10x faster")
        print()

        return True

    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        print()
        return False


def run_migration_manual():
    """Provide manual instructions for running the migration"""
    migration_file = backend_dir / "src" / "database" / "migrations" / "006_add_performance_indexes.sql"

    print()
    print("=" * 60)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("=" * 60)
    print()
    print("Since automatic execution is not available, please run the migration manually:")
    print()
    print("Option 1: Using Supabase SQL Editor")
    print("  1. Go to your Supabase dashboard")
    print("  2. Navigate to SQL Editor")
    print("  3. Create a new query")
    print(f"  4. Copy the contents of: {migration_file}")
    print("  5. Paste and execute")
    print()
    print("Option 2: Using psql command")
    print("  1. Install psql if not available")
    print("  2. Get your database connection string from Supabase")
    print(f"  3. Run: psql [connection-string] -f {migration_file}")
    print()
    print("Option 3: Using TablePlus/DBeaver/pgAdmin")
    print("  1. Connect to your Supabase database")
    print(f"  2. Open and execute: {migration_file}")
    print()
    print("=" * 60)
    print()


def run_migration():
    """Execute the performance indexes migration"""
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION MIGRATION")
    print("=" * 60)
    print()

    migration_file = backend_dir / "src" / "database" / "migrations" / "006_add_performance_indexes.sql"

    if not migration_file.exists():
        print(f"[ERROR] Migration file not found: {migration_file}")
        return False

    print("This migration will add performance indexes to improve query speed.")
    print()

    # Check if psycopg2 is available
    if PSYCOPG2_AVAILABLE:
        print("[OK] PostgreSQL driver (psycopg2) is available")
        print()
        choice = input("Do you want to connect directly to PostgreSQL? (y/n): ").strip().lower()

        if choice == 'y':
            return run_migration_with_psycopg2()
    else:
        print("[WARNING] PostgreSQL driver (psycopg2) not installed")
        print("   To install: pip install psycopg2-binary")
        print()

    # Fall back to manual instructions
    run_migration_manual()
    return False


if __name__ == "__main__":
    print()
    success = run_migration()
    sys.exit(0 if success else 1)
