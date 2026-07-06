#!/usr/bin/env python3
"""检查数据库中的用户"""

import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.db.models import User

async def check_users():
    async with AsyncSessionLocal() as session:
        try:
            # 查询所有用户
            result = await session.execute(
                text("SELECT id, username, email, is_active, is_deleted FROM users LIMIT 10")
            )
            users = result.fetchall()

            if not users:
                print("❌ 数据库中没有用户！")
                print("\n可能的原因：")
                print("1. 数据库是新创建的，还没有用户数据")
                print("2. 需要手动创建用户或运行初始化脚本")
                return

            print(f"✅ 找到 {len(users)} 个用户：\n")
            for user in users:
                user_id, username, email, is_active, is_deleted = user
                status = "✅ 活跃" if is_active and not is_deleted else "❌ 禁用"
                print(f"  ID: {user_id}")
                print(f"  用户名: {username}")
                print(f"  邮箱: {email}")
                print(f"  状态: {status}")
                print()

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_users())
