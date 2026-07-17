"""
Project: AlphaQuant AI
File: scripts/init_data.py
Description: Initialize default data (roles, permissions, admin user).
Python Version: 3.11.9
"""
from __future__ import annotations
import asyncio
from loguru import logger
from sqlalchemy import select
from backend.core.security import hash_password
from backend.database.session import AsyncSessionFactory
from backend.models.user import User, Role, Permission

async def init_default_data() -> None:
    async with AsyncSessionFactory() as session:
        async with session.begin():
            admin_role = await session.execute(select(Role).where(Role.name == "admin"))
            if not admin_role.scalar_one_or_none():
                admin_role = Role(name="admin", description="系统管理员", is_system=True)
                session.add(admin_role)
                user_role = Role(name="user", description="普通用户", is_system=True)
                session.add(user_role)
            admin_user = await session.execute(select(User).where(User.username == "admin"))
            if not admin_user.scalar_one_or_none():
                admin = User(
                    username="admin",
                    email="admin@alphaquant.ai",
                    hashed_password=hash_password("admin123456"),
                    full_name="管理员",
                    is_superuser=True,
                )
                session.add(admin)
        await session.commit()
    logger.info("Default data initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_default_data())
