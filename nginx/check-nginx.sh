#!/bin/bash

# ==============================================
# NLP 项目 Nginx 配置检查脚本
# ==============================================

echo "=========================================="
echo "NLP 项目 Nginx 配置检查"
echo "=========================================="
echo ""

# 检查 nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo "✗ Nginx 未安装"
    exit 1
else
    echo "✓ Nginx 已安装: $(nginx -v 2>&1)"
fi

# 检查 nginx 服务状态
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx 服务正在运行"
else
    echo "✗ Nginx 服务未运行"
fi

echo ""
echo "检查配置文件..."

# 检查项目配置
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONF_DIR="$PROJECT_DIR/nginx"

for conf in nlp-simple.conf nlp-frontend.conf nlp-complete.conf; do
    if [ -f "$CONF_DIR/$conf" ]; then
        echo "✓ 找到配置文件: $conf"
    fi
done

echo ""
echo "检查 nginx 配置目录..."

# 检查系统配置
if [ -d "/etc/nginx/conf.d" ]; then
    echo "✓ /etc/nginx/conf.d/ 存在"

    if [ -f "/etc/nginx/conf.d/nlp-frontend.conf" ]; then
        echo "  ✓ nlp-frontend.conf 已部署"

        # 检查配置语法
        if nginx -t 2>&1 | grep -q "successful"; then
            echo "  ✓ 配置语法正确"
        else
            echo "  ✗ 配置语法错误"
            nginx -t
        fi
    else
        echo "  ✗ nlp-frontend.conf 未部署"
    fi
fi

echo ""
echo "检查服务端口..."

# 检查前端服务
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tulpn 2>/dev/null | grep -q ':3000 '; then
    echo "✓ 前端服务运行在端口 3000"
else
    echo "⚠ 前端服务未检测到在端口 3000 运行"
    echo "  请确保 docker-compose up 正在运行"
fi

# 检查后端服务
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tulpn 2>/dev/null | grep -q ':8000 '; then
    echo "✓ 后端服务运行在端口 8000"
else
    echo "⚠ 后端服务未检测到在端口 8000 运行"
fi

echo ""
echo "检查 Docker 服务..."

if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "✓ Docker 服务正在运行"
    docker-compose ps
else
    echo "✗ Docker 服务未运行"
fi

echo ""
echo "检查域名解析..."

# 尝试解析配置的域名
SERVER_NAME=$(grep -oP 'server_name\s+\K[^;]+' /etc/nginx/conf.d/nlp-frontend.conf 2>/dev/null | head -1)
if [ -n "$SERVER_NAME" ]; then
    echo "配置的域名: $SERVER_NAME"
    if host "$SERVER_NAME" &>/dev/null; then
        echo "✓ 域名解析成功: $(host $SERVER_NAME | grep 'has address' | awk '{print $4}')"
    else
        echo "⚠ 域名无法解析"
        echo "  请在 /etc/hosts 或 DNS 中添加解析"
    fi
fi

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 如果配置未部署，运行: sudo bash nginx/setup-domain.sh"
echo "2. 如果配置有错误，查看日志: sudo tail -f /var/log/nginx/error.log"
echo "3. 测试访问: curl http://localhost/nginx-health"
echo ""
