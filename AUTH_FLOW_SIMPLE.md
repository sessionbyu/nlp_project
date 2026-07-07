# 🔐 登录和登出操作逻辑（简化版）

## 📊 一句话总结

**登录** = 输入账号密码 → 后端验证 → 生成 Token → 保存到浏览器 → 跳转到预测页

**登出** = 点击退出 → 清除 Token → 跳转到登录页

---

## 🔑 登录流程（7 步）

```
1. 用户在登录页输入账号密码
   ├─ 用户名: admin
   └─ 密码: admin123

2. 前端验证表单
   ├─ 用户名长度检查
   ├─ 密码长度检查
   └─ 验证通过才继续

3. 发送登录请求
   └─ POST /api/v1/auth/login
       ├─ username: admin
       ├─ password: admin123
       └─ remember_me: false/true

4. 后端处理登录
   ├─ 查找用户（用户名或邮箱）
   ├─ 验证密码（bcrypt）
   ├─ 检查账户状态
   ├─ 生成 Access Token (15分钟)
   └─ 生成 Refresh Token (7天，仅记住我时)

5. 返回响应
   └─ {
       access_token: "...",
       user: { id, username, email, role }
     }

6. 前端保存数据
   ├─ remember_me = true → localStorage
   └─ remember_me = false → sessionStorage

7. 跳转页面
   ├─ redirect=/ → /predict
   ├─ redirect=/predict → /predict
   └─ 无参数 → /predict
```

---

## 🚪 登出流程（4 步）

```
1. 用户点击右上角退出登录

2. 清除所有认证数据
   ├─ localStorage.removeItem('token')
   ├─ localStorage.removeItem('userInfo')
   ├─ sessionStorage.removeItem('token')
   └─ sessionStorage.removeItem('userInfo')

3. 更新 Store 状态
   └─ isAuthenticated = false

4. 跳转到登录页
   └─ /login
```

---

## 🛡️ 路由守卫检查（每次页面跳转时）

### 检查 1：访问根路径 `/`

```
访问 /
  ├─ 已登录？ → 是 → 跳转 /predict
  └─ 已登录？ → 否 → 跳转 /login?redirect=/
```

### 检查 2：访问受保护页面（如 /predict）

```
访问 /predict
  ├─ 已登录？ → 是 → 允许访问
  └─ 已登录？ → 否 → 跳转 /login?redirect=/predict
```

### 检查 3：已登录用户访问登录页

```
访问 /login（已登录状态）
  └─ 跳转 /predict（保护逻辑）
```

---

## 💾 Token 存储对比

| 特性 | localStorage | sessionStorage |
|------|-------------|----------------|
| **记住我 = true** | ✅ 保存到 localStorage | ❌ 清除 |
| **记住我 = false** | ❌ 清除 | ✅ 保存到 sessionStorage |
| **关闭浏览器后** | ✅ 仍然有效 | ❌ 自动清除 |
| **打开新标签页** | ✅ 保持登录 | ❌ 需要重新登录 |
| **手动清除** | localStorage.clear() | sessionStorage.clear() |

---

## 🔄 Token 生命周期

```
登录成功
  │
  ▼
生成 Token
  │
  ▼
保存到 Storage
  │
  ▼
每次请求自动添加到 Header
  │
  ├─ Authorization: Bearer <token>
  │
  ▼
Token 过期（15分钟后）
  │
  ▼
后端返回 401
  │
  ▼
前端自动登出
  │
  ▼
跳转到登录页
```

---

## 🚨 自动登出场景

### 场景 1：Token 过期
```
Token 过期
  → 请求返回 401
  → 前端自动清除 Token
  → 跳转到登录页
  → 提示"登录已过期，请重新登录"
```

### 场景 2：手动点击退出
```
点击退出登录
  → 清除所有 Storage
  → 跳转到 /login
```

### 场景 3：管理员删除账户
```
后端返回 403
  → 前端清除 Token
  → 跳转到登录页
```

---

## 🔐 请求头示例

### 登录请求
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123",
  "remember_me": false
}
```

### 认证请求（自动添加 Token）
```
GET /api/v1/history/recent
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 数据存储结构

### localStorage（记住我）

```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userInfo": "{\"id\":1,\"username\":\"admin\",\"nickname\":\"管理员\",\"roles\":[\"user\"],\"permissions\":[\"predict\",\"history\",...]}"
}
```

### sessionStorage（不记住我）

```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userInfo": "{\"id\":1,\"username\":\"admin\",\"nickname\":\"管理员\",\"roles\":[\"user\"],\"permissions\":[\"predict\",\"history\",...]}"
}
```

---

## 🧪 测试账号

```
用户名：admin
密码：admin123
```

---

## 📚 详细文档

如需了解更多细节，请查看完整版文档：`AUTH_FLOW_DETAILS.md`

---

**文档版本**：2026-07-03
**状态**：✅ 所有功能已修复并测试通过
