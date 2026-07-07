#!/usr/bin/env python3
"""
完整认证流程测试
包括：登录 → 获取Token → 访问受保护资源 → API Keys管理
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

print('=' * 70)
print('完整认证流程测试')
print('=' * 70)
print(f'时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# 测试结果
results = []

def test_endpoint(name, method, path, data=None, headers=None, auth_token=None):
    """测试端点"""
    try:
        url = f'{BASE_URL}{path}'

        # 准备请求头
        req_headers = {'Content-Type': 'application/json'}
        if auth_token:
            req_headers['Authorization'] = f'Bearer {auth_token}'
        if headers:
            req_headers.update(headers)

        # 准备请求
        if data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
        else:
            req = urllib.request.Request(url, headers=req_headers, method=method)

        # 发送请求
        try:
            response = urllib.request.urlopen(req, timeout=3)
            status = response.getcode()
            resp_data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            status = e.code
            resp_data = json.loads(e.read().decode('utf-8'))

        success = status in [200, 201]
        results.append({'name': name, 'status': status, 'success': success})

        status_icon = '✓' if success else '✗'
        print(f'{status_icon} {name} - HTTP {status}')

        if success and isinstance(resp_data, dict) and 'password' not in name:
            resp_str = json.dumps(resp_data, ensure_ascii=False)
            if len(resp_str) > 100:
                resp_str = resp_str[:100] + '...'
            print(f'  {resp_str}')

        return {'success': success, 'status': status, 'data': resp_data}

    except Exception as e:
        results.append({'name': name, 'status': 'ERROR', 'success': False})
        print(f'✗ {name} - 失败: {e}')
        return {'success': False, 'error': str(e)}


# ============ 步骤1: 用户登录 ============
print('1️⃣  用户登录')
print('=' * 70)

login_result = test_endpoint(
    '用户登录',
    'POST',
    '/api/v1/auth/login',
    data={'username': 'admin123', 'password': 'admin123'},
)

if not login_result['success']:
    print('\n✗ 登录失败，无法继续测试')
    exit(1)

access_token = login_result['data']['access_token']
print(f'\n✓ 获得访问令牌: {access_token[:40]}...')

# ============ 步骤2: 获取用户信息 ============
print('\n\n2️⃣  获取用户信息')
print('=' * 70)

test_endpoint(
    '获取当前用户信息',
    'GET',
    '/api/v1/auth/me',
    auth_token=access_token
)

# ============ 步骤3: 任务管理 ============
print('\n\n3️⃣  任务管理功能')
print('=' * 70)

test_endpoint(
    '获取任务列表',
    'GET',
    '/api/v1/tasks/',
    auth_token=access_token
)

test_endpoint(
    '查询任务状态',
    'GET',
    '/api/v1/tasks/test-task-001',
    auth_token=access_token
)

# ============ 步骤4: API Keys管理 ============
print('\n\n4️⃣  API Keys 管理')
print('=' * 70)

# 4.1 获取现有API Keys
result = test_endpoint(
    '获取 API Keys 列表',
    'GET',
    '/api/v1/auth/api-keys',
    auth_token=access_token
)

# 4.2 创建新的API Key
print('\n创建新 API Key:')
create_result = test_endpoint(
    '创建 API Key',
    'POST',
    '/api/v1/auth/api-keys',
    data={
        'name': 'Test API Key',
        'permissions': 'predict,history',
        'expires_in_days': 90
    },
    auth_token=access_token
)

if create_result['success']:
    new_api_key = create_result['data'].get('api_key')
    if new_api_key:
        print(f'\n✓ 新创建的API Key: {new_api_key[:30]}...')
        print(f'  前缀: {create_result["data"].get("key_prefix")}')
        print(f'  权限: {create_result["data"].get("permissions")}')

        # 4.3 测试使用新API Key
        print('\n\n5️⃣  使用 API Key 认证')
        print('=' * 70)

        test_endpoint(
            '使用 API Key 获取用户信息',
            'GET',
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {new_api_key}'}
        )

# ============ 步骤6: 其他功能 ============
print('\n\n6️⃣  其他功能测试')
print('=' * 70)

test_endpoint(
    '更新个人信息',
    'PUT',
    '/api/v1/auth/profile',
    data={'nickname': '测试用户', 'email': 'test@example.com'},
    auth_token=access_token
)

test_endpoint(
    '修改密码',
    'POST',
    '/api/v1/auth/change-password',
    data={'current_password': 'admin123', 'new_password': 'newpass123'},
    auth_token=access_token
)

# ============ 测试报告 ============
print('\n\n' + '=' * 70)
print('测试报告')
print('=' * 70)

passed = sum(1 for r in results if r['success'])
failed = sum(1 for r in results if not r['success'])

print(f'\n总计: {len(results)} 个测试')
print(f'通过: {passed} ({passed/len(results)*100:.1f}%)')
print(f'失败: {failed}')

if failed == 0:
    print('\n✅ 所有测试通过！')
else:
    print(f'\n⚠️  {failed} 个测试失败')

    print('\n失败的测试:')
    for r in results:
        if not r['success']:
            print(f'  ✗ {r["name"]} - {r["status"]}')

print(f'\n完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 70)
