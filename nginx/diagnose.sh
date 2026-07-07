#!/bin/bash
# ==============================================
# Nginx 配置诊断脚本
# ==============================================

echo "=========================================="
echo "Nginx 配置诊断"
echo "=========================================="
echo ""

echo "1. 检查 Nginx 配置中的 server_name"
echo "----------------------------------------"
grep -H "server_name" /etc/nginx/conf.d/nlp-frontend.conf 2>/dev/null || echo "未找到配置文件"
echo ""

echo "2. 检查 Nginx 配置中的 location /api/"
echo "----------------------------------------"
grep -A 10 "location /api" /etc/nginx/conf.d/nlp-frontend.conf 2>/dev/null || echo "未找到 /api/ 配置"
echo ""

echo "3. 测试后端健康检查接口"
echo "----------------------------------------"
echo "测试: curl http://127.0.0.1:8000/health"
curl -s http://127.0.0.1:8000/health
echo ""
echo ""

echo "4. 测试前端首页"
echo "----------------------------------------"
echo "测试: curl -s http://127.0.0.1:3000 | head -5"
curl -s http://127.0.0.1:3000 | head -5
echo "..."
echo ""

echo "5. 检查当前 Nginx 服务监听"
echo "----------------------------------------"
sudo ss -tulpn | grep ':80' || echo "Nginx 未在监听 80 端口"
echo ""

echo "6. 查看 Nginx 错误日志"
echo "----------------------------------------"
if [ -f /var/log/nginx/nlp-frontend-error.log ]; then
    echo "最近的错误："
    tail -10 /var/log/nginx/nlp-frontend-error.log
else
    echo "未找到日志文件"
fi
echo ""

echo "7. 查看 Nginx 访问日志"
echo "----------------------------------------"
if [ -f /var/log/nginx/nlp-frontend-access.log ]; then
    echo "最近的访问："
    tail -10 /var/log/nginx/nlp-frontend-access.log
else
    echo "未找到日志文件"
fi
echo ""

echo "8. 查看所有 Nginx 配置"
echo "----------------------------------------"
sudo nginx -T 2>&1 | head -100
echo ""

echo "=========================================="
echo "诊断完成"
echo "=========================================="
