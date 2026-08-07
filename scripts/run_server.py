#!/usr/bin/env python3
"""
Server startup script for the Metis PII Detection & Document Masking API.
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Enable dev bypass for local development
    os.environ['ALLOW_DEV_BYPASS'] = '1'

    # Use SQLite for easy local dev (no PostgreSQL required)
    if not os.environ.get('DATABASE_URL'):
        os.environ['SQLITE_FALLBACK'] = '1'

    print("=" * 60)
    print("  Metis — PII Detection & Document Masking API")
    print("=" * 60)
    print(f"  Server:  http://localhost:8001")
    print(f"  Docs:    http://localhost:8001/docs")
    print(f"  DB:      {'PostgreSQL' if not os.environ.get('SQLITE_FALLBACK') else 'SQLite (local dev)'}")
    print(f"  Auth:    {'Dev bypass (no login required)' if os.environ.get('ALLOW_DEV_BYPASS') else 'JWT'}")
    print("=" * 60)
    print("  Press Ctrl+C to stop the server")
    print()

    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
