#!/usr/bin/env python3
"""
Run the FastAPI application in production mode.
"""
import os
import sys
import uvicorn

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment to production
os.environ["ENVIRONMENT"] = "production"

if __name__ == "__main__":
    print("🚀 Starting FastAPI server in PRODUCTION mode...")
    print("📁 Using env.production configuration")
    print("🗄️  Connecting to Supabase")
    print("🌐 Server will be available at: http://0.0.0.0:8000")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # No auto-reload in production
        log_level="warning"
    )
