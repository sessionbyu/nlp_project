#!/bin/bash
# ==============================================
# NLP 域名配置 - 常用操作速查
# ==============================================

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║         NLP 域名配置 - 常用操作速查表                           ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 快速配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 自动化配置（推荐）
sudo bash nginx/setup-domain.sh

# 手动配置
sudo cp nginx/nlp-frontend.conf /etc/nginx/conf.d/
sudo vim /etc/nginx/conf.d/nlp-frontend.conf
sudo nginx -t && sudo systemctl reload nginx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Nginx 常用命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 测试配置
sudo nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看完整配置
sudo nginx -T

# 查看运行的进程
ps aux | grep nginx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 日志查看
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 访问日志
tail -f /var/log/nginx/nlp-frontend-access.log

# 错误日志
tail -f /var/log/nginx/nlp-frontend-error.log

# 通用错误日志
tail -f /var/log/nginx/error.log

# 查看最近错误
grep -i error /var/log/nginx/error.log | tail -20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 测试命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 测试 HTTP 访问
curl -I http://nlp.yourdomain.com

# 测试 HTTPS 访问
curl -I https://nlp.yourdomain.com

# 测试 API
curl https://nlp.yourdomain.com/api/health

# 测试域名解析
nslookup nlp.yourdomain.com
dig nlp.yourdomain.com

# 测试连接
telnet nlp.yourdomain.com 443
nc -zv nlp.yourdomain.com 443

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐳 Docker 命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 查看服务状态
docker-compose ps

# 查看前端日志
docker-compose logs -f frontend-vue

# 查看后端日志
docker-compose logs -f backend

# 重启前端
docker-compose restart frontend-vue

# 重启后端
docker-compose restart backend

# 重建前端
docker-compose up -d --build frontend-vue

# 停止所有服务
docker-compose down

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 SSL 证书命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d nlp.yourdomain.com

# 查看证书
sudo certbot certificates

# 测试证书续期
sudo certbot renew --dry-run

# 强制更新证书
sudo certbot renew --force-renewal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 诊断命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 检查端口监听
lsof -i :80
lsof -i :443
lsof -i :3000
lsof -i :8000

# 检查网络连接
netstat -tulpn | grep nginx
netstat -tulpn | grep 3000
netstat -tulpn | grep 8000

# 检查防火墙
sudo ufw status
sudo iptables -L -n

# 检查 DNS 解析
nslookup nlp.yourdomain.com
dig nlp.yourdomain.com
host nlp.yourdomain.com

# 检查 SSL 证书
openssl s_client -connect nlp.yourdomain.com:443
echo | openssl s_client -servername nlp.yourdomain.com -connect nlp.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💻 本地测试（hosts 文件）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Linux/Mac
sudo vim /etc/hosts
# 添加: 192.168.88.134   nlp.yourdomain.com

# Windows
notepad C:\Windows\System32\drivers\etc\hosts

# 刷新 DNS
sudo systemd-resolve --flush-caches
ipconfig /flushdns  # Windows

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 环境变量配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 编辑 .env 文件
vim .env

# 关键配置
VUE_FRONTEND_PORT=3000    # 前端端口
BACKEND_PORT=8000         # 后端端口
CORS_ORIGINS=...          # CORS 配置（域名配置后必须更新）

# 应用配置
docker-compose up -d

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 回滚操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 停止并删除配置
sudo rm /etc/nginx/conf.d/nlp-frontend.conf
sudo systemctl reload nginx

# 恢复备份
sudo cp /etc/nginx/conf.d/nlp-frontend.conf.bak.YYYYMMDDHHMMSS \
        /etc/nginx/conf.d/nlp-frontend.conf
sudo systemctl reload nginx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 文档速查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 查看详细指南
cat nginx/README.md

# 查看快速参考
cat nginx/QUICK_REF.md

# 查看配置总结
cat DOMAIN_CONFIG_SUMMARY.md

# 查看文件清单
cat NGINX_FILES_INDEX.md

# 查看架构说明
cat nginx/ARCHITECTURE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  常见问题快速修复
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 502 Bad Gateway
docker-compose restart frontend-vue backend

# 403 Forbidden
sudo chmod 755 /usr/share/nginx/html
sudo chown -R www-data:www-data /usr/share/nginx/html

# SSL 证书失败
sudo ufw allow 80
sudo ufw allow 443

# CORS 错误
# 更新 .env 中的 CORS_ORIGINS
vim .env
docker-compose restart backend

# DNS 无法解析
# 添加 hosts 记录
sudo vim /etc/hosts
# 192.168.88.134   nlp.yourdomain.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
