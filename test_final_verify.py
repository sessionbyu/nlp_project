#!/usr/bin/env python3
"""
最终验证测试 - 所有修复的完整测试
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

print('=' * 70)
print('最终验证测试')
print('=' * 70)
print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

results = []

def test(name, method, path, data=None, headers=None, auth=None):
    try:
        url = f'{BASE_URL}{path}'
        req_headers = {'Content-Type': 'application/json'}
        if auth:
            req_headers['Authorization'] = f'Bearer {auth}'
        if headers:
            req_headers.update(headers)

        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers=req_headers,
                method=method
            )
        else:
            req = urllib.request.Request(url, headers=req_headers, method=method)

        try:
            r = urllib.request.urlopen(req, timeout=3)
            status = r.getcode()
            resp = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            status = e.code
            resp = json.loads(e.read().decode())

        success = status in [200, 201]
        results.append({'name': name, 'ok': success})
        icon = '✓' if success else '✗'
        print(f'{icon} {name} - {status}')
        return resp if success else None

    except Exception as e:
        results.append({'name': name, 'ok': False})
        print(f'✗ {name} - {e}')
        return None

# ============ 1. 健康检查 ============
print('1️⃣  健康检查')
print('-' * 70)
test('健康检查', 'GET', '/api/v1/health')
test('就绪检查', 'GET', '/api/v1/health/ready')
test('存活检查', 'GET', '/api/v1/health/live')

# ============ 2. 登录 ============
print('\n2️⃣  登录认证')
print('-' * 70)
login = test('用户登录', 'POST', '/api/v1/auth/login',
             data={'username': 'admin123', 'password': 'admin123'})

if not login:
    print("\n✗ 登录失败！")
    exit(1)

token = login['access_token']
print(f"\n✓ 登录成功，用户: {login['user']['username']}")

# ============ 3. 用户信息 ============
print('\n3️⃣  用户信息')
print('-' * 70)
test('获取用户信息', 'GET', '/api/v1/auth/me', auth=token)
test('更新个人信息', 'PUT', '/api/v1/auth/profile',
     data={'nickname': 'Admin'}, auth=token)
test('修改密码', 'POST', '/api/v1/auth/change-password',
     data={'current_password': 'admin123', 'new_password': 'admin123'}, auth=token)

# ============ 4. API Keys ============
print('\n4️⃣  API Keys 管理')
print('-' * 70)
test('获取API Keys', 'GET', '/api/v1/auth/api-keys', auth=token)
test('创建API Key', 'POST', '/api/v1/auth/api-keys',
     data={'name': 'Test', 'permissions': 'predict'}, auth=token)

# ============ 5. 任务管理 ============
print('\n5️⃣  任务管理')
print('-' * 70)
test('获取任务列表', 'GET', '/api/v1/tasks/', auth=token)

# ============ 总结 ============
print('\n\n' + '=' * 70)
passed = sum(1 for r in results if r['ok'])
failed = sum(1 for r in results if not r['ok'])
print(f'总计: {len(results)} | 通过: {passed} | 失败: {failed}')
if failed == 0:
    print('✅ 全部通过！')
else:
    print(f'⚠️  {failed} 个失败')
print('=' * 70)
