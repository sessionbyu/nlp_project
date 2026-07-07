# NLP 域名配置架构说明

## 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         用户浏览器 (User)                            │
│                https://nlp.yourdomain.com                           │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ HTTPS (443)
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                   主机 Nginx (Host Nginx)                            │
│  - SSL 证书管理 (Let's Encrypt)                                      │
│  - 反向代理                                                           │
│  - 静态资源缓存                                                       │
│  - Gzip 压缩                                                         │
│  - HTTP/2 支持                                                       │
└──┬──────────────────────────┬───────────────────────────────────────┘
   │                          │
   │ proxy_pass               │ proxy_pass /api/
   │                          │
┌──▼──────────────────┐   ┌───▼────────────────────────────────────────┐
│  前端服务 (Frontend) │   │  后端服务 (Backend)                        │
│  Docker Container   │   │  Docker Container                          │
│  Port: 3000         │   │  Port: 8000                                │
│  Vue 3 + Element    │   │  FastAPI + Python                          │
│                     │   │                                            │
│  - SPA 路由         │   │  - 情感分析预测                             │
│  - 静态资源         │   │  - 历史记录管理                             │
│  - API 调用         │   │  - 统计分析                                 │
│                     │   │  - 批量处理                                 │
│                     │   │  - 任务队列                                 │
└─────────────────────┘   └────────────────────────────────────────────┘
```

## 请求流程

### 1. 用户访问 https://nlp.yourdomain.com

```
用户浏览器
  ↓
主机 Nginx (443端口)
  ↓ SSL 卸载
  ↓ 反向代理
前端 Docker 容器 (3000端口)
  ↓
返回 index.html + 静态资源
  ↓
用户浏览器
```

### 2. 前端发起 API 请求

```
用户浏览器
  ↓ GET /api/v1/predict
主机 Nginx
  ↓ 识别 /api/ 路径
  ↓ 代理到后端
后端 Docker 容器 (8000端口)
  ↓ FastAPI 处理
  ↓ 返回 JSON 数据
  ↓
前端接收数据并渲染
```

### 3. API 独立域名访问（可选）

```
用户浏览器
  ↓
https://api.nlp.yourdomain.com
  ↓
主机 Nginx
  ↓ 代理到后端
后端服务
```

## 配置方案对比

### 方案一：主机 Nginx（推荐）

```
用户 → 主机Nginx → Docker前端 → 后端
     (443/80)    (3000)      (8000)

优点：
✅ 性能最好（减少一层 Docker 网络）
✅ 配置简单
✅ 易于管理和监控
✅ SSL 证书管理方便

缺点：
❌ 与主机共享网络栈
```

### 方案二：Docker Nginx

```
用户 → DockerNginx → Docker前端 → 后端
     (443/80)      (80)        (8000)

优点：
✅ 完全容器化
✅ 环境隔离性好
✅ 易于迁移和部署

缺点：
❌ 多一层网络转发
❌ SSL 证书管理稍复杂
❌ 需要额外的 Docker 卷管理
```

## 流量路径详解

### 静态资源（JS/CSS/图片）

```
1. 用户请求 https://nlp.yourdomain.com/app.js
2. Nginx 接收请求
3. 检查是否匹配静态资源规则
4. 代理到前端容器
5. 前端容器返回静态文件
6. Nginx 设置缓存头并返回
7. 用户浏览器缓存 1 年
```

### API 请求

```
1. 用户请求 https://nlp.yourdomain.com/api/v1/predict
2. Nginx 接收请求
3. 识别 /api/ 路径
4. 代理到后端容器 http://backend:8000
5. 后端处理并返回 JSON
6. Nginx 转发给用户
```

### SPA 路由

```
1. 用户访问 https://nlp.yourdomain.com/statistics
2. Nginx 接收请求
3. 后端没有 /statistics 文件
4. Nginx 返回 /index.html
5. Vue Router 处理前端路由
6. 显示统计页面
```

## SSL/TLS 流程

```
1. Let's Encrypt 验证域名所有权
   └─ 访问 http://nlp.yourdomain.com/.well-known/acme-challenge/xxx
   └─ Nginx 返回验证文件
   └─ 验证成功

2. 证书获取
   └─ certbot 保存证书到 /etc/letsencrypt/live/nlp.yourdomain.com/

3. HTTPS 访问
   └─ 用户发起 HTTPS 请求
   └─ Nginx 提供 SSL 证书
   └─ 浏览器验证证书
   └─ 建立加密连接
```

## 安全配置

### Nginx 安全头

```nginx
Strict-Transport-Security    # 强制 HTTPS
X-Content-Type-Options       # 防止 MIME 类型嗅探
X-Frame-Options             # 防止点击劫持
X-XSS-Protection            # XSS 过滤
Referrer-Policy             # 引用策略
```

### CORS 配置

```python
# backend/app/core/config.py
CORS_ORIGINS = [
    "https://nlp.yourdomain.com",
    "https://api.nlp.yourdomain.com"
]
```

### 网络隔离

```yaml
# docker-compose.yml
networks:
  backend:
    driver: bridge
    internal: true  # 内网隔离
```

## 监控和日志

```
Nginx 日志
├── /var/log/nginx/nlp-frontend-access.log    # 前端访问日志
├── /var/log/nginx/nlp-frontend-error.log     # 前端错误日志
└── /var/log/nginx/nlp-api-access.log         # API 访问日志（可选）

Docker 日志
├── docker-compose logs nlp_backend
├── docker-compose logs nlp_frontend_vue
└── docker-compose logs nlp_nginx
```

## 扩展建议

### 高可用部署

```
用户 → 负载均衡器 (LB)
       ├── Nginx 服务器 1
       ├── Nginx 服务器 2
       └── Nginx 服务器 3
```

### CDN 加速

```
用户 → CDN (Cloudflare/AWS CloudFront)
       ↓ 缓存静态资源
       源站 Nginx
```

### WAF 防护

```
用户 → WAF (Web Application Firewall)
       ↓ 过滤恶意请求
       Nginx
```

## 性能指标

### 预期性能

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 首屏加载时间 | < 2s | 3G 网络 |
| API 响应时间 | < 100ms | 本地网络 |
| 并发用户数 | 100+ | 单服务器 |
| SSL 握手时间 | < 50ms | TLS 1.3 |
| 静态资源加载 | < 500ms | 已缓存 |

### 监控指标

```bash
# Nginx 连接数
nginx -T | grep connections

# 请求速率
tail -f /var/log/nginx/access.log | awk '{print $4}' | uniq -c

# 错误率
tail -f /var/log/nginx/error.log | grep -c "error"
```

---

更多详细信息请参考：
- [详细架构文档](https://github.com/your-repo/wiki/architecture)
- [Nginx 官方文档](http://nginx.org/en/docs/)
- [部署指南](DEPLOYMENT_GUIDE.md)
