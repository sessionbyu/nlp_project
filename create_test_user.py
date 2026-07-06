#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.db.session import async_session
from app.db.models import User
from app.services.auth import get_password_hash, verify_password
from sqlalchemy import select

import asyncio

async def test():
    async with async_session() as session:
        # 检查用户
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"用户数量: {len(users)}")

        for user in users:
            print(f"\n用户: {user.username}")
            print(f"  ID: {user.id}")
            print(f"  邮箱: {user.email}")
            print(f"  活跃: {user.is_active}")

            # 测试密码
            is_valid = verify_password('admin123', user.hashed_password)
            print(f"  密码验证: {'✓' if is_valid else '✗'}")

        if not users:
            print("\n创建测试用户...")
            hashed = get_password_hash('admin123')
            print(f"密码哈希: {hashed[:50]}...")

            user = User(
                username='admin123',
                email='admin123@example.com',
                hashed_password=hashed,
                nickname='Admin123',
                role='admin',
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print("✓ 用户创建成功")
            print(f"  ID: {user.id}")

asyncio.run(test())
