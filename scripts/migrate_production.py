#!/usr/bin/env python3
"""
Run Alembic migrations on production database (Supabase).
"""
import os
import subprocess
import sys

def run_migrations():
    print("🔄 Running migrations on PRODUCTION database (Supabase)...")
    print("📁 Using env.production configuration")
    print("-" * 50)
    
    # Set environment to production
    os.environ["ENVIRONMENT"] = "production"
    
    try:
        # Run alembic upgrade head with environment variable
        result = subprocess.run(["alembic", "upgrade", "head"], check=True, env=os.environ)
        print("✅ Production migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
