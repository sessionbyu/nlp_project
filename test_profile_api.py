#!/usr/bin/env python3
"""
测试个人设置页面的API调用
"""

import urllib.request
import json

BASE_URL = 'http://localhost:8000'

print('=' * 60)
print('个人设置API测试')
print('=' * 60)

# 1. 登录
print('\n1. 登录')
data = json.dumps({'username': 'admin123', 'password': 'admin123'}).encode()
req = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/login',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
r = urllib.request.urlopen(req)
login = json.loads(r.read())
token = login['access_token']
print(f'✓ Token: {token[:30]}...')

# 2. 获取用户信息
print('\n2. 获取用户信息')
req2 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/me',
    headers={'Authorization': f'Bearer {token}'}
)
r2 = urllib.request.urlopen(req2)
user = json.loads(r2.read())
print(f'✓ 用户: {user["username"]} ({user["nickname"]})')

# 3. 更新个人信息
print('\n3. 更新个人信息')
req3 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/profile',
    data=json.dumps({'nickname': 'Admin User', 'email': 'admin@nlp.com'}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
    method='PUT'
)
r3 = urllib.request.urlopen(req3)
updated = json.loads(r3.read())
print(f'✓ 更新成功: {updated["nickname"]}')

# 4. 修改密码
print('\n4. 修改密码')
req4 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/change-password',
    data=json.dumps({'current_password': 'admin123', 'new_password': 'newpass123'}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
    method='POST'
)
r4 = urllib.request.urlopen(req4)
print(f'✓ 密码修改: {r4.read().decode()}')

# 5. 用新密码重新登录
print('\n5. 用新密码重新登录')
data5 = json.dumps({'username': 'admin123', 'password': 'newpass123'}).encode()
req5 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/login',
    data=data5,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
r5 = urllib.request.urlopen(req5)
login5 = json.loads(r5.read())
token5 = login5['access_token']
print(f'✓ 新Token: {token5[:30]}...')

# 6. 获取API Keys
print('\n6. 获取API Keys')
req6 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/api-keys',
    headers={'Authorization': f'Bearer {token5}'}
)
r6 = urllib.request.urlopen(req6)
keys = json.loads(r6.read())
print(f'✓ API Keys: {len(keys)}个')

# 7. 创建API Key
print('\n7. 创建API Key')
req7 = urllib.request.Request(
    f'{BASE_URL}/api/v1/auth/api-keys',
    data=json.dumps({'name': 'My Key', 'permissions': 'predict,history', 'expires_in_days': 90}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token5}'},
    method='POST'
)
r7 = urllib.request.urlopen(req7)
new_key = json.loads(r7.read())
print(f'✓ 创建成功: {new_key["name"]}')
print(f'  完整密钥: {new_key["api_key"][:30]}...')

print('\n' + '=' * 60)
print('✓ 所有测试通过！')
print('=' * 60)
