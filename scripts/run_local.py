#!/usr/bin/env python3
"""
Run the FastAPI application in local development mode.
"""
import os
import sys
import uvicorn

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment to local
os.environ["ENVIRONMENT"] = "local"

if __name__ == "__main__":
    print("🚀 Starting FastAPI server in LOCAL mode...")
    print("📁 Using env.local configuration")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
