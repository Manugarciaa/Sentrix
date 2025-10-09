#!/usr/bin/env python3
"""
Test Supabase connection and basic functionality
"""

import os
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_environment_variables():
    """Test if Supabase environment variables are set"""
    print("=== Testing Environment Variables ===")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'DATABASE_URL'
        ]

        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                # Only show first few characters for security
                display_value = value[:20] + "..." if len(value) > 20 else value
                print(f"OK {var}: {display_value}")

        if missing_vars:
            print(f"FAIL Missing environment variables: {missing_vars}")
            return False

        print("OK All required environment variables are set")
        return True

    except Exception as e:
        print(f"FAIL Error checking environment variables: {e}")
        return False


def test_supabase_import():
    """Test if Supabase can be imported"""
    print("\n=== Testing Supabase Import ===")

    try:
        from supabase import create_client, Client
        print("OK Supabase library imported successfully")
        return True
    except ImportError as e:
        print(f"FAIL Could not import Supabase: {e}")
        print("Run: pip install supabase")
        return False
    except Exception as e:
        print(f"FAIL Unexpected error importing Supabase: {e}")
        return False


def test_supabase_client_creation():
    """Test creating Supabase client"""
    print("\n=== Testing Supabase Client Creation ===")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            print("FAIL Supabase URL or Key not found in environment")
            return False

        # Create client
        supabase = create_client(supabase_url, supabase_key)
        print("OK Supabase client created successfully")

        return True

    except Exception as e:
        print(f"FAIL Error creating Supabase client: {e}")
        traceback.print_exc()
        return False


def test_supabase_manager():
    """Test our custom Supabase manager"""
    print("\n=== Testing Supabase Manager ===")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        from ..utils.supabase_client import get_supabase_manager

        manager = get_supabase_manager()
        print("OK Supabase manager created")

        # Test connection
        connection_result = manager.test_connection()
        print(f"Connection test result: {connection_result['status']}")

        if connection_result['status'] == 'connected':
            print("OK Supabase connection successful")
            return True
        else:
            print(f"FAIL Supabase connection failed: {connection_result['message']}")
            return False

    except Exception as e:
        print(f"FAIL Error testing Supabase manager: {e}")
        traceback.print_exc()
        return False


def test_database_connection():
    """Test PostgreSQL database connection"""
    print("\n=== Testing Database Connection ===")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        import psycopg2
        from urllib.parse import urlparse

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("FAIL DATABASE_URL not found in environment")
            return False

        # Parse database URL
        parsed = urlparse(database_url)

        # Test connection
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        print(f"OK Database connection successful")
        print(f"PostgreSQL version: {version[0][:50]}...")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"FAIL Database connection failed: {e}")
        return False


def run_all_tests():
    """Run all Supabase connection tests"""
    print("Starting Supabase Connection Tests...")
    print("=" * 50)

    tests = [
        test_environment_variables,
        test_supabase_import,
        test_supabase_client_creation,
        test_database_connection,
        test_supabase_manager
    ]

    results = {}
    for test in tests:
        test_name = test.__name__
        try:
            result = test()
            results[test_name] = result
        except Exception as e:
            print(f"FAIL {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{test_name:30} {status}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("OK All tests passed! Supabase integration is ready.")
    else:
        print("FAIL Some tests failed. Check configuration and dependencies.")

    return passed == total


if __name__ == "__main__":
    run_all_tests()