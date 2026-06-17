"""
Run once to create all tables and seed a test user for local dev.

Usage:
    python -m scripts.init_db
    python -m scripts.init_db --username admin --password secret --name "Admin User"
"""
import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text

from app.database import Base, engine, AsyncSessionLocal
from app.models import user, session, recording, annotation  # noqa: F401 — registers all models
from app.models.user import User
from app.services.auth import hash_password


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[init_db] Tables created.")


async def seed_user(username: str, password: str, name: str):
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == username))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"[init_db] User '{username}' already exists — skipping seed.")
            return

        user_obj = User(
            username=username,
            password_hash=hash_password(password),
            name=name,
        )
        db.add(user_obj)
        await db.commit()
        print(f"[init_db] Seeded user '{username}' (id={user_obj.id})")


async def main(username: str, password: str, name: str):
    await create_tables()
    await seed_user(username, password, name)
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Init MXTZ local dev DB")
    parser.add_argument("--username", default="testuser", help="Seed username")
    parser.add_argument("--password", default="testpass123", help="Seed password")
    parser.add_argument("--name", default="Test User", help="Display name")
    args = parser.parse_args()

    asyncio.run(main(args.username, args.password, args.name))
