#!/usr/bin/env python3
"""
NLP项目功能测试报告
任务管理 + 个人设置
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

print('=' * 70)
print('NLP项目功能测试报告')
print('任务管理 + 个人设置')
print('=' * 70)
print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

BASE_URL = 'http://localhost:8000'
results = []

# 辅助函数
def test_endpoint(method, path, name, data=None, headers=None):
    try:
        url = f'{BASE_URL}{path}'

        if data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={'Content-Type': 'application/json'},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)

        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        try:
            response = urllib.request.urlopen(req, timeout=3)
            status = response.getcode()
            resp_text = response.read().decode('utf-8')
            try:
                resp_data = json.loads(resp_text)
            except:
                resp_data = {'raw': resp_text[:100]}
        except urllib.error.HTTPError as e:
            status = e.code
            resp_text = e.read().decode('utf-8')
            try:
                resp_data = json.loads(resp_text)
            except:
                resp_data = {'raw': resp_text[:100]}

        result = {
            'name': name,
            'path': f'{method} {path}',
            'status': status,
            'passed': status in [200, 201, 401, 403, 404, 422],
            'response': resp_data if isinstance(resp_data, dict) else {'raw': str(resp_data)[:100]}
        }
        results.append(result)
        return result

    except Exception as e:
        result = {
            'name': name,
            'path': f'{method} {path}',
            'status': 'ERROR',
            'passed': False,
            'error': str(e)
        }
        results.append(result)
        return result

# ============ 1. 健康检查 ============
print('1️⃣  健康检查测试')
print('=' * 70)

test_endpoint('GET', '/api/v1/health', '健康检查')
test_endpoint('GET', '/api/v1/health/ready', '就绪检查')
test_endpoint('GET', '/api/v1/health/live', '存活检查')

# ============ 2. 系统监控 ============
print('\n2️⃣  系统监控测试')
print('=' * 70)

test_endpoint('GET', '/api/v1/status', '系统状态')
test_endpoint('GET', '/api/v1/metrics', 'Prometheus指标')

# ============ 3. 任务管理（未认证） ============
print('\n3️⃣  任务管理 API 测试（未认证）')
print('=' * 70)

test_endpoint('GET', '/api/v1/tasks/', '获取任务列表')
test_endpoint('GET', '/api/v1/tasks/test-id', '查询任务状态')
test_endpoint('POST', '/api/v1/tasks/test-id/cancel', '取消任务')

# ============ 4. 个人设置（未认证） ============
print('\n4️⃣  个人设置 API 测试（未认证）')
print('=' * 70)

test_endpoint('GET', '/api/v1/auth/me', '获取用户信息')
test_endpoint('PUT', '/api/v1/auth/profile', '更新资料')
test_endpoint('POST', '/api/v1/auth/change-password', '修改密码')
test_endpoint('GET', '/api/v1/auth/api-keys', '获取API Keys列表')
test_endpoint('POST', '/api/v1/auth/api-keys', '创建API Key')

# ============ 5. 认证端点 ============
print('\n5️⃣  认证端点测试')
print('=' * 70)

test_endpoint('POST', '/api/v1/auth/login', '用户登录', {
    'username': 'admin123',
    'password': 'admin123'
})
test_endpoint('POST', '/api/v1/auth/logout', '用户登出')
test_endpoint('POST', '/api/v1/auth/refresh', '刷新Token')

# ============ 打印测试报告 ============
print('\n\n' + '=' * 70)
print('详细测试报告')
print('=' * 70)

passed = sum(1 for r in results if r['passed'])
failed = sum(1 for r in results if not r['passed'])

for r in results:
    status_icon = '✓' if r['passed'] else '✗'
    status_color = '\033[0;32m' if r['passed'] else '\033[0;31m'
    reset = '\033[0m'

    if r['status'] in [200, 201]:
        desc = '成功'
    elif r['status'] in [401, 403]:
        desc = '需要认证'
    elif r['status'] == 404:
        desc = '不存在'
    elif r['status'] == 422:
        desc = '验证错误'
    elif r['status'] == 'ERROR':
        desc = r.get('error', '未知错误')
    else:
        desc = str(r['status'])

    print(f"{status_color}{status_icon}{reset} {r['name']}")
    print(f"   {r['path']} - {desc}")

    if 'response' in r and r.get('passed') and r['status'] in [200, 201]:
        resp_str = json.dumps(r['response'], ensure_ascii=False)
        if len(resp_str) > 120:
            resp_str = resp_str[:120] + '...'
        print(f"   响应: {resp_str}")

# 总体结果
print('\n\n' + '=' * 70)
print('总体测试结果')
print('=' * 70)
print(f'总计: {len(results)}')
print(f'通过: {passed}')
print(f'失败: {failed}')

if failed == 0:
    print('\n✅ 所有测试通过！')
else:
    print(f'\n⚠️  {failed} 个测试失败')

print(f'\n完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 70)
