#!/usr/bin/env python3
"""
Script de prueba de integración para verificar que todos los servicios funcionen correctamente
"""

import requests
import json
import time
from pathlib import Path

def test_service_health(service_name, url):
    """Test if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name}: HEALTHY")
            return True
        else:
            print(f"❌ {service_name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: CONNECTION ERROR - {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    print("\n🧪 Testing Backend API...")

    # Test root endpoint
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Root: {data.get('message', 'OK')}")
        else:
            print(f"❌ Backend Root: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Backend Root: {e}")

def test_yolo_service():
    """Test YOLO service endpoints"""
    print("\n🧪 Testing YOLO Service...")

    # Test models endpoint
    try:
        response = requests.get("http://localhost:8001/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('available_models', [])
            current = data.get('current_model', 'Unknown')
            print(f"✅ YOLO Models: {len(models)} available, current: {current}")
        else:
            print(f"❌ YOLO Models: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ YOLO Models: {e}")

def test_frontend():
    """Test frontend accessibility"""
    print("\n🧪 Testing Frontend...")

    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        if response.status_code == 200:
            if "Sentrix" in response.text:
                print("✅ Frontend: Accessible and serving Sentrix app")
            else:
                print("❌ Frontend: Accessible but not serving expected content")
        else:
            print(f"❌ Frontend: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend: {e}")

def main():
    """Run all integration tests"""
    print("🚀 Sentrix Integration Test Suite")
    print("=" * 50)

    # Test service health
    print("\n📡 Testing Service Health...")
    backend_ok = test_service_health("Backend", "http://localhost:8000/")
    yolo_ok = test_service_health("YOLO Service", "http://localhost:8001/health")
    frontend_ok = test_service_health("Frontend", "http://localhost:3000/")

    # Test specific functionalities
    if backend_ok:
        test_backend_api()

    if yolo_ok:
        test_yolo_service()

    if frontend_ok:
        test_frontend()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Integration Test Summary:")
    print(f"Backend: {'✅ OK' if backend_ok else '❌ FAILED'}")
    print(f"YOLO Service: {'✅ OK' if yolo_ok else '❌ FAILED'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAILED'}")

    if all([backend_ok, yolo_ok, frontend_ok]):
        print("\n🎉 ALL SERVICES ARE RUNNING CORRECTLY!")
        print("You can now access:")
        print("- Frontend: http://localhost:3000")
        print("- Backend API Docs: http://localhost:8000/docs")
        print("- YOLO Service Docs: http://localhost:8001/docs")
    else:
        print("\n⚠️  Some services have issues. Check the logs above.")

if __name__ == "__main__":
    main()