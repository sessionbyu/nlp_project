# Nginx Docker Compose 集成总结

## ✅ 已完成的集成

### 📁 创建的文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `nginx/nginx.conf` | 统一 Nginx 配置文件 | ✅ 新建 |
| `docker-compose.yml` | 已集成 Nginx 服务 | ✅ 已更新 |
| `.env` | 环境变量（已添加 Nginx 配置） | ✅ 已更新 |
| `.env.example` | 环境变量模板 | ✅ 新建 |
| `logs/nginx/` | Nginx 日志目录 | ✅ 已创建 |

---

## 🏗️ Docker Compose 配置

### 服务架构

```yaml
services:
  # 统一入口（新增）
  nginx:
    image: nginx:alpine
    ports:
      - "${NGINX_HTTP_PORT:-80}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      backend:
        condition: service_healthy
      frontend-vue:
        condition: service_started

  # 后端服务（保持不变）
  backend:
    image: ...
    ports:
      - "${BACKEND_PORT}:8000"  # 内部网络也可通过 Nginx 访问

  # 前端服务（已更新）
  frontend-vue:
    expose:
      - "80"  # 只暴露给内部网络
    # 移除了 ports 映射，通过 Nginx 统一访问
```

### 关键变化

#### 1. 新增 Nginx 服务

```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"  # 统一入口端口
```

#### 2. 前端服务更新

**修改前：**
```yaml
frontend-vue:
  ports:
    - "${VUE_FRONTEND_PORT:-3000}:80"  # 直接暴露给主机
```

**修改后：**
```yaml
frontend-vue:
  expose:
    - "80"  # 只暴露给内部 Docker 网络
```

**原因：**
- ✅ 统一入口，便于管理
- ✅ 隐藏内部服务细节
- ✅ 方便添加负载均衡
- ✅ 提升安全性

---

## 🔄 请求流程

### 通过 Nginx 访问

```
用户 → http://localhost
     → Nginx (80)
     ├─→ /api/* → backend:8000
     └─→ /*     → frontend-vue:80
```

### API 请求示例

```bash
# 通过 Nginx 代理访问后端
curl http://localhost/api/v1/models

# 等同于直接访问后端
curl http://localhost:8000/api/v1/models
```

---

## 📊 Nginx 配置功能

### 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 反向代理 | 前端 + 后端统一入口 | ✅ |
| 静态资源缓存 | 1年缓存，减少请求 | ✅ |
| Gzip 压缩 | 自动压缩文本资源 | ✅ |
| WebSocket 支持 | proxy_set_header Upgrade | ✅ |
| 健康检查 | /nginx-health 端点 | ✅ |
| SPA 路由 | try_files 支持 | ✅ |

### 代理规则

| 路径 | 代理目标 | 说明 |
|------|---------|------|
| `/api/*` | `http://backend:8000/` | 后端 API |
| `/health` | `http://backend:8000/` | 后端健康检查 |
| `/nginx-health` | Nginx 直接响应 | Nginx 健康检查 |
| `/*` | `http://frontend-vue:80/` | 前端应用 |

---

## 🚀 使用指南

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps

# 期望输出
# Name              Command               State           Ports
# -----------------------------------------------------------------
# nlp_nginx         nginx -g daemon off;  Up      0.0.0.0:80->80/tcp
# nlp_backend       uvicorn app.main:app   Up      8000/tcp
# nlp_frontend_vue  nginx -g daemon off;  Up      80/tcp
```

### 访问服务

```bash
# 前端应用
http://localhost

# 后端 API
http://localhost/api/v1/models
http://localhost/api/v1/predict

# 健康检查
http://localhost/nginx-health   # Nginx
http://localhost/health         # 后端（通过 Nginx 代理）
```

### 查看日志

```bash
# Nginx 访问日志
tail -f logs/nginx/access.log

# Nginx 错误日志
tail -f logs/nginx/error.log

