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
from backend.models.stock import Stock

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


async def init_stock_data() -> None:
    from backend.models.stock import Stock
    async with AsyncSessionFactory() as session:
        async with session.begin():
            existing = await session.execute(select(Stock).limit(1))
            if existing.scalar_one_or_none():
                logger.info("Stock data already exists, skipping seed")
                return
            stocks = [
        Stock(symbol="000001", name="平安银行", market="A", exchange="SZSE", industry="银行", currency="CNY", status="active"),
        Stock(symbol="000002", name="万科A", market="A", exchange="SZSE", industry="房地产", currency="CNY", status="active"),
        Stock(symbol="000333", name="美的集团", market="A", exchange="SZSE", industry="家用电器", currency="CNY", status="active"),
        Stock(symbol="000651", name="格力电器", market="A", exchange="SZSE", industry="家用电器", currency="CNY", status="active"),
        Stock(symbol="000725", name="京东方A", market="A", exchange="SZSE", industry="电子", currency="CNY", status="active"),
        Stock(symbol="000858", name="五粮液", market="A", exchange="SZSE", industry="食品饮料", currency="CNY", status="active"),
        Stock(symbol="002007", name="华兰生物", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="002230", name="科大讯飞", market="A", exchange="SZSE", industry="计算机", currency="CNY", status="active"),
        Stock(symbol="002304", name="洋河股份", market="A", exchange="SZSE", industry="食品饮料", currency="CNY", status="active"),
        Stock(symbol="002352", name="顺丰控股", market="A", exchange="SZSE", industry="交通运输", currency="CNY", status="active"),
        Stock(symbol="002371", name="北方华创", market="A", exchange="SZSE", industry="电子", currency="CNY", status="active"),
        Stock(symbol="002415", name="海康威视", market="A", exchange="SZSE", industry="计算机", currency="CNY", status="active"),
        Stock(symbol="002459", name="晶澳科技", market="A", exchange="SZSE", industry="电力设备", currency="CNY", status="active"),
        Stock(symbol="002475", name="立讯精密", market="A", exchange="SZSE", industry="电子", currency="CNY", status="active"),
        Stock(symbol="002594", name="比亚迪", market="A", exchange="SZSE", industry="汽车", currency="CNY", status="active"),
        Stock(symbol="002714", name="牧原股份", market="A", exchange="SZSE", industry="农林牧渔", currency="CNY", status="active"),
        Stock(symbol="002812", name="恩捷股份", market="A", exchange="SZSE", industry="电力设备", currency="CNY", status="active"),
        Stock(symbol="300014", name="亿纬锂能", market="A", exchange="SZSE", industry="电力设备", currency="CNY", status="active"),
        Stock(symbol="300015", name="爱尔眼科", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="300059", name="东方财富", market="A", exchange="SZSE", industry="非银金融", currency="CNY", status="active"),
        Stock(symbol="300122", name="智飞生物", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="300124", name="汇川技术", market="A", exchange="SZSE", industry="机械设备", currency="CNY", status="active"),
        Stock(symbol="300274", name="阳光电源", market="A", exchange="SZSE", industry="电力设备", currency="CNY", status="active"),
        Stock(symbol="300308", name="中际旭创", market="A", exchange="SZSE", industry="通信", currency="CNY", status="active"),
        Stock(symbol="300413", name="芒果超媒", market="A", exchange="SZSE", industry="传媒", currency="CNY", status="active"),
        Stock(symbol="300433", name="蓝思科技", market="A", exchange="SZSE", industry="电子", currency="CNY", status="active"),
        Stock(symbol="300450", name="先导智能", market="A", exchange="SZSE", industry="机械设备", currency="CNY", status="active"),
        Stock(symbol="300498", name="温氏股份", market="A", exchange="SZSE", industry="农林牧渔", currency="CNY", status="active"),
        Stock(symbol="300502", name="新易盛", market="A", exchange="SZSE", industry="通信", currency="CNY", status="active"),
        Stock(symbol="300676", name="华大基因", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="300750", name="宁德时代", market="A", exchange="SZSE", industry="电力设备", currency="CNY", status="active"),
        Stock(symbol="300759", name="康龙化成", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="300760", name="迈瑞医疗", market="A", exchange="SZSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="600036", name="招商银行", market="A", exchange="SSE", industry="银行", currency="CNY", status="active"),
        Stock(symbol="600276", name="恒瑞医药", market="A", exchange="SSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="600309", name="万华化学", market="A", exchange="SSE", industry="基础化工", currency="CNY", status="active"),
        Stock(symbol="600519", name="贵州茅台", market="A", exchange="SSE", industry="食品饮料", currency="CNY", status="active"),
        Stock(symbol="600585", name="海螺水泥", market="A", exchange="SSE", industry="建筑材料", currency="CNY", status="active"),
        Stock(symbol="600690", name="海尔智家", market="A", exchange="SSE", industry="家用电器", currency="CNY", status="active"),
        Stock(symbol="600809", name="山西汾酒", market="A", exchange="SSE", industry="食品饮料", currency="CNY", status="active"),
        Stock(symbol="600887", name="伊利股份", market="A", exchange="SSE", industry="食品饮料", currency="CNY", status="active"),
        Stock(symbol="600900", name="长江电力", market="A", exchange="SSE", industry="公用事业", currency="CNY", status="active"),
        Stock(symbol="600941", name="中国移动", market="A", exchange="SSE", industry="通信", currency="CNY", status="active"),
        Stock(symbol="601088", name="中国神华", market="A", exchange="SSE", industry="煤炭", currency="CNY", status="active"),
        Stock(symbol="601166", name="兴业银行", market="A", exchange="SSE", industry="银行", currency="CNY", status="active"),
        Stock(symbol="601318", name="中国平安", market="A", exchange="SSE", industry="非银金融", currency="CNY", status="active"),
        Stock(symbol="601398", name="工商银行", market="A", exchange="SSE", industry="银行", currency="CNY", status="active"),
        Stock(symbol="601766", name="中国中车", market="A", exchange="SSE", industry="机械设备", currency="CNY", status="active"),
        Stock(symbol="601857", name="中国石油", market="A", exchange="SSE", industry="石油石化", currency="CNY", status="active"),
        Stock(symbol="601899", name="紫金矿业", market="A", exchange="SSE", industry="有色金属", currency="CNY", status="active"),
        Stock(symbol="603259", name="药明康德", market="A", exchange="SSE", industry="医药生物", currency="CNY", status="active"),
        Stock(symbol="688981", name="中芯国际", market="A", exchange="SSE", industry="电子", currency="CNY", status="active"),
            ]
            session.add_all(stocks)
            logger.info(f"Seeded {len(stocks)} popular stocks")

if __name__ == "__main__":
    asyncio.run(init_default_data())
