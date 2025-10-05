#!/usr/bin/env python3
"""
Server startup script for the Optiv Masking API
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Enable dev bypass for local development
    os.environ['ALLOW_DEV_BYPASS'] = '1'
    
    print("Starting Optiv Masking API server...")
    print("Server will be available at: http://localhost:8001")
    print("API documentation at: http://localhost:8001/docs")
    print("Dev bypass enabled for local testing")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
