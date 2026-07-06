#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 数据库配置
DB_HOST = "db"
DB_PORT = 5432
DB_USER = "nlp_user"
DB_PASS = "nlp_pass"
DB_NAME = "nlp_db"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def check_users():
    try:
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # 查询用户
            result = await session.execute(
                text("SELECT id, username, email, is_active, is_deleted FROM users LIMIT 10")
            )
            users = result.fetchall()

            if not users:
                print("❌ 数据库中没有用户！")
                print("\n需要创建初始用户。")
                return False
            else:
                print(f"✅ 找到 {len(users)} 个用户:\n")
                for user in users:
                    user_id, username, email, is_active, is_deleted = user
                    status = "✅ 活跃" if is_active and not is_deleted else "❌ 禁用"
                    print(f"  ID: {user_id}")
                    print(f"  用户名: {username}")
                    print(f"  邮箱: {email}")
                    print(f"  状态: {status}")
                    print()
                return True
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(check_users())
    sys.exit(0 if result else 1)
