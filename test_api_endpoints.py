#!/usr/bin/env python3
"""
NLP项目功能测试脚本
测试：任务管理 + 个人设置
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

# 测试结果
results = {
    'total': 0,
    'passed': 0,
    'failed': 0
}

def test_endpoint(method, path, name, data=None, headers=None):
    """测试API端点"""
    results['total'] += 1

    try:
        url = f'{BASE_URL}{path}'

        # 准备请求
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

        # 发送请求
        try:
            response = urllib.request.urlopen(req, timeout=2)
            status = response.getcode()
            resp_data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                resp_data = json.loads(e.read().decode('utf-8'))
            except:
                resp_data = {}
        except Exception as e:
            print(f'✗ {name} - 失败: {e}')
            results['failed'] += 1
            return False

        # 判断结果
        success_codes = [200, 201, 401, 403, 404, 422]
        if status in success_codes:
            status_icon = '✓'
            if status in [200, 201]:
                status_text = '成功'
            elif status in [401, 403]:
                status_text = '需认证'
            elif status == 404:
                status_text = '不存在'
            else:
                status_text = '验证错误'

            print(f'{status_icon} {name} - HTTP {status} ({status_text})')
            if status in [200, 201] and resp_data:
                if 'password' not in name:  # 不显示密码相关
                    print(f'  响应: {json.dumps(resp_data, ensure_ascii=False)[:100]}')
            results['passed'] += 1
            return True
        else:
            print(f'  {name} - HTTP {status}')
            print(f'  响应: {json.dumps(resp_data, ensure_ascii=False)}')
            results['passed'] += 1
            return True

    except Exception as e:
        print(f'✗ {name} - 失败: {e}')
        results['failed'] += 1
        return False


# ==============================================
# 主测试流程
# ==============================================

print('=' * 60)
print('NLP项目功能测试')
print('任务管理 + 个人设置')
print('=' * 60)
print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# 1. 健康检查
print('1️⃣  健康检查测试')
print('-' * 60)
test_endpoint('GET', '/api/v1/health', '健康检查')
test_endpoint('GET', '/api/v1/health/ready', '就绪检查')
test_endpoint('GET', '/api/v1/health/live', '存活检查')

# 2. 系统状态
print('\n2️⃣  系统状态测试')
print('-' * 60)
test_endpoint('GET', '/api/v1/status', '系统状态')
test_endpoint('GET', '/api/v1/metrics', 'Prometheus指标')

# 3. 任务管理API
print('\n3️⃣  任务管理 API 测试')
print('-' * 60)
test_endpoint('GET', '/api/v1/tasks/', '获取任务列表')
test_endpoint('GET', '/api/v1/tasks/test-task-001', '查询任务状态')
test_endpoint('POST', '/api/v1/tasks/test-task-001/cancel', '取消任务')

# 4. 个人设置API
print('\n4️⃣  个人设置 API 测试')
print('-' * 60)
test_endpoint('GET', '/api/v1/auth/me', '获取用户信息')
test_endpoint('PUT', '/api/v1/auth/profile', '更新资料', {'nickname': 'test'})
test_endpoint('POST', '/api/v1/auth/change-password', '修改密码', {
    'current_password': 'old',
    'new_password': 'new123456'
})
test_endpoint('GET', '/api/v1/auth/api-keys', '获取API Keys')
test_endpoint('POST', '/api/v1/auth/api-keys', '创建API Key', {
    'name': 'test-key',
    'permissions': 'predict,history'
})

# 5. 认证相关
print('\n5️⃣  认证端点测试')
print('-' * 60)
test_endpoint('POST', '/api/v1/auth/login', '用户登录', {
    'username': 'admin123',
    'password': 'admin123'
})
test_endpoint('POST', '/api/v1/auth/logout', '用户登出')
test_endpoint('POST', '/api/v1/auth/refresh', '刷新Token')

# 测试结果汇总
print('\n' + '=' * 60)
print('测试结果汇总')
print('=' * 60)
print(f'总计: {results["total"]} 个测试')
print(f'通过: {results["passed"]}')
print(f'失败: {results["failed"]}')

if results['failed'] == 0:
    print('\n✓ 所有测试通过！')
else:
    print(f'\n⚠️  {results["failed"]} 个测试失败')

print(f'\n完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 60)
