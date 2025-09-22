#!/usr/bin/env python3
"""
Unified migration management script.
Generates migrations based on production database schema and applies to both databases.
"""
import os
import subprocess
import sys
import argparse
from pathlib import Path

def set_environment(env):
    """Set the environment variable for database selection."""
    os.environ["ENVIRONMENT"] = env

def run_command(cmd, description, environment=None):
    """Run a command with proper environment setup."""
    if environment:
        set_environment(environment)
    
    print(f"🔄 {description}...")
    if environment:
        print(f"📁 Using env.{environment} configuration")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True, env=os.environ)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

def generate_migration(message=None):
    """Generate a new migration based on production database schema."""
    if not message:
        message = "Auto-generated migration from production schema"
    
    print("📝 Generating new migration based on PRODUCTION database...")
    print("📁 Using env.production configuration")
    print("-" * 50)
    
    set_environment("production")
    
    try:
        cmd = ["alembic", "revision", "--autogenerate", "-m", message]
        result = subprocess.run(cmd, check=True, env=os.environ)
        print("✅ New migration generated successfully!")
        print(f"📄 Message: {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration generation failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

def apply_migrations(environment, description):
    """Apply migrations to specified environment."""
    return run_command(
        ["alembic", "upgrade", "head"],
        f"Running migrations on {description}",
        environment
    )

def migrate_both():
    """Apply migrations to both databases."""
    print("🚀 Running migrations on BOTH databases...")
    print("=" * 60)
    
    local_success = apply_migrations("local", "LOCAL")
    print()
    
    production_success = apply_migrations("production", "PRODUCTION")
    print()
    
    print("=" * 60)
    if local_success and production_success:
        print("🎉 All migrations completed successfully!")
        return True
    else:
        print("❌ Some migrations failed. Check the output above.")
        return False

def generate_and_migrate(message=None):
    """Generate migration from production and apply to both databases."""
    print("🚀 Generate migration from PRODUCTION and apply to BOTH databases...")
    print("=" * 70)
    
    # Step 1: Generate migration based on production schema
    print("Step 1: Generating migration from production database schema")
    print("-" * 50)
    if not generate_migration(message):
        print("❌ Migration generation failed. Stopping.")
        return False
    
    print()
    
    # Step 2: Apply to both databases
    print("Step 2: Applying migration to both databases")
    print("-" * 50)
    if not migrate_both():
        print("❌ Migration application failed.")
        return False
    
    print("=" * 70)
    print("🎉 Complete migration workflow completed successfully!")
    return True

def show_status():
    """Show current migration status for both databases."""
    print("📊 Migration Status Report")
    print("=" * 50)
    
    # Check local status
    print("LOCAL Database:")
    set_environment("local")
    run_command(["alembic", "current"], "Checking local migration status", "local")
    print()
    
    # Check production status
    print("PRODUCTION Database:")
    set_environment("production")
    run_command(["alembic", "current"], "Checking production migration status", "production")
    print()

def main():
    parser = argparse.ArgumentParser(description="Unified migration management")
    parser.add_argument("action", choices=["generate", "migrate", "upgrade", "status"], 
                       help="Action to perform")
    parser.add_argument("-m", "--message", 
                       help="Message for new migration (optional)")
    
    args = parser.parse_args()
    
    if args.action == "generate":
        success = generate_migration(args.message)
    elif args.action == "migrate":
        success = migrate_both()
    elif args.action == "upgrade":
        success = generate_and_migrate(args.message)
    elif args.action == "status":
        show_status()
        success = True
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
