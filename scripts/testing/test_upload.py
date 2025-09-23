#!/usr/bin/env python3
"""
Test script to verify image upload functionality
"""

import requests
import io
from PIL import Image

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def get_auth_token():
    """Get auth token for testing"""
    url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "test@sentrix.com",
        "password": "testpassword123"
    }

    try:
        response = requests.post(url, json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"Login failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_upload_image(token):
    """Test image upload"""
    if not token:
        print("No token available")
        return False

    url = "http://localhost:8000/api/v1/analyses"
    headers = {"Authorization": f"Bearer {token}"}

    # Create test image
    test_image = create_test_image()

    files = {
        'file': ('test_image.jpg', test_image, 'image/jpeg')
    }

    data = {
        'confidence_threshold': 0.5,
        'include_gps': True
    }

    try:
        print("Uploading test image...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201]:
            print("Upload successful!")
            return True
        else:
            print("Upload failed!")
            return False

    except Exception as e:
        print(f"Upload error: {e}")
        return False

if __name__ == "__main__":
    print("Testing image upload functionality...")

    # Get auth token
    token = get_auth_token()

    if token:
        print("Authentication successful")
        success = test_upload_image(token)
        if success:
            print("\nUpload test PASSED!")
        else:
            print("\nUpload test FAILED!")
    else:
        print("Authentication failed")