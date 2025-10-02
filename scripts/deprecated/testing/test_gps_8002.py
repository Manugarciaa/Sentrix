#!/usr/bin/env python3
import requests
import json

def test_gps_analysis_8002():
    """Test the specific GPS analysis on port 8002"""

    # Get token
    try:
        response = requests.post('http://localhost:8002/api/v1/auth/login',
                                json={'email': 'test@sentrix.com', 'password': 'testpassword123'})
        if response.status_code != 200:
            print(f"Auth failed: {response.text}")
            return
        token = response.json()['access_token']
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Test the specific analysis that should have GPS
    analysis_id = "1f3b29f0-12ed-4ef5-8f19-c3183cac7886"

    try:
        print(f"Testing analysis: {analysis_id} on port 8002")
        response = requests.get(f"http://localhost:8002/api/v1/analyses/{analysis_id}", headers=headers)

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Full response:")
            print(json.dumps(data, indent=2, default=str))

            print("\n=== LOCATION DATA ===")
            location = data.get('location', {})
            print(f"Has location: {location.get('has_location')}")
            print(f"Latitude: {location.get('latitude')}")
            print(f"Longitude: {location.get('longitude')}")
            print(f"Coordinates: {location.get('coordinates')}")
            print(f"Google Maps URL: {location.get('google_maps_url')}")

        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gps_analysis_8002()