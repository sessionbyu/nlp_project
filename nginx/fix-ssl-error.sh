#!/bin/bash
# ==============================================
# SSL 证书错误快速修复脚本
# ==============================================

echo "=========================================="
echo "Nginx SSL 证书错误修复"
echo "=========================================="
echo ""

# 检查当前配置
echo "检查当前配置..."
CURRENT_CONF="/etc/nginx/conf.d/nlp-frontend.conf"

if [ ! -f "$CURRENT_CONF" ]; then
    echo "✗ 未找到 nginx 配置文件: $CURRENT_CONF"
    exit 1
fi

# 检查是否包含 SSL 配置
if grep -q "ssl_certificate" "$CURRENT_CONF"; then
    echo "⚠ 检测到 SSL 配置，但证书文件不存在"
    echo ""
    echo "解决方案："
    echo "  1. 临时使用 HTTP 配置（快速测试）"
    echo "  2. 获取 SSL 证书（生产环境推荐）"
    echo ""

    read -p "请选择 (1/2): " choice

    case $choice in
        1)
            echo ""
            echo "应用 HTTP 配置..."
            sudo cp /home/user/nlp_project/nginx/nlp-http-only.conf "$CURRENT_CONF"
            sudo nginx -t && sudo systemctl reload nginx
            echo ""
            echo "✓ HTTP 配置已应用"
            echo "  访问地址: http://nlp.example.com"
            echo ""
            echo "后续可以随时切换到 HTTPS:"
            echo "  sudo cp nginx/nlp-complete.conf $CURRENT_CONF"
            echo "  sudo certbot --nginx -d nlp.example.com"
            ;;
        2)
            echo ""
            echo "准备获取 SSL 证书..."
            read -p "确认域名已解析到服务器? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "获取 SSL 证书..."
                sudo apt-get install -y certbot python3-certbot-nginx
                sudo certbot --nginx -d nlp.example.com

                if [ $? -eq 0 ]; then
                    echo ""
                    echo "✓ SSL 证书获取成功！"
                    sudo nginx -t && sudo systemctl reload nginx
                else
                    echo ""
                    echo "✗ SSL 证书获取失败"
                    echo "请检查："
                    echo "  1. 域名 DNS 解析是否正确"
                    echo "  2. 80/443 端口是否开放"
                    echo "  3. 防火墙设置"
                fi
            else
                echo "已取消，先配置 DNS 解析后再试"
            fi
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
else
    echo "✓ 当前配置未使用 SSL"
    sudo nginx -t
fi
