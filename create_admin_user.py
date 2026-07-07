#!/usr/bin/env python3
"""创建初始管理员用户"""

import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from passlib.context import CryptContext

# 数据库配置
DB_HOST = "db"
DB_PORT = 5432
DB_USER = "nlp_user"
DB_PASS = "nlp_pass"
DB_NAME = "nlp_db"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_admin_user():
    try:
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # 检查是否已存在 admin 用户
            result = await session.execute(
                text("SELECT id, username, email FROM users WHERE username = 'admin' OR username = 'admin123'")
            )
            existing_user = result.fetchone()

            if existing_user:
                print(f"⚠️  用户已存在: ID={existing_user[0]}, 用户名={existing_user[1]}, 邮箱={existing_user[2]}")
                print("\n如果要重置密码，请先删除该用户或手动更新密码。")
                return False

            # 创建 admin 用户
            print("正在创建管理员用户...")
            hashed_password = get_password_hash("admin123")

            result = await session.execute(
                text("""
                    INSERT INTO users (username, email, hashed_password, nickname, role, is_active, is_verified, is_deleted, created_at, updated_at)
                    VALUES (:username, :email, :hashed_password, :nickname, :role, :is_active, :is_verified, :is_deleted, NOW(), NOW())
                    RETURNING id, username, email
                """),
                {
                    "username": "admin123",
                    "email": "admin@example.com",
                    "hashed_password": hashed_password,
                    "nickname": "管理员",
                    "role": "admin",
                    "is_active": True,
                    "is_verified": True,
                    "is_deleted": False,
                }
            )

            new_user = result.fetchone()
            await session.commit()

            print(f"✅ 用户创建成功!")
            print(f"  ID: {new_user[0]}")
            print(f"  用户名: {new_user[1]}")
            print(f"  邮箱: {new_user[2]}")
            print(f"  密码: admin123")
            print(f"\n🎉 现在可以使用 admin123 / admin123 登录了！")

            return True

    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(create_admin_user())
    sys.exit(0 if result else 1)
