#!/usr/bin/env python3
"""
Run Alembic migrations on both local and production databases.
"""
import os
import subprocess
import sys

def run_migrations(environment, description):
    print(f"🔄 Running migrations on {description}...")
    os.environ["ENVIRONMENT"] = environment
    
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], check=True)
        print(f"✅ {description} migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} migration failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

def main():
    print("🚀 Running migrations on BOTH databases...")
    print("=" * 60)
    
    # Run local migrations first
    local_success = run_migrations("local", "LOCAL")
    print()
    
    # Run production migrations
    production_success = run_migrations("production", "PRODUCTION")
    print()
    
    # Summary
    print("=" * 60)
    if local_success and production_success:
        print("🎉 All migrations completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some migrations failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
