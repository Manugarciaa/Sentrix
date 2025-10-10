"""
Fix user roles in database - Update lowercase 'user' to uppercase 'USER'
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from backend directory
backend_dir = os.path.dirname(__file__)
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, os.path.join(backend_dir, 'src'))

from sqlalchemy import create_engine, text
from src.database.connection import get_database_url

def fix_roles():
    """Fix user roles from lowercase to uppercase"""
    try:
        # Get database connection
        database_url = get_database_url()
        print(f"[INFO] Connecting to database...")

        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Check current roles
            result = conn.execute(text("""
                SELECT id, email, role FROM user_profiles
            """))

            users = result.fetchall()
            print(f"\n[INFO] Found {len(users)} users in database")

            for user in users:
                print(f"  - {user[1]}: role = '{user[2]}'")

            # Update lowercase roles to uppercase
            print(f"\n[INFO] Updating roles to uppercase...")
            result = conn.execute(text("""
                UPDATE user_profiles
                SET role = 'USER'
                WHERE role = 'user'
            """))
            conn.commit()

            print(f"[SUCCESS] Updated {result.rowcount} user(s) with role 'user' to 'USER'")

            # Verify
            result = conn.execute(text("""
                SELECT id, email, role FROM user_profiles
            """))

            users = result.fetchall()
            print(f"\n[INFO] Updated user roles:")
            for user in users:
                print(f"  - {user[1]}: role = '{user[2]}'")

            return True

    except Exception as e:
        print(f"[ERROR] Failed to fix roles: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*60)
    print("Fix User Roles in Database")
    print("="*60)
    print()

    success = fix_roles()

    if success:
        print("\n[SUCCESS] Database roles fixed successfully!")
    else:
        print("\n[ERROR] Failed to fix database roles")

    sys.exit(0 if success else 1)
