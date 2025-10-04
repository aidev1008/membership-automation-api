#!/usr/bin/env python3
"""
Railway-specific server launcher.
Optimized for cloud deployment with proper host binding and Playwright installation.
"""

import uvicorn
import os
import subprocess
import sys
from pathlib import Path


def install_playwright_browsers():
    """Install Playwright browsers in Railway environment."""
    try:
        print("🎭 Installing Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "firefox"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Playwright browsers installed successfully")
        else:
            print(f"⚠️ Playwright installation warning: {result.stderr}")
            # Don't fail - browsers might already be installed
            
    except subprocess.TimeoutExpired:
        print("⏰ Playwright installation timed out, continuing...")
    except Exception as e:
        print(f"⚠️ Error installing Playwright browsers: {e}")
        # Don't fail - continue anyway


if __name__ == "__main__":
    # Change to service directory
    service_dir = Path(__file__).parent
    os.chdir(service_dir)
    
    # Set Railway-specific environment variables
    os.environ["HEADLESS"] = "true"
    os.environ["HOST"] = "0.0.0.0"
    
    # Get Railway port
    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    
    print("🚀 Starting ACT Strategic Service (Railway Mode)")
    print("=" * 50)
    print("📍 Service Directory:", service_dir)
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print("☁️ Environment: Railway Cloud")
    print("🎭 Browser Mode: Headless")
    print()
    
    # Install Playwright browsers for Railway
    install_playwright_browsers()
    
    print()
    print("🏃 Starting web server...")
    
    # Run the server with Railway-optimized configuration
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,  # Never reload in production
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for Railway
        timeout_keep_alive=65,  # Railway timeout handling
        limit_concurrency=10  # Railway resource limits
    )