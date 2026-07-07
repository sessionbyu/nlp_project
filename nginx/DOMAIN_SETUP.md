# NLP 前端 Nginx 域名映射配置总结

## ✅ 已完成的工作

### 1. 创建了完整的 Nginx 配置文件

#### 方案一：主机 Nginx（推荐）
- **`nginx/nlp-frontend.conf`** - 基础域名配置
- **`nginx/nlp-complete.conf`** - 完整配置（前端 + API 域名 + SSL）
- **`nginx/nlp-simple.conf`** - 简单配置（适合本地测试）

#### 方案二：Docker Nginx（容器化部署）
- **`nginx/nginx-docker.conf`** - Docker nginx 配置
- **`docker-compose.nginx.yml`** - 完整的 docker-compose 配置

### 2. 创建了自动化工具

- **`nginx/setup-domain.sh`** - 交互式配置脚本，自动化部署
- **`nginx/check-nginx.sh`** - 配置检查脚本

### 3. 创建了完整文档

- **`nginx/README.md`** - 详细配置指南
- **`nginx/QUICK_REF.md`** - 快速参考手册

## 📦 当前项目状态

### 端口配置
- **前端端口**：3000（可通过 `.env` 中的 `VUE_FRONTEND_PORT` 修改）
- **后端端口**：8000（可通过 `.env` 中的 `BACKEND_PORT` 修改）
- **后端内网地址**：`http://backend:8000`（Docker 内部服务名）

### 现有配置
- Docker 容器中的 nginx 已配置反向代理
- 前端容器内 nginx 监听 80 端口
- Docker 映射：`<host-port>:3000` → `container-port:80`

## 🚀 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
cd /home/user/nlp_project
sudo bash nginx/setup-domain.sh
```

按提示输入域名，脚本将自动完成配置。

### 方法二：手动配置

```bash
# 1. 复制配置到 nginx 目录
sudo cp nginx/nlp-frontend.conf /etc/nginx/conf.d/

# 2. 编辑配置，修改域名
sudo vim /etc/nginx/conf.d/nlp-frontend.conf
# 将 nlp.yourdomain.com 改为你的域名

# 3. 测试并应用
sudo nginx -t && sudo systemctl reload nginx
```

## 📝 配置域名示例

假设你要使用域名 `nlp.example.com`：

### 1. 修改 nginx 配置

```nginx
server {
    listen 80;
    server_name nlp.example.com;  # ← 改为你的域名
    ...
}
```

### 2. 配置 DNS 解析

在域名服务商处添加 A 记录：

```
类型：A
主机记录：nlp
记录值：<你的服务器IP>
```

### 3. 本地测试（可选）

修改 `/etc/hosts`：

```
127.0.0.1   nlp.example.com
```

### 4. 获取 SSL 证书

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d nlp.example.com
```

### 5. 更新 CORS 配置

编辑 `.env`：

```bash
CORS_ORIGINS=http://localhost:3000,https://nlp.example.com
```

重启后端：

```bash
docker-compose restart backend
```

## 🔧 支持的配置场景

### 场景一：单域名（前端 + API）

```
https://nlp.example.com          # 前端
https://nlp.example.com/api/*    # API 代理
```

**配置**：使用 `nlp-frontend.conf`

### 场景二：双域名（前端 + API 独立）

```
https://nlp.example.com          # 前端
https://api.nlp.example.com      # API
```

**配置**：使用 `nlp-complete.conf`

### 场景三：本地测试（无 SSL）

```
http://nlp.localhost:80          # 本地测试
```

**配置**：使用 `nlp-simple.conf`

## 📚 文件清单

```
/home/user/nlp_project/
├── nginx/
│   ├── README.md              # 详细配置文档
│   ├── QUICK_REF.md           # 快速参考
│   ├── nlp-frontend.conf      # 基础域名配置
│   ├── nlp-complete.conf      # 完整配置（含 API 域名）
│   ├── nlp-simple.conf        # 简单配置（无 SSL）
│   ├── nginx-docker.conf      # Docker nginx 配置
│   ├── nginx-docker.conf.example
│   ├── setup-domain.sh        # 自动化配置脚本 ⭐
│   ├── check-nginx.sh         # 配置检查脚本
│   └── generated.conf         # 自动生成（运行脚本后）
└── docker-compose.nginx.yml   # Docker nginx 服务配置
```

## 🎯 下一步操作

1. **选择配置方案**（推荐：方案一 + 自动化脚本）
2. **运行配置脚本**：`sudo bash nginx/setup-domain.sh`
3. **配置 DNS 解析**：将域名指向服务器 IP
4. **获取 SSL 证书**：`sudo certbot --nginx -d <你的域名>`
5. **更新 CORS 配置**：在 `.env` 中添加新域名
6. **重启后端服务**：`docker-compose restart backend`
7. **测试访问**：`https://<你的域名>`

## ❓ 常见问题

### Q: 需要修改哪些配置？
A: 只需要修改域名，其他配置可以直接使用。

### Q: SSL 证书必须吗？
A: 生产环境强烈建议使用，本地测试可跳过。

### Q: 会中断服务吗？
A: 不会，nginx 配置重载是热重载，不中断现有连接。

### Q: 如何回滚？
A: 删除 `/etc/nginx/conf.d/nlp-frontend.conf` 并重载 nginx。

### Q: 支持多域名吗？
A: 支持，在 `server_name` 中添加多个域名即可。

## 📞 获取帮助

- 查看详细文档：`cat nginx/README.md`
- 运行检查脚本：`bash nginx/check-nginx.sh`
- 查看快速参考：`cat nginx/QUICK_REF.md`

---

**配置时间估算**：5-15 分钟（取决于 SSL 证书获取速度）

**难度等级**：⭐⭐ 简单

**推荐指数**：⭐⭐⭐⭐⭐
