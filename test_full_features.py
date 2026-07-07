#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')
import bcrypt
import json
import urllib.request

print('=' * 70)
print('完整功能测试 - 任务管理 + 个人设置')
print('=' * 70)

# 1. 生成新的密码哈希
print('\n1️⃣  生成密码哈希')
print('-' * 70)

password = b'admin123'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)

print(f'✓ 新密码哈希: {hashed.decode()[:60]}...')

# 2. 更新数据库中的密码
print('\n2️⃣  更新数据库密码')
print('-' * 70)

from app.db.session import async_session
from app.db.models import User
from sqlalchemy import select
import asyncio

async def update_password():
    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == 'admin123'))
        user = result.scalar_one_or_none()

        if user:
            user.hashed_password = hashed.decode()
            await session.commit()
            print('✓ 数据库密码已更新')
            return True
        else:
            print('✗ 用户不存在')
            return False

success = asyncio.run(update_password())

if not success:
    print('\n创建用户...')
    # 创建用户
    from app.services.auth import get_password_hash

    async def create_user():
        async with async_session() as session:
            user = User(
                username='admin123',
                email='admin123@example.com',
                hashed_password=hashed.decode(),
                nickname='Administrator',
                role='admin',
                is_active=True,
                is_verified=True,
                is_deleted=False
            )
            session.add(user)
            await session.commit()
            print('✓ 用户创建成功')

    asyncio.run(create_user())

# 3. 测试登录
print('\n3️⃣  测试登录')
print('-' * 70)

BASE_URL = 'http://localhost:8000'

try:
    data = json.dumps({'username': 'admin', 'password': 'admin123'}).encode()
    req = urllib.request.Request(
        f'{BASE_URL}/api/v1/auth/login',
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=3)
    result = json.loads(response.read().decode('utf-8'))

    print(f'✓ 登录成功')
    print(f'  用户: {result["user"]["username"]}')
    print(f'  角色: {result["user"]["role"]}')
    print(f'  Token: {result["access_token"][:50]}...')

    access_token = result['access_token']
    auth_headers = {'Authorization': f'Bearer {access_token}'}

except urllib.error.HTTPError as e:
    print(f'✗ 登录失败: HTTP {e.code}')
    error = json.loads(e.read().decode('utf-8'))
    print(f'  错误: {error}')
    access_token = None
    auth_headers = {}
except Exception as e:
    print(f'✗ 登录失败: {e}')
    access_token = None
    auth_headers = {}

# 4. 测试认证后的端点
if access_token:
    print('\n4️⃣  测试认证后的端点')
    print('-' * 70)

    def auth_test(method, path, name, data=None):
        try:
            url = f'{BASE_URL}{path}'
            if data:
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={'Content-Type': 'application/json', **auth_headers},
                    method=method
                )
            else:
                req = urllib.request.Request(
                    url,
                    headers=auth_headers,
                    method=method
                )

            try:
                response = urllib.request.urlopen(req, timeout=3)
                status = response.getcode()
                resp = json.loads(response.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                status = e.code
                resp = json.loads(e.read().decode('utf-8'))

            if status in [200, 201]:
                print(f'✓ {name} - HTTP {status}')
                if isinstance(resp, dict) and 'password' not in name:
                    print(f'  {json.dumps(resp, ensure_ascii=False)[:100]}')
                return True
            else:
                print(f'  {name} - HTTP {status}')
                print(f'  {json.dumps(resp, ensure_ascii=False)[:100]}')
                return status in [404, 403]
        except Exception as e:
            print(f'✗ {name} - 失败: {e}')
            return False

    # 任务管理
    print('\n任务管理:')
    auth_test('GET', '/api/v1/tasks/', '获取任务列表')
    auth_test('GET', '/api/v1/tasks/test-123', '查询任务状态')
    auth_test('POST', '/api/v1/tasks/test-123/cancel', '取消任务')

    # 个人设置
    print('\n个人设置:')
    auth_test('GET', '/api/v1/auth/me', '获取用户信息')
    auth_test('PUT', '/api/v1/auth/profile', '更新个人信息', {'nickname': '测试用户'})
    auth_test('POST', '/api/v1/auth/change-password', '修改密码', {
        'current_password': 'admin123',
        'new_password': 'newpass123'
    })

    # API Keys
    print('\nAPI Keys:')
    auth_test('GET', '/api/v1/auth/api-keys', '获取API Keys列表')
    auth_test('POST', '/api/v1/auth/api-keys', '创建API Key', {
        'name': 'Test Key',
        'permissions': 'predict,history'
    })

# 5. 测试未认证端点
print('\n5️⃣  测试未认证端点')
print('-' * 70)

# Prometheus指标
try:
    req = urllib.request.Request(f'{BASE_URL}/api/v1/metrics')
    response = urllib.request.urlopen(req, timeout=3)
    content = response.read().decode('utf-8')
    if content.startswith('#'):
        print(f'✓ Prometheus指标 - HTTP 200 (格式正确)')
        print(f'  内容: {content[:150]}...')
except Exception as e:
    print(f'✗ Prometheus指标 - {e}')

print('\n' + '=' * 70)
print('测试完成')
print('=' * 70)
