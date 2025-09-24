#!/usr/bin/env python3
"""
Run the FastAPI application in production mode.
"""
import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment to production
os.environ["ENVIRONMENT"] = "production"

# Load production environment variables from config file if running locally
# (On Render, these will be set as actual environment variables)
if not os.getenv("DB_HOST"):
    project_root = Path(__file__).parent.parent
    env_file = project_root / "config" / "env.production"
    if env_file.exists():
        load_dotenv(env_file)
        print("📁 Loaded production config from file for local testing")
    else:
        print("⚠️  No production config file found - make sure environment variables are set")

if __name__ == "__main__":
    print("🚀 Starting FastAPI server in PRODUCTION mode...")
    print("📁 Using production configuration")
    print("🗄️  Connecting to PostgreSQL database")
    print("🌐 Server will be available at: http://0.0.0.0:8000")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # No auto-reload in production
        log_level="warning"
    )
