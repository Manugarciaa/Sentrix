#!/usr/bin/env python3

import requests
import json

def test_services():
    print("Sentrix Integration Test Suite")
    print("="*50)

    # Test backend
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("Backend: OK - " + data.get('message', 'Running'))
        else:
            print(f"Backend: ERROR - HTTP {response.status_code}")
    except Exception as e:
        print(f"Backend: ERROR - {e}")

    # Test YOLO service
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("YOLO Service: OK - " + data.get('status', 'Running'))
        else:
            print(f"YOLO Service: ERROR - HTTP {response.status_code}")
    except Exception as e:
        print(f"YOLO Service: ERROR - {e}")

    # Test frontend
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200 and "Sentrix" in response.text:
            print("Frontend: OK - Serving Sentrix app")
        else:
            print(f"Frontend: ERROR - HTTP {response.status_code}")
    except Exception as e:
        print(f"Frontend: ERROR - {e}")

    print("\nAll services tested!")
    print("Frontend: http://localhost:3000")
    print("Backend Docs: http://localhost:8000/docs")
    print("YOLO Docs: http://localhost:8001/docs")

if __name__ == "__main__":
    test_services()