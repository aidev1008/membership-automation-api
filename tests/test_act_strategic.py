#!/usr/bin/env python3
"""
ACT Strategic Fix My Ads Service Test Script
Tests the real workflow: Login -> Form Fill -> Extract ID from Table
"""

import subprocess
import time
import requests
import json

def test_act_strategic_service():
    """Test the ACT Strategic service workflow."""
    
    print("🎯 ACT Strategic Fix My Ads Service Test")
    print("=" * 60)
    print("Workflow: Login → Fill Form → Extract ID from Table")
    print("URLs:")
    print("  📝 Login: https://actstrategic.ai/myaccount/")
    print("  📋 Form: https://actstrategic.ai/fixmyads/")
    print("  📊 Results: https://actstrategic.ai/myaccount/fix-my-ads/")
    print("=" * 60)
    
    # Start server in background
    print("🚀 Starting ACT Strategic service...")
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
        
        # Test ACT Strategic workflow
        print("\n🎬 Testing ACT Strategic Fix My Ads workflow...")
        print("📋 Sending test data to service...")
        
        test_data = {
            "salesforceId": "ACT-TEST-12345",
            "firstName": "John",
            "lastName": "Doe", 
            "email": "john.doe@example.com",
            "dob": "1990-01-01",
            "phone": "555-0123",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zipCode": "12345"
        }
        
        headers = {
            "x-api-key": "test-demo-key-12345",
            "Content-Type": "application/json"
        }
        
        print("\n👀 IMPORTANT: Watch for Chrome browser to open!")
        print("🔍 You should see the browser:")
        print("   1. Navigate to https://actstrategic.ai/myaccount/")
        print("   2. Attempt to login (may fail if no real credentials)")
        print("   3. Navigate to /fixmyads/ and fill form")
        print("   4. Navigate to /myaccount/fix-my-ads/ for results")
        print()
        
        response = requests.post(
            "http://localhost:8000/process", 
            json=test_data,
            headers=headers,
            timeout=60  # ACT Strategic may be slower than demo
        )
        
        print(f"📋 Response Status: {response.status_code}")
        print(f"📋 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🎉 SUCCESS! Fix My Ads ID: {result.get('membership', 'N/A')}")
        else:
            print("\n⚠️  Got an error response. Common reasons:")
            print("   • Need real ACT Strategic credentials in .env file")
            print("   • Need to update selectors after inspecting the actual website")
            print("   • Website structure may be different than expected")
            print("   • May need to handle additional steps (2FA, etc.)")
            
        print(f"\n📝 Next Steps:")
        print("1. 🔑 Update SCHMICK_USER and SCHMICK_PASS in .env with real credentials")
        print("2. 🔍 Inspect the actual ACT Strategic website to get correct selectors")
        print("3. 🛠️  Update website_selectors.py with real form field names")
        print("4. 🧪 Test with real credentials")
        
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this may be normal for first login attempt")
        print("💡 The browser automation may still be working in the background")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Check the server logs for detailed error information")
        
    finally:
        print("\n🛑 Stopping server...")
        server.terminate()
        server.wait()
        print("✅ Test completed!")
        
        print(f"\n🔧 Configuration Notes:")
        print("• The service is configured for actstrategic.ai URLs")
        print("• Selectors are set up with common patterns but may need adjustment")
        print("• Browser will stay visible (HEADLESS=false) so you can see what happens")
        print("• Update .env file with real credentials before production use")

if __name__ == "__main__":
    test_act_strategic_service()