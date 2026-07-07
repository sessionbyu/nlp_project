# Nginx 配置指南

本目录包含 NLP 项目的 Nginx 配置文件，用于统一入口、反向代理和负载均衡。

## 📋 目录结构

```
nginx/
├── README.md              # 本文件
├── nginx.conf             # 统一配置文件（Docker Compose 集成）
├── nginx-docker.conf      # Docker 简单配置
├── nlp-simple.conf        # 简单配置（无 SSL，适合本地测试）
├── nlp-frontend.conf      # 前端域名配置（需手动修改域名）
├── nlp-complete.conf      # 完整配置（前端 + API 域名 + SSL）
├── setup-domain.sh        # 自动化配置脚本
└── generated.conf         # 自动生成的配置（运行脚本后创建）
```

## 🚀 快速开始

### 方案一：Docker Compose 集成（推荐）

#### 1. 启动服务

```bash
# 启动所有服务（包括 Nginx）
docker-compose up -d

# 或只启动 Nginx 和相关服务
docker-compose up -d nginx backend frontend-vue
```

#### 2. 访问服务

```
http://localhost              # 通过 Nginx 访问前端
http://localhost/api/v1/models # 通过 Nginx 访问后端 API
http://localhost/nginx-health  # Nginx 健康检查
```

#### 3. 配置说明

- **Nginx 端口**：80（HTTP），443（HTTPS，可选）
- **后端服务**：`http://backend:8000`（内部网络）
- **前端服务**：`http://frontend-vue:80`（内部网络）
- **环境变量**：`.env` 文件中的 `NGINX_HTTP_PORT`

### 方案二：使用自动化脚本（宿主机 Nginx）

```bash
# 1. 进入项目目录
cd /home/user/nlp_project

# 2. 运行配置脚本
sudo bash nginx/setup-domain.sh

# 3. 按照提示输入域名信息
```

### 方案三：手动配置（宿主机 Nginx）

#### 1. 复制配置文件

```bash
# 备份现有配置
sudo cp /etc/nginx/conf.d/nlp-frontend.conf /etc/nginx/conf.d/nlp-frontend.conf.bak

# 复制新配置
sudo cp nginx/nlp-frontend.conf /etc/nginx/conf.d/
```

#### 2. 修改域名

编辑 `/etc/nginx/conf.d/nlp-frontend.conf`，将 `nlp.yourdomain.com` 改为你的实际域名。

#### 3. 测试并应用

```bash
# 测试配置
sudo nginx -t

# 应用配置
sudo systemctl reload nginx
```

## 配置说明

### 环境要求

- **Nginx**: 已安装并运行
- **Docker**: NLP 项目服务正在运行
- **端口**: 前端端口 3000，后端端口 8000（与 docker-compose.yml 中的配置一致）

### 端口映射确认

检查 `.env` 文件中的端口配置：

```bash
VUE_FRONTEND_PORT=3000   # 前端端口
BACKEND_PORT=8000        # 后端端口
```

### 域名配置方式

#### 方式一：DNS 解析（生产环境）

在域名服务商处添加 A 记录：

```
类型: A
主机记录: nlp
记录值: <你的服务器IP>
TTL: 600
```

#### 方式二：本地 hosts 文件（本地测试）

```bash
# Linux/Mac
sudo vim /etc/hosts

# Windows
notepad C:\Windows\System32\drivers\etc\hosts
```

添加以下行：

```
127.0.0.1   nlp.localhost
# 或
192.168.88.134   nlp.yourdomain.com
```

## SSL/HTTPS 配置

### 使用 Let's Encrypt（推荐）

```bash
# 1. 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d nlp.yourdomain.com -d api.nlp.yourdomain.com

# 3. 证书会自动续期
```

### 使用自有证书

编辑 nginx 配置，修改以下路径：

```nginx
ssl_certificate /path/to/your/fullchain.pem;
ssl_certificate_key /path/to/your/privkey.pem;
```

## 后端 API 配置

### 方式一：通过前端域名代理

前端请求 `/api/*` 会自动代理到后端，无需修改前端配置。

### 方式二：独立 API 域名

使用 `nlp-complete.conf`，配置独立的 API 域名（如 `api.nlp.yourdomain.com`）。

### 方式三：修改前端配置

如果前端需要直接访问后端，修改 `.env` 文件：

```bash
# .env 文件
VITE_API_BASE_URL=https://api.nlp.yourdomain.com
```

然后重新构建前端：

```bash
cd frontend-vue
npm run build
docker-compose up -d --build frontend-vue
```

## 更新 CORS 配置

域名配置后，需要更新后端 CORS 允许的源：

编辑 `.env` 文件：

```bash
CORS_ORIGINS=http://localhost:3000,https://nlp.yourdomain.com,https://api.nlp.yourdomain.com
```

重启后端服务：

```bash
docker-compose restart backend
```

## 常见问题

### 1. 502 Bad Gateway

**原因**: 后端服务未运行或端口错误

**解决**:

```bash
# 检查服务状态
docker-compose ps

# 检查端口
netstat -tulpn | grep 3000
netstat -tulpn | grep 8000
```

### 2. 403 Forbidden

**原因**: nginx 配置的静态资源权限问题

**解决**: 检查文件权限，确保 nginx 可以读取

### 3. 404 Not Found (SPA 路由)

**原因**: SPA 路由配置缺失

**解决**: 确保配置中包含 `try_files $uri $uri/ /index.html;` 或使用 `location /` 代理。

### 4. WebSocket 连接失败

**原因**: WebSocket 代理配置缺失

**解决**: 确保 nginx 配置包含：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 5. SSL 证书获取失败

**原因**: 域名未解析到服务器或防火墙未开放 80/443 端口

**解决**:

```bash
# 检查端口
sudo ufw allow 80
sudo ufw allow 443

# 检查 DNS
nslookup nlp.yourdomain.com
```

## 性能优化

### 启用 Gzip 压缩

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml application/atom+xml image/svg+xml;
```

### 启用 HTTP/2

已在配置中启用（`listen 443 ssl http2;`）

### 静态资源 CDN

可将静态资源上传到 CDN，修改前端构建配置。

## 监控和日志

### 查看访问日志

```bash
tail -f /var/log/nginx/nlp-frontend-access.log
```

### 查看错误日志

```bash
tail -f /var/log/nginx/nlp-frontend-error.log
```

### 监控 nginx 状态

```bash
systemctl status nginx
nginx -t
```

## 参考文档

- [Nginx 官方文档](http://nginx.org/en/docs/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
