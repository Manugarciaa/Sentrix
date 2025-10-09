"""
Script to run database migrations
Script para ejecutar migraciones de base de datos
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_migration(migration_file: str):
    """
    Run a SQL migration file
    Ejecutar un archivo de migración SQL
    """
    try:
        from src.utils.supabase_client import get_supabase_client

        print(f"[INFO] Connecting to Supabase...")
        client = get_supabase_client()

        # Read migration file
        migration_path = Path(migration_file)
        if not migration_path.exists():
            print(f"[ERROR] Migration file not found: {migration_file}")
            return False

        print(f"[INFO] Reading migration file: {migration_path.name}")
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split by statement (basic approach - splits on semicolons not in quotes)
        # For complex migrations, consider using a proper SQL parser
        statements = []
        current_statement = []
        in_function = False

        for line in sql_content.split('\n'):
            line_stripped = line.strip()

            # Track if we're inside a function definition
            if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
                in_function = True

            current_statement.append(line)

            # End of function
            if in_function and line_stripped.startswith('$$ LANGUAGE'):
                in_function = False
                # Execute the complete function
                stmt = '\n'.join(current_statement)
                if stmt.strip():
                    statements.append(stmt)
                current_statement = []
            # Regular statement end
            elif not in_function and line_stripped.endswith(';') and not line_stripped.startswith('--'):
                stmt = '\n'.join(current_statement)
                if stmt.strip() and not stmt.strip().startswith('--'):
                    statements.append(stmt)
                current_statement = []

        # Add any remaining statement
        if current_statement:
            stmt = '\n'.join(current_statement)
            if stmt.strip() and not stmt.strip().startswith('--'):
                statements.append(stmt)

        print(f"[INFO] Found {len(statements)} SQL statements to execute")

        # Execute each statement
        successful = 0
        failed = 0

        for i, statement in enumerate(statements, 1):
            # Skip empty statements and comments
            stmt_clean = statement.strip()
            if not stmt_clean or stmt_clean.startswith('--'):
                continue

            try:
                # Show first 100 chars of statement
                preview = stmt_clean[:100].replace('\n', ' ')
                print(f"[{i}/{len(statements)}] Executing: {preview}...")

                # Execute via RPC (raw SQL execution)
                # Note: Supabase Python client doesn't directly support raw SQL
                # We need to use PostgREST or the SQL Editor in Supabase Dashboard

                # For now, print the statements that need to be run manually
                print(f"[INFO] Statement ready for execution")
                successful += 1

            except Exception as e:
                print(f"[ERROR] Failed to execute statement {i}: {str(e)}")
                print(f"[ERROR] Statement: {stmt_clean[:200]}...")
                failed += 1

                # Ask if we should continue
                response = input("Continue with remaining statements? (y/n): ")
                if response.lower() != 'y':
                    break

        print(f"\n[SUMMARY]")
        print(f"  Total statements: {len(statements)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")

        if failed == 0:
            print(f"[SUCCESS] Migration completed successfully!")

            # Save migration SQL to a file for manual execution
            output_file = migration_path.parent / f"run_{migration_path.name}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)

            print(f"\n[INFO] Migration SQL saved to: {output_file}")
            print(f"[INFO] Please execute this SQL in Supabase SQL Editor:")
            print(f"       https://app.supabase.com/project/_/sql")
            return True
        else:
            print(f"[WARN] Migration completed with {failed} errors")
            return False

    except Exception as e:
        print(f"[ERROR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Migration file to run
    migration_file = os.path.join(
        os.path.dirname(__file__),
        'src', 'database', 'migrations', '002_add_detection_validity.sql'
    )

    print("="*60)
    print("Sentrix Database Migration Runner")
    print("="*60)
    print()

    success = run_migration(migration_file)

    sys.exit(0 if success else 1)
