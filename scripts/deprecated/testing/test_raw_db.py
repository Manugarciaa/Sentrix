#!/usr/bin/env python3
import requests
import json

def test_raw_analysis():
    """Test the analysis service directly"""

    # Get token
    try:
        response = requests.post('http://localhost:8000/api/v1/auth/login',
                                json={'email': 'test@sentrix.com', 'password': 'testpassword123'})
        if response.status_code != 200:
            print(f"Auth failed: {response.text}")
            return
        token = response.json()['access_token']
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Test the backend service call directly (no API endpoint cache)
    print("=== TESTING BACKEND SERVICE DIRECTLY ===")

    # First, let's see what's in the list that shows GPS data
    try:
        response = requests.get("http://localhost:8000/api/v1/analyses?limit=5", headers=headers)
        if response.status_code == 200:
            list_data = response.json()
            print("=== LIST ANALYSES (this one shows GPS) ===")
            for analysis in list_data.get('analyses', []):
                if analysis['id'] == "1f3b29f0-12ed-4ef5-8f19-c3183cac7886":
                    print("Found GPS analysis in LIST:")
                    print(f"  has_location: {analysis['location']['has_location']}")
                    print(f"  latitude: {analysis['location']['latitude']}")
                    print(f"  longitude: {analysis['location']['longitude']}")
                    print(f"  google_maps_url: {analysis['location']['google_maps_url']}")
                    break
        else:
            print(f"List error: {response.text}")
    except Exception as e:
        print(f"List error: {e}")

    # Now test the detail endpoint
    analysis_id = "1f3b29f0-12ed-4ef5-8f19-c3183cac7886"
    try:
        print(f"\n=== TESTING DETAIL ENDPOINT ===")
        response = requests.get(f"http://localhost:8000/api/v1/analyses/{analysis_id}", headers=headers)
        if response.status_code == 200:
            detail_data = response.json()
            print("Detail response location:")
            print(f"  has_location: {detail_data['location']['has_location']}")
            print(f"  latitude: {detail_data['location']['latitude']}")
            print(f"  longitude: {detail_data['location']['longitude']}")
            print(f"  google_maps_url: {detail_data['location']['google_maps_url']}")
        else:
            print(f"Detail error: {response.text}")
    except Exception as e:
        print(f"Detail error: {e}")

if __name__ == "__main__":
    test_raw_analysis()