#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en el sistema Sentrix
"""

import requests
import json

def create_test_user():
    """Create a test user for the dashboard"""
    url = "http://localhost:8000/api/v1/auth/register"

    user_data = {
        "email": "test@sentrix.com",
        "password": "testpassword123",
        "display_name": "Usuario Test"
    }

    try:
        response = requests.post(url, json=user_data, timeout=10)

        if response.status_code == 201:
            data = response.json()
            print("Usuario creado exitosamente!")
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            return True
        else:
            print(f"Error creating user: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test login with the created user"""
    url = "http://localhost:8000/api/v1/auth/login"

    login_data = {
        "email": "test@sentrix.com",
        "password": "testpassword123"
    }

    try:
        response = requests.post(url, json=login_data, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("\nLogin exitoso!")
            print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
            return data.get('access_token')
        else:
            print(f"\nError en login: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"\nError en login: {e}")
        return None

def test_dashboard_api(token):
    """Test dashboard API with token"""
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    endpoints = [
        "/api/v1/reports/statistics",
        "/api/v1/reports/risk-distribution",
        "/api/v1/reports/monthly-analyses",
        "/api/v1/reports/recent-activity"
    ]

    print("\nTesting dashboard endpoints:")

    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    print("Creating test user and testing dashboard APIs...")

    # Try to create user (might already exist)
    create_test_user()

    # Test login
    token = test_login()

    # Test dashboard APIs
    test_dashboard_api(token)

    print("\nYou can now use these credentials to test the frontend:")
    print("Email: test@sentrix.com")
    print("Password: testpassword123")