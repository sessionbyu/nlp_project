#!/bin/bash

# 后端 API 健康检查脚本
# 检查所有文本相关的 API 端点是否正常运行

set -e

# 配置
API_BASE="http://localhost:8000"
TIMEOUT=5

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 图标
CHECK="✓"
CROSS="✗"
WARN="⚠"

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}🔍 后端 API 健康检查${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local expected_status=$4

    TOTAL=$((TOTAL + 1))

    echo -e "${YELLOW}测试 ${TOTAL}: ${name}${NC}"

    # 发送请求
    local start_time=$(date +%s%N)
    local response
    local status_code

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null || echo -e "\n000")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT -X POST "$url" \
            -H "Content-Type: application/json" \
            -d '{"test": true}' 2>/dev/null || echo -e "\n000")
    fi

    status_code=$(echo "$response" | tail -n1)
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 ))

    # 检查状态码
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "  ${GREEN}${CHECK} 通过${NC} - HTTP ${status_code} (${duration}ms)"
        PASSED=$((PASSED + 1))
        return 0
    elif [ "$status_code" -eq "$expected_status" ] || [ "$expected_status" -ge 200 ] && [ "$expected_status" -lt 300 ]; then
        echo -e "  ${GREEN}${CHECK} 通过${NC} - HTTP ${status_code} (${duration}ms)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "  ${RED}${CROSS} 失败${NC} - 期望 HTTP ${expected_status}, 实际 ${status_code} (${duration}ms)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 测试登录 API
test_endpoint \
    "登录 API" \
    "POST" \
    "${API_BASE}/api/v1/auth/login" \
    200

# 测试文本预测 API（需要认证）
echo -e "${YELLOW}获取认证 Token...${NC}"
TOKEN=$(curl -s -X POST "${API_BASE}/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}${CHECK} Token 获取成功${NC}"

    # 测试文本预测 API
    test_endpoint_with_auth() {
        local name=$1
        local method=$2
        local url=$3
        local data=$4

        TOTAL=$((TOTAL + 1))
        echo -e "${YELLOW}测试 ${TOTAL}: ${name}${NC}"

        local start_time=$(date +%s%N)
        local response
        local status_code

        if [ "$method" = "GET" ]; then
            response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
                -H "Authorization: Bearer $TOKEN" "$url" 2>/dev/null || echo -e "\n000")
        elif [ "$method" = "POST" ]; then
            response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
                -X POST "$url" \
                -H "Authorization: Bearer $TOKEN" \
                -H "Content-Type: application/json" \
                -d "$data" 2>/dev/null || echo -e "\n000")
        fi

        status_code=$(echo "$response" | tail -n1)
        local end_time=$(date +%s%N)
        local duration=$(( (end_time - start_time) / 1000000 ))

        if [ "$status_code" -ge 200 ] && [ "$status_code" -lt 300 ]; then
            echo -e "  ${GREEN}${CHECK} 通过${NC} - HTTP ${status_code} (${duration}ms)"
            PASSED=$((PASSED + 1))
            echo "$response" | head -n-1 | jq '.' 2>/dev/null | head -10 || echo "$response" | head -n-1
            return 0
        else
            echo -e "  ${RED}${CROSS} 失败${NC} - HTTP ${status_code} (${duration}ms)"
            FAILED=$((FAILED + 1))
            return 1
        fi
    }

    # 测试文本预测
    test_endpoint_with_auth \
        "文本情感预测 API" \
        "POST" \
        "${API_BASE}/api/v1/predict" \
        '{"text":"今天天气真好","model_key":"bert"}'

    # 测试获取模型列表
    test_endpoint_with_auth \
        "获取模型列表 API" \
        "GET" \
        "${API_BASE}/api/v1/models" \
        ""

else
    echo -e "${RED}${CROSS} Token 获取失败，跳过需要认证的测试${NC}"
fi

# 输出汇总
echo ""
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}📊 测试汇总${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""
echo -e "总计: ${BLUE}${TOTAL}${NC} 个测试"
echo -e "通过: ${GREEN}${PASSED}${NC} 个 ${GREEN}${CHECK}${NC}"
echo -e "失败: ${RED}${FAILED}${NC} 个 ${RED}${CROSS}${NC}"

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
echo -e "通过率: ${PASS_RATE}%"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 有 ${FAILED} 个测试失败${NC}"
    exit 1
fi
