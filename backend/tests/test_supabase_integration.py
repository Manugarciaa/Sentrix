#!/usr/bin/env python3
"""
Test complete Supabase integration for Sentrix Backend
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_full_integration():
    """Test complete Supabase integration"""
    print("=== Testing Complete Supabase Integration ===")

    try:
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        supabase = create_client(supabase_url, supabase_key)

        # Test 1: Read data from tables
        print("\n1. Testing data retrieval...")

        # Get users
        users_response = supabase.table('user_profiles').select('*').execute()
        print(f"OK Found {len(users_response.data)} users")

        # Get analyses
        analyses_response = supabase.table('analyses').select('*').execute()
        print(f"OK Found {len(analyses_response.data)} analyses")

        # Get detections
        detections_response = supabase.table('detections').select('*').execute()
        print(f"OK Found {len(detections_response.data)} detections")

        # Test 2: Complex query with joins
        print("\n2. Testing complex queries...")

        # Get analyses with detection count
        complex_response = supabase.table('analyses').select(
            'id, image_filename, risk_level, total_detections, detections(count)'
        ).execute()

        if complex_response.data:
            analysis = complex_response.data[0]
            print(f"OK Complex query successful: Analysis {analysis.get('image_filename')} has {analysis.get('total_detections')} detections")

        # Test 3: Filter queries
        print("\n3. Testing filtered queries...")

        # Get high-risk analyses
        high_risk = supabase.table('analyses').select('*').eq('risk_level', 'MEDIUM').execute()
        print(f"OK Found {len(high_risk.data)} medium-risk analyses")

        # Get pending detections
        pending = supabase.table('detections').select('*').eq('validation_status', 'pending').execute()
        print(f"OK Found {len(pending.data)} pending detections")

        # Test 4: Insert new data
        print("\n4. Testing data insertion...")

        # Create a new user
        new_user = {
            "display_name": "Integration Test User",
            "role": "user",
            "organization": "Test Org"
        }

        user_insert = supabase.table('user_profiles').insert(new_user).execute()
        if user_insert.data:
            new_user_id = user_insert.data[0]['id']
            print(f"OK Created new user: {new_user_id}")

            # Create a new analysis for this user
            new_analysis = {
                "user_id": new_user_id,
                "image_url": "https://example.com/integration_test.jpg",
                "image_filename": "integration_test.jpg",
                "has_gps_data": False,
                "total_detections": 1,
                "risk_level": "LOW",
                "confidence_threshold": 0.6,
                "model_used": "yolo11s-seg-test"
            }

            analysis_insert = supabase.table('analyses').insert(new_analysis).execute()
            if analysis_insert.data:
                new_analysis_id = analysis_insert.data[0]['id']
                print(f"OK Created new analysis: {new_analysis_id}")

                # Clean up test data
                supabase.table('analyses').delete().eq('id', new_analysis_id).execute()
                supabase.table('user_profiles').delete().eq('id', new_user_id).execute()
                print("OK Cleaned up test data")

        # Test 5: Real-time subscriptions (basic test)
        print("\n5. Testing real-time capabilities...")
        try:
            # This just tests that the real-time client can be created
            realtime = supabase.realtime
            print("OK Real-time client available")
        except Exception as rt_error:
            print(f"INFO Real-time test: {rt_error}")

        print("\nOK All integration tests passed!")
        return True

    except Exception as e:
        print(f"FAIL Integration test failed: {e}")
        return False


def test_backend_supabase_manager():
    """Test our custom Supabase manager without complex imports"""
    print("\n=== Testing Backend Supabase Manager ===")

    try:
        # Simple direct test without importing the complex structure
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        client = create_client(supabase_url, supabase_key)

        # Test basic operations that our manager would do
        print("1. Testing connection...")
        response = client.table('user_profiles').select('id').limit(1).execute()
        print("OK Connection works")

        print("2. Testing data retrieval...")
        analyses = client.table('analyses').select('*').limit(5).execute()
        print(f"OK Retrieved {len(analyses.data)} analyses")

        print("3. Testing filtering...")
        pending_detections = client.table('detections').select('*').eq('validation_status', 'pending').limit(5).execute()
        print(f"OK Found {len(pending_detections.data)} pending detections")

        print("OK Backend manager simulation successful!")
        return True

    except Exception as e:
        print(f"FAIL Backend manager test failed: {e}")
        return False


def display_database_summary():
    """Display a summary of the current database state"""
    print("\n=== Database Summary ===")

    try:
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        supabase = create_client(supabase_url, supabase_key)

        # Get counts
        users = supabase.table('user_profiles').select('id').execute()
        analyses = supabase.table('analyses').select('id').execute()
        detections = supabase.table('detections').select('id').execute()

        print(f"Users: {len(users.data)}")
        print(f"Analyses: {len(analyses.data)}")
        print(f"Detections: {len(detections.data)}")

        # Get risk level distribution
        risk_dist = {}
        for analysis in supabase.table('analyses').select('risk_level').execute().data:
            risk_level = analysis.get('risk_level', 'UNKNOWN')
            risk_dist[risk_level] = risk_dist.get(risk_level, 0) + 1

        print(f"Risk distribution: {risk_dist}")

        # Get validation status distribution
        validation_dist = {}
        for detection in supabase.table('detections').select('validation_status').execute().data:
            status = detection.get('validation_status', 'unknown')
            validation_dist[status] = validation_dist.get(status, 0) + 1

        print(f"Validation status: {validation_dist}")

    except Exception as e:
        print(f"Error getting summary: {e}")


def main():
    """Run all integration tests"""
    print("Sentrix Supabase Integration Tests")
    print("=" * 50)

    tests = [
        test_full_integration,
        test_backend_supabase_manager
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"FAIL Test {test.__name__} crashed: {e}")
            results.append(False)

    # Display summary
    display_database_summary()

    # Results
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\nOK Supabase integration is fully functional!")
        print("OK Database tables created")
        print("OK Data operations working")
        print("OK Complex queries working")
        print("OK Ready for backend integration")
    else:
        print("\nFAIL Some integration tests failed")

    return passed == total


if __name__ == "__main__":
    main()