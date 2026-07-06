#!/bin/bash

# ==============================================
# NLP 项目 Nginx 域名配置脚本
# 自动化配置前端域名映射
# ==============================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "NLP 项目 Nginx 域名配置向导"
echo "=========================================="
echo ""

# 配置变量
NGINX_CONF_DIR="/etc/nginx/conf.d"
SITES_AVAILABLE="/etc/nginx/sites-available"
SITES_ENABLED="/etc/nginx/sites-enabled"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOCAL_CONF_DIR="$PROJECT_DIR/nginx"

# 检查权限
if [[ $EUID -ne 0 ]]; then
   echo "错误：此脚本需要 root 权限运行"
   echo "请使用: sudo bash nginx/setup-domain.sh"
   exit 1
fi

# 检查 nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo "Nginx 未安装，正在安装..."
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y nginx
    elif command -v yum &> /dev/null; then
        yum install -y nginx
    else
        echo "错误：无法自动安装 nginx，请手动安装"
        exit 1
    fi
fi

# 收集用户输入
read -p "请输入前端域名 (例如: nlp.example.com): " FRONTEND_DOMAIN
read -p "请输入 API 域名（可选，直接回车跳过）: " API_DOMAIN
read -p "前端端口 [3000]: " FRONTEND_PORT
FRONTEND_PORT=${FRONTEND_PORT:-3000}
read -p "后端 API 端口 [8000]: " BACKEND_PORT
BACKEND_PORT=${BACKEND_PORT:-8000}

# 验证域名格式
if ! [[ $FRONTEND_DOMAIN =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$ ]]; then
    echo "警告：域名格式可能不正确: $FRONTEND_DOMAIN"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "配置信息："
echo "  前端域名: $FRONTEND_DOMAIN"
echo "  API 域名: ${API_DOMAIN:-未设置}"
echo "  前端端口: $FRONTEND_PORT"
echo "  后端端口: $BACKEND_PORT"
echo ""

read -p "确认配置正确? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 生成 nginx 配置文件
CONFIG_FILE="$LOCAL_CONF_DIR/generated.conf"

cat > "$CONFIG_FILE" << EOF
# ==============================================
# NLP 项目 - 自动生成的 Nginx 配置
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# ==============================================

upstream nlp_backend {
    server 127.0.0.1:$BACKEND_PORT;
}

upstream nlp_frontend {
    server 127.0.0.1:$FRONTEND_PORT;
}

# HTTP -> HTTPS 重定向
server {
    listen 80;
    server_name $FRONTEND_DOMAIN${API_DOMAIN:+ $API_DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

# HTTPS - 前端
server {
    listen 443 ssl http2;
    server_name $FRONTEND_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$FRONTEND_DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;

    access_log /var/log/nginx/nlp-frontend-access.log;
    error_log /var/log/nginx/nlp-frontend-error.log;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|map)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # SPA 支持
    location / {
        proxy_pass http://nlp_frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 如果配置了 API 域名，添加 API 配置
if [[ -n "$API_DOMAIN" ]]; then
    cat >> "$CONFIG_FILE" << EOF

# HTTPS - API
server {
    listen 443 ssl http2;
    server_name $API_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$FRONTEND_DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header X-Content-Type-Options "nosniff" always;

    access_log /var/log/nginx/nlp-api-access.log;
    error_log /var/log/nginx/nlp-api-error.log;

    location / {
        proxy_pass http://nlp_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF
fi

echo "配置文件已生成: $CONFIG_FILE"
echo ""

# 询问是否应用配置
read -p "是否立即应用配置? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份现有配置
    if [ -f "$NGINX_CONF_DIR/nlp-frontend.conf" ]; then
        echo "备份现有配置..."
        cp "$NGINX_CONF_DIR/nlp-frontend.conf" "$NGINX_CONF_DIR/nlp-frontend.conf.bak.$(date +%Y%m%d%H%M%S)"
    fi

    # 复制配置
    echo "应用配置..."
    cp "$CONFIG_FILE" "$NGINX_CONF_DIR/nlp-frontend.conf"

    # 测试配置
    echo "测试 nginx 配置..."
    nginx -t

    if [ $? -eq 0 ]; then
        # 重新加载 nginx
        echo "重新加载 nginx..."
        systemctl reload nginx

        echo ""
        echo "=========================================="
        echo "✓ 配置成功！"
        echo "=========================================="
        echo ""
        echo "访问地址："
        echo "  前端: https://$FRONTEND_DOMAIN"
        if [[ -n "$API_DOMAIN" ]]; then
            echo "  API: https://$API_DOMAIN"
        fi
        echo ""
        echo "下一步："
        echo "1. 配置 DNS 解析将域名指向此服务器"
        echo "2. 获取 SSL 证书: certbot --nginx -d $FRONTEND_DOMAIN${API_DOMAIN:+ -d $API_DOMAIN}"
        echo "3. 更新 CORS_ORIGINS 环境变量"
        echo ""
    else
        echo "错误：nginx 配置测试失败！"
        exit 1
    fi
else
    echo "配置已生成，但未应用"
    echo "手动应用: sudo cp $CONFIG_FILE $NGINX_CONF_DIR/ && sudo nginx -t && sudo systemctl reload nginx"
fi