# Docker 日志
docker-compose logs -f nginx
```

---

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置：

```bash
# Nginx HTTP 端口
NGINX_HTTP_PORT=80

# Nginx HTTPS 端口（可选）
# NGINX_HTTPS_PORT=443

# 后端端口
BACKEND_PORT=8000

# 前端端口（内部使用）
VUE_FRONTEND_PORT=3000
```

### 自定义配置

#### 修改端口

```bash
# .env 文件
NGINX_HTTP_PORT=8080

# 重启服务
docker-compose down
docker-compose up -d
```

#### 启用 HTTPS

1. 准备 SSL 证书
2. 取消 `nginx.conf` 中 HTTPS 配置的注释
3. 取消 `docker-compose.yml` 中 HTTPS 端口的注释
4. 重启服务

---

## 🧪 测试验证

### 健康检查

```bash
# Nginx 健康检查
curl http://localhost/nginx-health
# 输出: healthy

# 后端健康检查（通过 Nginx）
curl http://localhost/health

# API 测试
curl http://localhost/api/v1/models
```

### 性能测试

```bash
# 使用 wrk 测试
docker run --rm -it williamyeh/wrk \
  -t12 -c100 -d30s \
  http://localhost/

# 查看结果
# 应该看到稳定在 10000+ req/s
```

---

## 🐛 故障排查

### Nginx 无法启动

```bash
# 检查端口占用
netstat -tulpn | grep :80

# 检查配置语法
docker-compose exec nginx nginx -t

# 查看日志
docker-compose logs nginx
```

### 502 Bad Gateway

```bash
# 检查后端服务
docker-compose ps backend
docker-compose logs backend

# 检查网络
docker-compose exec nginx ping backend
```

### 静态资源加载失败

```bash
# 检查文件存在
docker-compose exec nginx ls -la /usr/share/nginx/html/

# 检查 Nginx 日志
tail -f logs/nginx/error.log
```

---

## 📈 优势

### 相比直接访问

| 特性 | 直接访问 | 通过 Nginx |
|------|---------|-----------|
| 统一入口 | ❌ 多个端口 | ✅ 单一入口 |
| SSL 终止 | ❌ 需要配置每个服务 | ✅ 只需配置 Nginx |
| 负载均衡 | ❌ 不支持 | ✅ 支持 |
| 静态资源缓存 | ❌ 依赖服务 | ✅ 统一管理 |
| Gzip 压缩 | ❌ 需要单独配置 | ✅ 统一配置 |
| WebSocket | ❌ 需要单独配置 | ✅ 自动支持 |
| 安全防护 | ❌ 需要单独实现 | ✅ 可统一配置 |
| 日志聚合 | ❌ 分散 | ✅ 统一收集 |

---

## 🔐 安全建议

### 1. 隐藏 Nginx 版本

```nginx
# 在 http 块中添加
server_tokens off;
```

### 2. 限制请求大小

```nginx
client_max_body_size 10M;
```

### 3. 配置速率限制

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://nlp_backend/;
}
```

### 4. IP 白名单（管理后台）

```nginx
location /api/v1/admin/ {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://nlp_backend/;
}
```

---

## 📚 相关文档

- **Docker Compose 配置**：`docker-compose.yml`
- **Nginx 配置**：`nginx/nginx.conf`
- **环境变量**：`.env` 和 `.env.example`
- **Nginx 使用指南**：`nginx/README.md`
- **前端文档**：`frontend-vue/README.md`
- **后端文档**：`backend/README.md`

---

## 🎯 下一步

1. ✅ **启动服务**
   ```bash
   docker-compose up -d
   ```

2. ✅ **测试访问**
   ```bash
   curl http://localhost/nginx-health
   ```

3. ✅ **配置域名**（可选）
   - 参考 `nginx/README.md` 中的域名配置指南

4. ✅ **启用 HTTPS**（生产环境）
   - 参考 `nginx/README.md` 中的 SSL 配置指南

---

**状态**: ✅ Nginx 集成完成
**最后更新**: 2026-07-04
