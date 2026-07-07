# NLP 前端域名映射快速参考

## 📋 目录

- [快速开始](#快速开始)
- [三种方案对比](#三种方案对比)
- [配置文件说明](#配置文件说明)
- [常见命令](#常见命令)
- [故障排查](#故障排查)

---

## 快速开始

### 方式一：主机 Nginx + 自动化脚本（推荐）⭐

```bash
# 1. 运行配置向导
sudo bash nginx/setup-domain.sh

# 2. 按提示输入域名

# 3. 配置 DNS 解析

# 4. 获取 SSL 证书
sudo certbot --nginx -d nlp.yourdomain.com
```

### 方式二：主机 Nginx + 手动配置

```bash
# 1. 复制配置
sudo cp nginx/nlp-frontend.conf /etc/nginx/conf.d/

# 2. 修改域名
sudo vim /etc/nginx/conf.d/nlp-frontend.conf
# 将 nlp.yourdomain.com 改为你的域名

# 3. 测试并应用
sudo nginx -t && sudo systemctl reload nginx
```

### 方式三：Docker Nginx（隔离部署）

```bash
# 1. 复制配置
cp nginx/nginx-docker.conf nginx/nginx-docker.conf
# 修改其中的域名

# 2. 使用专门的 docker-compose
docker-compose -f docker-compose.nginx.yml up -d nginx
```

---

## 三种方案对比

| 特性 | 方案一：主机 Nginx | 方案二：主机 Nginx（手动） | 方案三：Docker Nginx |
|------|------------------|----------------------|-------------------|
| 难度 | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 复杂 |
| 灵活性 | ⭐⭐⭐ 高 | ⭐⭐⭐ 高 | ⭐⭐ 中等 |
| 隔离性 | ⭐⭐ 中等 | ⭐⭐ 中等 | ⭐⭐⭐ 高 |
| 适用场景 | 推荐所有场景 | 已有 nginx 配置 | 容器化部署 |
| SSL 支持 | ✅ | ✅ | ✅ |
| 性能 | ⭐⭐⭐ 高 | ⭐⭐⭐ 高 | ⭐⭐ 中等 |

**推荐**：方案一（自动化脚本），适合绝大多数场景。

---

## 配置文件说明

### nginx/nlp-frontend.conf
- **用途**：主机 nginx 域名配置（需手动修改域名）
- **适用**：主机 nginx 环境

### nginx/nlp-complete.conf
- **用途**：完整配置（前端 + API 域名 + SSL）
- **适用**：生产环境、需要独立 API 域名

### nginx/nlp-simple.conf
- **用途**：简单配置（无 SSL，适合本地测试）
- **适用**：本地开发、测试环境

### nginx/nginx-docker.conf
- **用途**：Docker nginx 配置
- **适用**：Docker 容器化部署

### docker-compose.nginx.yml
- **用途**：包含 nginx 服务的完整 docker-compose
- **适用**：方案三的配套文件

---

## 常见命令

### Nginx 基础命令

```bash
# 测试配置
sudo nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 重启 nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看配置
sudo nginx -T

# 查看运行中的配置
ps aux | grep nginx
```

### 日志查看

```bash
# 访问日志
tail -f /var/log/nginx/nlp-frontend-access.log

# 错误日志
tail -f /var/log/nginx/nlp-frontend-error.log

# 通用错误日志
tail -f /var/log/nginx/error.log
```

### 测试域名解析

```bash
# 测试域名解析
nslookup nlp.yourdomain.com
dig nlp.yourdomain.com

# 测试 HTTP 访问
curl -I http://nlp.yourdomain.com

# 测试 HTTPS 访问
curl -I https://nlp.yourdomain.com

# 测试 API
curl http://nlp.yourdomain.com/api/health
```

### Docker 相关

```bash
# 检查服务状态
docker-compose ps

# 查看前端日志
docker-compose logs -f frontend-vue

# 重启前端
docker-compose restart frontend-vue

# 重建前端
docker-compose up -d --build frontend-vue
```

---

## 故障排查

### 502 Bad Gateway

**原因**：后端服务未运行或端口错误

```bash
# 检查服务
docker-compose ps

# 检查端口
lsof -i :3000
lsof -i :8000

# 检查配置
grep proxy_pass /etc/nginx/conf.d/nlp-frontend.conf
```

### 403 Forbidden

**原因**：权限问题

```bash
# 检查文件权限
ls -la /usr/share/nginx/html/

# 检查 nginx 用户
ps aux | grep nginx
```

### 404 Not Found

**原因**：SPA 路由未配置

**解决**：确保配置中有 `try_files` 或 `location /` 代理

### SSL 证书错误

**原因**：证书未获取或配置错误

```bash
# 重新获取证书
sudo certbot certonly --nginx -d nlp.yourdomain.com

# 检查证书
sudo certbot certificates

# 测试续期
sudo certbot renew --dry-run
```

### 域名无法解析

**原因**：DNS 未配置或 hosts 文件错误

```bash
# 本地测试：修改 /etc/hosts
sudo vim /etc/hosts

# 添加：
# 127.0.0.1   nlp.yourdomain.com
# 或
# 192.168.88.134   nlp.yourdomain.com

# 刷新 DNS
sudo systemd-resolve --flush-caches
```

### WebSocket 连接失败

**原因**：WebSocket 代理配置缺失

**解决**：确保 nginx 配置包含：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

---

## 端口映射

当前项目默认端口：

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| Frontend | 80 | 3000 | Vue 前端 |
| Backend | 8000 | 8000 | FastAPI 后端 |
| Redis | 6379 | - | 仅内部访问 |
| PostgreSQL | 5432 | - | 仅内部访问 |

**修改端口**：编辑 `.env` 文件中的 `VUE_FRONTEND_PORT` 或 `BACKEND_PORT`

---

## 环境变量

关键配置（`.env` 文件）：

```bash
# 端口
VUE_FRONTEND_PORT=3000    # 前端端口
BACKEND_PORT=8000         # 后端端口

# CORS 配置（域名配置后必须更新）
CORS_ORIGINS=http://localhost:3000,https://nlp.yourdomain.com

# 其他配置...
```

---

## 下一步

1. ✅ 选择配置方案
2. ✅ 应用 nginx 配置
3. ✅ 配置 DNS 解析
4. ✅ 获取 SSL 证书（生产环境）
5. ✅ 更新 CORS 配置
6. ✅ 测试访问

---

## 参考文档

- 详细指南：[nginx/README.md](README.md)
- Nginx 官方文档：http://nginx.org/en/docs/
- Let's Encrypt：https://letsencrypt.org/docs/
