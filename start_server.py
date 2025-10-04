#!/usr/bin/env python3
"""
Simple server launcher without signal handling conflicts.
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Change to service directory
    service_dir = Path(__file__).parent
    os.chdir(service_dir)
    
    # Local development configuration
    host = "127.0.0.1"  # Local only
    port = 8000
    
    print("🚀 Starting ACT Strategic Service (Local Mode)")
    print("=" * 50)
    print("📍 Service Directory:", service_dir)
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print("🖥️ Environment: Local Development")
    print("👁️ Browser Mode: Visible (headless=false)")
    print()
    
    # Run the server with local development configuration
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,  # Disable reload to avoid signal conflicts
        log_level="info",
        access_log=True
    )