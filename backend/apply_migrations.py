"""Script to apply database migrations."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command
from app.core.config import settings


def apply_migrations():
    """Apply all pending migrations."""
    alembic_cfg = Config("alembic.ini")
    
    print(f"Connecting to database: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    print("Applying migrations...")
    
    try:
        command.upgrade(alembic_cfg, "head")
        print("[OK] Migrations applied successfully!")
        return 0
    except Exception as e:
        print(f"[ERROR] Error applying migrations: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check .env file for correct database credentials")
        print("3. Ensure database exists")
        return 1


if __name__ == "__main__":
    exit_code = apply_migrations()
    sys.exit(exit_code)

