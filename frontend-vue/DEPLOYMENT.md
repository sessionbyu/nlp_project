# Vue 3 前端 - 部署指南

## 📋 部署前检查

### 检查清单

- [ ] 后端 API 已部署并正常运行
- [ ] Node.js 18+ 已安装（用于本地构建）
- [ ] Docker 已安装（用于容器部署）
- [ ] Nginx 已安装（用于 Nginx 部署）

## 🚀 部署方案

### 方案 1: 直接部署（推荐测试）

#### 步骤 1: 构建项目

```bash
cd /home/user/nlp_project/frontend-vue

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 步骤 2: 启动本地服务器

```bash
# 使用任何静态文件服务器
npx serve -s dist -l 3000
```

或使用 Python:
```bash
cd dist
python3 -m http.server 3000
```

访问 http://localhost:3000

---

### 方案 2: Nginx 部署（推荐生产）

#### 步骤 1: 构建项目

```bash
cd /home/user/nlp_project/frontend-vue
npm install
npm run build
```

#### 步骤 2: 复制到 Nginx 目录

```bash
sudo cp -r dist/* /var/www/nlp-frontend/
```

#### 步骤 3: 配置 Nginx

创建配置文件 `/etc/nginx/sites-available/nlp-frontend`:

```nginx
server {
    listen 80;
    server_name 192.168.88.134;

    root /var/www/nlp-frontend;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

启用站点:
```bash
sudo ln -s /etc/nginx/sites-available/nlp-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

访问 http://192.168.88.134

---

### 方案 3: Docker 部署（推荐容器化）

#### 步骤 1: 构建镜像

```bash
cd /home/user/nlp_project/frontend-vue

# 开发环境镜像
docker build -t nlp-frontend:dev -f Dockerfile.dev .

# 生产环境镜像
docker build -t nlp-frontend:prod -f Dockerfile.prod .
```

#### 步骤 2: 运行容器

```bash
# 开发环境
docker run -d -p 3000:3000 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  nlp-frontend:dev

# 生产环境
docker run -d -p 80:80 \
  -e VITE_API_BASE_URL=http://192.168.88.134:8000 \
  nlp-frontend:prod
```

访问 http://localhost:80

---

### 方案 4: Docker Compose 部署（推荐集群）

在 `docker-compose.yml` 添加:

```yaml
frontend-vue:
  build:
    context: ./frontend-vue
    dockerfile: Dockerfile.prod
  ports:
    - "80:80"
  depends_on:
    - backend
  environment:
    - VITE_API_BASE_URL=http://backend:8000
  networks:
    - backend
```

启动:
```bash
docker-compose up -d frontend-vue
```

---

## 🔄 更新部署

### Nginx 部署更新

```bash
cd /home/user/nlp_project/frontend-vue
npm run build
sudo cp -r dist/* /var/www/nlp-frontend/
sudo systemctl reload nginx
```

### Docker 部署更新

```bash
# 重新构建
docker build -t nlp-frontend:prod -f Dockerfile.prod .

# 停止旧容器
docker stop nlp-frontend

# 删除旧容器
docker rm nlp-frontend

# 启动新容器
docker run -d -p 80:80 \
  -e VITE_API_BASE_URL=http://192.168.88.134:8000 \
  nlp-frontend:prod
```

### Docker Compose 更新

```bash
docker-compose up -d --build frontend-vue
```

## 📝 环境配置

### 开发环境 (.env.development)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
```

### 生产环境 (.env.production)

```env
VITE_API_BASE_URL=http://192.168.88.134:8000
VITE_API_TIMEOUT=10000
```

## 🔧 故障排查

### 问题 1: 页面空白

**原因**: 路由配置错误或资源加载失败

**解决**:
```bash
# 检查浏览器控制台
# 检查 Network 标签页
# 确认 API 地址正确
```

### 问题 2: API 请求失败

**原因**: CORS 或 API 地址错误

**解决**:
- 检查 `VITE_API_BASE_URL`
- 确认后端已启动
- 检查浏览器控制台的错误信息

### 问题 3: Docker 构建失败

**原因**: Node 镜像拉取失败

**解决**:
```bash
# 配置 Docker 镜像加速器
sudo nano /etc/docker/daemon.json
# 添加 registry-mirrors
sudo systemctl restart docker
```

### 问题 4: Nginx 502 错误

**原因**: 后端服务未启动或配置错误

**解决**:
```bash
# 检查后端状态
curl http://localhost:8000/health

# 检查 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

## 📊 性能优化

### 1. Gzip 压缩

已在 `nginx.conf` 中配置。验证:
```bash
curl -H "Accept-Encoding: gzip" -I http://localhost
```

### 2. 静态资源缓存

已在 `nginx.conf` 中配置。验证:
```bash
curl -I http://localhost/assets/
```

### 3. CDN 加速

将静态资源上传到 CDN:
- 阿里云 CDN
- 腾讯云 CDN
- Cloudflare

### 4. HTTP/2

在 Nginx 配置中添加:
```nginx
listen 443 ssl http2;
```

## 🔒 安全建议

1. **HTTPS**: 配置 SSL 证书
2. **CORS**: 后端配置正确的 CORS 头
3. **CSP**: 配置 Content-Security-Policy
4. **Rate Limiting**: Nginx 限流配置

## 📈 监控

### 健康检查

```bash
# 应用健康检查
curl http://localhost/health

# Nginx 状态
sudo systemctl status nginx

# Docker 容器状态
docker ps
```

### 日志查看

```bash
# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# Docker 日志
docker logs nlp-frontend
```

## 🔄 备份

### 备份构建产物

```bash
tar -czf nlp-frontend-backup-$(date +%Y%m%d).tar.gz /var/www/nlp-frontend/
```

### 备份 Nginx 配置

```bash
sudo cp /etc/nginx/sites-available/nlp-frontend /etc/nginx/sites-available/nlp-frontend.backup
```

## 📞 支持

如有问题，请查看:
- Vue 3 官方文档: https://vuejs.org/
- Element Plus 文档: https://element-plus.org/
- Vite 文档: https://vitejs.dev/

---

**版本**: 1.0.0
**最后更新**: 2026-06-28
