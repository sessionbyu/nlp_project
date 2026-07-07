#!/bin/bash
# ==============================================
# 修复 Nginx 配置 - 支持本地访问
# ==============================================

set -e

CONF_FILE="/etc/nginx/conf.d/nlp-frontend.conf"
BACKUP_FILE="/etc/nginx/conf.d/nlp-frontend.conf.bak.localhost.$(date +%Y%m%d%H%M%S)"

echo "=========================================="
echo "修复 Nginx 配置 - 支持本地访问"
echo "=========================================="
echo ""

# 检查文件存在
if [ ! -f "$CONF_FILE" ]; then
    echo "错误：配置文件不存在: $CONF_FILE"
    exit 1
fi

# 备份
echo "1. 备份当前配置..."
cp "$CONF_FILE" "$BACKUP_FILE"
echo "   已备份到: $BACKUP_FILE"

# 修改 server_name
echo ""
echo "2. 修改 server_name 配置..."
sed -i 's/server_name nlp.example.com;/server_name nlp.example.com localhost 127.0.0.1 _;/' "$CONF_FILE"
echo "   ✓ 已修改"

# 验证修改
echo ""
echo "3. 验证修改..."
grep "server_name" "$CONF_FILE"

# 测试配置
echo ""
echo "4. 测试 nginx 配置..."
nginx -t

# 重载 nginx
echo ""
echo "5. 重新加载 nginx..."
systemctl reload nginx

echo ""
echo "=========================================="
echo "✓ 修复完成！"
echo "=========================================="
echo ""
echo "现在支持以下访问方式："
echo "  http://localhost"
echo "  http://127.0.0.1"
echo "  http://$(hostname -I | awk '{print $1}')"
echo "  http://nlp.example.com（需要配置 hosts 或 DNS）"
echo ""
echo "测试命令："
echo "  curl -I http://localhost"
echo "  curl http://localhost/api/health"
echo ""
