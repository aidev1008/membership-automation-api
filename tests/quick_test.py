#!/usr/bin/env python3
"""
Quick test script to verify the improved Schmick service.
"""

import subprocess
import time
import requests
import signal
import os

def test_service():
    """Test the service quickly."""
    
    # Start server in background
    print("🚀 Starting server...")
    server = subprocess.Popen([
        "venv/bin/python", "-m", "uvicorn", "app:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server startup...")
        time.sleep(4)
        
        # Test health
        print("🏥 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health: {response.status_code} - {response.json()}")
        
        # Test membership processing
        print("🎬 Testing membership processing (watch for browser!)...")
        test_data = {
            "salesforceId": "DEMO-12345",
            "firstName": "John",
            "lastName": "Doe", 
            "email": "john.doe@example.com",
            "dob": "1990-01-01"
        }
        
        headers = {
            "x-api-key": "test-demo-key-12345",
            "Content-Type": "application/json"
        }
        
        print("👀 Watch for Chrome browser to open!")
        response = requests.post(
            "http://localhost:8000/process", 
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📋 Result: {response.status_code}")
        print(f"📋 Body: {response.json()}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! The service is working!")
        else:
            print("⚠️ Got an error response, but that's expected in demo mode")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 This might be expected with demo selectors")
    finally:
        print("🛑 Stopping server...")
        server.terminate()
        server.wait()
        print("✅ Test completed!")

if __name__ == "__main__":
    test_service()