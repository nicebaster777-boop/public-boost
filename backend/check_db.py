"""Script to check database connection."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def check_connection():
    """Check database connection."""
    print(f"Checking connection to: {settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}")
    
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row:
                print("[OK] Database connection successful!")
                return 0
            else:
                print("[ERROR] Database connection failed: No response")
                return 1
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check .env file for correct database credentials")
        print("3. Ensure database exists")
        print(f"4. Connection string: {settings.database_url.replace(settings.postgres_password, '***')}")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    exit_code = asyncio.run(check_connection())
    sys.exit(exit_code)

