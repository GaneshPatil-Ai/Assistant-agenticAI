#!/usr/bin/env python3
"""
Startup script for LangGraph Supervisor-Worker API
Can run directly or with Gunicorn
"""

import os
import sys
import asyncio
from config import Config

def main():
    """Main entry point"""
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated successfully")
        
        # Import and create app
        from api import app
        print("✅ Falcon application created successfully")
        
        # Check if running with Gunicorn
        if 'gunicorn' in sys.argv[0]:
            print("🚀 Starting with Gunicorn...")
            return app
        
        # Run directly for development
        print("🚀 Starting development server...")
        import uvicorn
        
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()