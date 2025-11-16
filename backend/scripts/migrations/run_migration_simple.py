#!/usr/bin/env python3
"""
Simple script to run performance optimization migration
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

import psycopg2

def run_migration():
    """Execute the performance indexes migration"""
    print("=" * 60)
    print("PERFORMANCE OPTIMIZATION MIGRATION")
    print("=" * 60)
    print()

    migration_file = backend_dir / "src" / "database" / "migrations" / "006_add_performance_indexes.sql"

    if not migration_file.exists():
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    print("This migration will add performance indexes to improve query speed.")
    print()

    # Prompt for connection details
    print("Enter your Supabase database details:")
    db_host = input("  Host (e.g., db.xxx.supabase.co): ").strip()
    db_password = input("  Password: ").strip()
    db_name = input("  Database name [postgres]: ").strip() or "postgres"
    db_user = input("  Username [postgres]: ").strip() or "postgres"
    db_port = input("  Port [5432]: ").strip() or "5432"

    print()
    print(f"Connecting to {db_host}...")

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

        print("Connected successfully")
        print()

        # Read migration file
        print(f"Reading migration: {migration_file.name}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print(f"Lines: {len(migration_sql.splitlines())}")
        print()

        # Execute migration
        print("Executing migration...")
        print("Creating performance indexes...")

        cursor.execute(migration_sql)

        print("Migration executed successfully!")
        print()

        # Verify indexes were created
        print("Verifying indexes...")
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
            print(f"Found {len(indexes)} performance indexes:")
            for tablename, indexname in indexes:
                print(f"  - {tablename}.{indexname}")
        else:
            print("WARNING: No indexes found (might need manual check)")

        cursor.close()
        conn.close()

        print()
        print("=" * 60)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Expected improvements:")
        print("  - Analysis list queries: 2.8s -> <500ms (5-6x faster)")
        print("  - Heatmap queries: Significant improvement")
        print("  - User-specific queries: 10x faster")
        print()

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        print()
        return False


if __name__ == "__main__":
    print()
    success = run_migration()
    sys.exit(0 if success else 1)
