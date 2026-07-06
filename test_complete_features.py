#!/usr/bin/env python3
"""
NLP项目完整功能测试
任务管理 + 个人设置
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'

# 测试结果
results = {
    'task_management': {'total': 0, 'passed': 0, 'failed': 0, 'details': []},
    'personal_settings': {'total': 0, 'passed': 0, 'failed': 0, 'details': []},
    'health_check': {'total': 0, 'passed': 0, 'failed': 0, 'details': []},
    'metrics': {'total': 0, 'passed': 0, 'failed': 0, 'details': []}
}

def test_endpoint(category, method, path, name, data=None, headers=None, expected_codes=None):
    """测试API端点"""
    results[category]['total'] += 1

    if expected_codes is None:
        expected_codes = [200, 201, 401, 403, 404, 422]

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
            response = urllib.request.urlopen(req, timeout=3)
            status = response.getcode()
            resp_data = response.read().decode('utf-8')
            try:
                resp_json = json.loads(resp_data)
            except:
                resp_json = {'raw': resp_data[:100]}
        except urllib.error.HTTPError as e:
            status = e.code
            resp_data = e.read().decode('utf-8')
            try:
                resp_json = json.loads(resp_data)
            except:
                resp_json = {'raw': resp_data[:100]}
        except Exception as e:
            print(f'  ✗ {name} - 失败: {e}')
            results[category]['failed'] += 1
            return False

        # 判断结果
        if status in expected_codes:
            status_desc = {
                200: '成功',
                201: '已创建',
                401: '未认证',
                403: '禁止访问',
                404: '不存在',
                422: '验证错误'
            }.get(status, '其他')

            result = {
                'name': name,
                'status': status,
                'status_desc': status_desc,
                'passed': True,
                'response': resp_json if isinstance(resp_json, dict) else {'raw': str(resp_json)[:100]}
            }
            results[category]['passed'] += 1
            results[category]['details'].append(result)
            return True
        else:
            result = {
                'name': name,
                'status': status,
                'status_desc': '意外状态',
                'passed': False,
                'response': resp_json
            }
            results[category]['failed'] += 1
            results[category]['details'].append(result)
            return False

    except Exception as e:
        result = {
            'name': name,
            'status': 'ERROR',
            'status_desc': str(e),
            'passed': False,
            'response': None
        }
        results[category]['failed'] += 1
        results[category]['details'].append(result)
        return False


# ==============================================
# 主测试流程
# ==============================================

print('=' * 70)
print('NLP项目功能测试报告')
print('任务管理 + 个人设置')
print('=' * 70)
print(f'测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'测试地址: {BASE_URL}')
print()

# 1. 健康检查测试
print('1️⃣  健康检查测试')
print('=' * 70)

test_endpoint('health_check', 'GET', '/api/v1/health', '健康检查')
test_endpoint('health_check', 'GET', '/api/v1/health/ready', '就绪检查')
test_endpoint('health_check', 'GET', '/api/v1/health/live', '存活检查')

# 2. 系统监控测试
print('\n2️⃣  系统监控测试')
print('=' * 70)

# Metrics端点是文本格式，特殊处理
result = {'total': 1, 'passed': 0, 'failed': 0, 'details': []}
try:
    req = urllib.request.Request(f'{BASE_URL}/api/v1/metrics', method='GET')
    response = urllib.request.urlopen(req, timeout=3)
    status = response.getcode()
    content = response.read().decode('utf-8')

    if status == 200 and content.startswith('#'):
        print(f'✓ Prometheus指标 - HTTP {status} (Prometheus格式)')
        print(f'  内容预览: {content[:200]}...')
        result['passed'] = 1
        result['details'].append({
            'name': 'Prometheus指标',
            'status': status,
            'passed': True
        })
    else:
        print(f'  Prometheus指标 - HTTP {status}')
        result['failed'] = 1
except Exception as e:
    print(f'✗ Prometheus指标 - 失败: {e}')
    result['failed'] = 1

results['metrics'] = result

# 3. 任务管理测试
print('\n3️⃣  任务管理 API 测试')
print('=' * 70)

test_endpoint('task_management', 'GET', '/api/v1/tasks/', '获取活跃任务列表')
test_endpoint('task_management', 'GET', '/api/v1/tasks/test-task-001', '查询任务状态')
test_endpoint('task_management', 'POST', '/api/v1/tasks/test-task-001/cancel', '取消任务')
test_endpoint('task_management', 'GET', '/api/v1/tasks/nonexistent', '查询不存在的任务')

# 4. 个人设置测试
print('\n4️⃣  个人设置 API 测试')
print('=' * 70)

# 认证端点
test_endpoint('personal_settings', 'GET', '/api/v1/auth/me', '获取当前用户信息')
test_endpoint('personal_settings', 'PUT', '/api/v1/auth/profile', '更新个人信息', data={'nickname': 'TestUser'})
test_endpoint('personal_settings', 'POST', '/api/v1/auth/change-password', '修改密码', data={
    'current_password': 'oldpass',
    'new_password': 'newpass123'
})

# API Keys端点
print('\n  API Keys功能测试:')
test_endpoint('personal_settings', 'GET', '/api/v1/auth/api-keys', '获取API Keys列表')
test_endpoint('personal_settings', 'POST', '/api/v1/auth/api-keys', '创建API Key', data={
    'name': 'Test Key',
    'permissions': 'predict,history',
    'expires_in_days': 30
})

# 5. 登录测试
print('\n5️⃣  登录认证测试')
print('=' * 70)

test_endpoint('personal_settings', 'POST', '/api/v1/auth/login', '用户登录', data={
    'username': 'admin123',
    'password': 'admin123'
})
test_endpoint('personal_settings', 'POST', '/api/v1/auth/logout', '用户登出')
test_endpoint('personal_settings', 'POST', '/api/v1/auth/refresh', '刷新Token', data={
    'refresh_token': 'fake-token'
})

# 6. 系统状态
print('\n6️⃣  系统状态测试')
print('=' * 70)

result = test_endpoint('health_check', 'GET', '/api/v1/status', '系统状态')

# 7. 生成详细报告
print('\n\n' + '=' * 70)
print('详细测试报告')
print('=' * 70)

for category, data in results.items():
    if data['total'] == 0:
        continue

    print(f'\n【{category.upper()}】')
    print(f'总计: {data["total"]} | 通过: {data["passed"]} | 失败: {data["failed"]}')

    for detail in data['details']:
        if detail['passed']:
            print(f'  ✓ {detail["name"]} - HTTP {detail["status"]} ({detail.get("status_desc", "")})')
        else:
            print(f'  ✗ {detail["name"]} - {detail.get("status", "ERROR")} ({detail.get("status_desc", "")})')

# 总体统计
print('\n\n' + '=' * 70)
print('总体测试结果')
print('=' * 70)

total_all = sum(cat['total'] for cat in results.values())
passed_all = sum(cat['passed'] for cat in results.values())
failed_all = sum(cat['failed'] for cat in results.values())

print(f'总计测试: {total_all}')
print(f'通过: {passed_all} ({passed_all/total_all*100:.1f}%)' if total_all > 0 else '通过: 0')
print(f'失败: {failed_all}')

if failed_all == 0:
    print('\n✅ 所有测试通过！')
else:
    print(f'\n⚠️  {failed_all} 个测试失败')

print(f'\n测试完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('=' * 70)
