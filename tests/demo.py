#!/usr/bin/env python3
"""
Demo script to test the Schmick membership service.
This will start the service and make a test request so you can see the browser in action.
"""

import asyncio
import time
import httpx
import subprocess
import signal
import sys
from pathlib import Path

async def test_service():
    """Test the service with a sample request."""
    
    # Wait a bit for the server to start
    print("⏳ Waiting for server to start...")
    await asyncio.sleep(3)
    
    # Test data
    test_record = {
        "salesforceId": "DEMO-12345", 
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "dob": "1990-01-01",
        "phone": "555-0123"
    }
    
    headers = {
        "x-api-key": "test-demo-key-12345",
        "Content-Type": "application/json"
    }
    
    try:
        print("🏥 Testing health endpoint...")
        async with httpx.AsyncClient() as client:
            # Test health endpoint first
            response = await client.get("http://localhost:8000/health", timeout=10.0)
            print(f"✅ Health check: {response.status_code} - {response.json()}")
            
            print("🚀 Sending membership request...")
            print(f"📝 Test record: {test_record}")
            print("👀 Watch for the browser window to open!")
            print("🌐 The browser will navigate to httpbin.org and fill the form")
            
            # Test process endpoint  
            response = await client.post(
                "http://localhost:8000/process", 
                json=test_record,
                headers=headers,
                timeout=60.0
            )
            
            print(f"📋 Response status: {response.status_code}")
            print(f"📋 Response body: {response.json()}")
            
            if response.status_code == 200:
                print("🎉 Success! The demo worked.")
            else:
                print("⚠️  Expected error due to demo selectors - that's normal!")
                
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        print("💡 This is expected since we're using demo selectors")

def main():
    """Run the demo."""
    print("🎬 Schmick Service Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Start the FastAPI service with visible browser (HEADLESS=false)")
    print("2. Make a test request to create a membership")  
    print("3. You'll see Chrome open and navigate to httpbin.org")
    print("4. The browser will fill out a demo form")
    print("5. It will likely error (expected) but you'll see it in action!")
    print("")
    print("Press Ctrl+C at any time to stop")
    print("=" * 50)
    
    # Change to the service directory
    service_dir = Path(__file__).parent
    
    server_process = None
    try:
        # Start the server
        print("🚀 Starting FastAPI server...")
        server_process = subprocess.Popen([
            "venv/bin/python", "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=service_dir)
        
        # Run the test
        asyncio.run(test_service())
        
        print("\n" + "=" * 50)
        print("✅ Demo completed!")
        print("💡 The server is still running for you to test manually")
        print("🔗 Try: curl http://localhost:8000/health")  
        print("📚 API docs at: http://localhost:8000/docs")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Keep the server running for manual testing
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if server_process:
            print("🔄 Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
            print("✅ Server stopped")

if __name__ == "__main__":
    main()