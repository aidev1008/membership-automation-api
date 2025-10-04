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
    
    print("🚀 Starting ACT Strategic Service...")
    print("📍 Service Directory:", service_dir)
    print("🌐 URL: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print()
    
    # Run the server with simple configuration
    uvicorn.run(
        "app:app",
        host="127.0.0.1", 
        port=8000,
        reload=False,  # Disable reload to avoid signal conflicts
        log_level="info",
        access_log=True
    )