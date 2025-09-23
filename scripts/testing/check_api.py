#!/usr/bin/env python3
import requests
import json

def get_token():
    """Get auth token"""
    try:
        response = requests.post('http://localhost:8000/api/v1/auth/login',
                                json={'email': 'test@sentrix.com', 'password': 'testpassword123'})
        if response.status_code == 200:
            return response.json()['access_token']
    except Exception as e:
        print(f"Error getting token: {e}")
    return None

def check_analyses():
    """Check analyses data"""
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Get list of analyses
        response = requests.get("http://localhost:8000/api/v1/analyses?limit=5", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Analysis list response:")
            print(json.dumps(data, indent=2, default=str))

            # Get details of first analysis if available
            if 'analyses' in data and data['analyses']:
                first_id = data['analyses'][0]['id']
                print(f"\nGetting details for analysis: {first_id}")

                detail_response = requests.get(f"http://localhost:8000/api/v1/analyses/{first_id}", headers=headers)
                print(f"Detail status: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("Analysis detail response:")
                    print(json.dumps(detail_data, indent=2, default=str))
                else:
                    print(f"Detail error: {detail_response.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_analyses()