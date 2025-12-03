"""
Script to create an admin user
Run with: python -m scripts.create_admin
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import async_session_maker
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin():
    async with async_session_maker() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print(f"Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"Email: admin@example.com")
        print(f"\nPlease change the password after first login!")


if __name__ == "__main__":
    asyncio.run(create_admin())
