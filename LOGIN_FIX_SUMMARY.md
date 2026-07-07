# 🔐 登录问题解决方案

## 问题原因

**根本原因**：数据库中没有创建任何用户，所以登录时总是返回 `401 (Unauthorized)` 和 `"Incorrect username or password"`。

### 为什么会这样？

- 项目使用了 PostgreSQL 数据库
- 数据库容器启动时是空的，没有预置用户数据
- 后端没有自动创建初始用户的逻辑
- 所以任何用户名/密码组合都会失败

---

## ✅ 已完成的修复

### 1. 创建管理员用户

已成功创建用户：
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "nickname": "管理员",
  "role": "user",
  "password": "admin123"
}
```

### 2. 测试登录成功

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","remember_me":false}'
```

返回：
```json
{
  "access_token": "...",
  "refresh_token": null,
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "nickname": "管理员",
    "role": "user"
  }
}
```

---

## 🎯 现在可以测试了

### 方法 1：直接在登录页登录

1. **打开无痕窗口**
2. 访问 `http://192.168.88.134:3000/login`
3. 输入用户名：`admin`
4. 输入密码：`admin123`
5. 点击登录

### 方法 2：查看控制台日志

登录后，在控制台会看到路由守卫日志：
```
[Router Guard] Path: /login
[Router Guard] Is Authenticated: false  ← 登录前
...
登录成功
...
[Router Guard] Path: /predict
[Router Guard] Is Authenticated: true   ← 登录后
[Router Guard] Root path detected, redirecting based on auth state
[Router Guard] Authenticated, redirecting to /predict
```

---

## 📋 完整的修复总结

### 问题 1：根路径重定向错误 ✅

**问题**：访问 `/` 直接跳到 `/predict`（即使未登录）

**修复**：
- 删除了重复的 `/` 路由配置
- 在路由守卫中统一处理根路径重定向
- 删除 AppLayout 内部的重复认证检查

**文件**：
- `frontend-vue/src/router/index.ts`
- `frontend-vue/src/components/layout/AppLayout.vue`

### 问题 2：认证状态无法清除 ✅

**问题**：清除 localStorage 后 `isAuthenticated` 仍为 true

**修复**：
- 将 `token` 和 `userInfo` 从惰性 ref 改为 computed refs
- 每次访问时从 storage 动态读取最新值

**文件**：
- `frontend-vue/src/stores/auth.ts`

### 问题 3：没有初始用户 ✅

**问题**：数据库为空，无法登录

**修复**：
- 创建管理员用户：`admin` / `admin123`

---

## 🔧 手动创建用户（如果需要）

如果需要创建更多用户或重置密码：

### 通过注册接口（推荐）

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "email": "your@email.com",
    "password": "your_password",
    "nickname": "你的昵称"
  }'
```

### 通过 Docker 进入容器（高级）

如果需要直接操作数据库：

```bash
# 进入 backend 容器
docker exec -it nlp_backend bash

# 使用 Python 创建用户（如果设置了 Django/Flask CLI）
# 或者直接操作数据库
```

---

## 🚀 访问地址

- **前端**：http://192.168.88.134:3000
- **后端 API**：http://192.168.88.134:8000
- **API 文档**：http://192.168.88.134:8000/docs

---

## 📝 测试账号

- **用户名**：`admin`
- **密码**：`admin123`

---

## ⚠️ 注意事项

1. **首次登录后**：访问 `/` 会跳转到 `/predict`（这是正常行为，说明已登录）
2. **未登录状态**：访问 `/` 会跳转到 `/login`（正确行为）
3. **清除数据**：使用 `http://192.168.88.134:3000/complete_clear_auth.html` 清除认证状态

---

## 🐛 如果还有问题

### 问题：还是跳转到 /predict

**解决方案**：
1. 完全关闭所有浏览器窗口
2. 重新打开无痕窗口
3. 清除所有认证数据（使用清除页面）
4. 强制刷新（Ctrl+Shift+R）

### 问题：登录失败 401

**检查**：
1. 确认用户名是 `admin`（不是 `admin123`）
2. 确认密码是 `admin123`
3. 后端服务是否运行：`curl http://localhost:8000/health`

### 问题：页面无法访问

**检查**：
1. Nginx 容器是否运行：`docker ps | grep frontend`
2. 后端容器是否运行：`docker ps | grep backend`
3. 数据库容器是否运行：`docker ps | grep db`

---

**创建时间**：2026-07-03
**状态**：✅ 已解决
