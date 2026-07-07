#!/bin/bash
# ==============================================
# 一键应用 HTTP 配置脚本（无需交互）
# ==============================================

echo "=========================================="
echo "应用 Nginx HTTP 配置"
echo "=========================================="
echo ""

# 配置路径
CONF_SRC="/home/user/nlp_project/nginx/nlp-http-only.conf"
CONF_DST="/etc/nginx/conf.d/nlp-frontend.conf"
BACKUP="/etc/nginx/conf.d/nlp-frontend.conf.bak.$(date +%Y%m%d%H%M%S)"

# 检查源文件
if [ ! -f "$CONF_SRC" ]; then
    echo "错误：源配置文件不存在: $CONF_SRC"
    exit 1
fi

# 备份现有配置
echo "1. 备份现有配置..."
if [ -f "$CONF_DST" ]; then
    cp "$CONF_DST" "$BACKUP"
    echo "   已备份到: $BACKUP"
else
    echo "   未找到现有配置，跳过备份"
fi

# 复制新配置
echo ""
echo "2. 应用 HTTP 配置..."
cp "$CONF_SRC" "$CONF_DST"
echo "   ✓ 配置已应用"

# 测试配置
echo ""
echo "3. 测试 nginx 配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "   ✓ 配置语法正确"

    # 重新加载 nginx
    echo ""
    echo "4. 重新加载 nginx..."
    systemctl reload nginx

    if [ $? -eq 0 ]; then
        echo "   ✓ Nginx 已重新加载"

        # 显示配置信息
        echo ""
        echo "=========================================="
        echo "✓ 配置成功！"
        echo "=========================================="
        echo ""
        echo "配置信息："
        grep "server_name" "$CONF_DST" | head -1 | sed 's/^/  域名: /'
        echo ""
        echo "测试命令："
        echo "  curl -I http://nlp.example.com"
        echo "  curl http://nlp.example.com/api/health"
        echo ""
        echo "查看日志："
        echo "  tail -f /var/log/nginx/nlp-frontend-access.log"
        echo ""
    else
        echo "   ✗ Nginx 重载失败"
        exit 1
    fi
else
    echo "   ✗ 配置语法错误"
    echo ""
    echo "恢复备份..."
    if [ -f "$BACKUP" ]; then
        cp "$BACKUP" "$CONF_DST"
        echo "   已恢复备份"
    fi
    exit 1
fi
