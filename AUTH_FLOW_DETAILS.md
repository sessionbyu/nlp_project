# 🔐 登录和登出操作逻辑详解

## 📋 目录

1. [登录流程](#登录流程)
2. [登出流程](#登出流程)
3. [路由守卫认证检查](#路由守卫认证检查)
4. [Token 管理](#token-管理)
5. [数据存储](#数据存储)
6. [流程图](#流程图)

---

## 登录流程

### 1️⃣ 前端：用户输入凭证

**文件**：`frontend-vue/src/views/LoginView.vue`

#### 步骤 1.1：用户填写表单
```vue
<el-form :model="form" :rules="rules">
  <el-form-item label="用户名" prop="username">
    <el-input v-model="form.username" />
  </el-form-item>
  <el-form-item label="密码" prop="password">
    <el-input v-model="form.password" type="password" />
  </el-form-item>
  <el-checkbox v-model="form.rememberMe">记住我</el-checkbox>
</el-form>
```

**用户输入**：
- `username`: `admin`
- `password`: `admin123`
- `rememberMe`: `false` 或 `true`

---

#### 步骤 1.2：表单验证
```typescript
await formRef.value.validate(async (valid) => {
  if (!valid) return
  // 验证通过后才继续
})
```

**验证规则**：
- 用户名：必填，长度 3-20 字符
- 密码：必填，长度 6-20 字符

---

#### 步骤 1.3：调用 AuthStore.login()
```typescript
await authStore.login({
  username: form.username,
  password: form.password,
  rememberMe: form.rememberMe,
})
```

---

### 2️⃣ 前端：AuthStore 处理登录

**文件**：`frontend-vue/src/stores/auth.ts`

#### 步骤 2.1：发送登录请求
```typescript
async function login(params: LoginParams) {
  loading.value = true
  try {
    // 调用 API
    const response = await loginApi(params)
    // loginApi 会发送 POST 请求到 /api/v1/auth/login
  }
}
```

**API 请求**：
- **URL**: `POST /api/v1/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "username": "admin",
  "password": "admin123",
  "remember_me": false
}
```

---

### 3️⃣ 后端：处理登录请求

**文件**：`backend/app/api/v1/auth.py`

#### 步骤 3.1：查找用户
```python
@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    # 查找用户（支持用户名或邮箱）
    result = await session.execute(
        select(User).where(
            (User.username == data.username) | (User.email == data.username),
            User.is_deleted == False,
        )
    )
    user = result.scalar_one_or_none()
```

**查询条件**：
- 用户名匹配 OR 邮箱匹配
- 用户未删除（`is_deleted = False`）

---

#### 步骤 3.2：验证密码
```python
if not user or not verify_password(data.password, user.hashed_password):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )
```

**密码验证**：
- 使用 bcrypt 验证：`bcrypt.checkpw(password.encode(), hashed_password.encode())`
- 失败 → 返回 401

---

#### 步骤 3.3：检查用户状态
```python
if not user.is_active:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is disabled",
    )
```

**检查项**：
- 账户是否激活（`is_active = True`）

---

#### 步骤 3.4：更新最后登录时间
```python
from datetime import datetime
user.last_login = datetime.utcnow()
await session.commit()
```

---

#### 步骤 3.5：生成 Token
```python
# 生成 Access Token（15分钟过期）
access_token = create_access_token(
    data={"sub": str(user.id), "role": user.role}
)

# 如果选择了"记住我"，生成 Refresh Token（7天过期）
refresh_token = None
if data.remember_me:
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
```

**Token 信息**：
- **Access Token**: JWT，包含用户 ID 和角色
- **Refresh Token**: 可选，用于刷新 Access Token
- **过期时间**：
  - Access Token: 15 分钟
  - Refresh Token: 7 天

---

#### 步骤 3.6：返回响应
```python
return TokenResponse(
    access_token=access_token,
    refresh_token=refresh_token,
    token_type="bearer",
    user={
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "role": user.role,
    },
)
```

**响应示例**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

### 4️⃣ 前端：保存 Token 和用户信息

**文件**：`frontend-vue/src/stores/auth.ts`

#### 步骤 4.1：构造用户信息对象
```typescript
const newUserInfo = {
  id: user.id,
  username: user.username,
  email: user.email || '',
  nickname: user.nickname || user.username,
  avatar: '',
  roles: [user.role],  // ['user'] 或 ['admin']
  permissions: [
    'predict', 'batch', 'history', 'stats',
    'model', 'upload', 'tasks', 'monitoring', 'text_analysis'
  ],
}
```

---

#### 步骤 4.2：持久化到 Storage

**情况 A：记住我（rememberMe = true）**
```typescript
localStorage.setItem('token', access_token)
localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
sessionStorage.removeItem('token')
sessionStorage.removeItem('userInfo')
```
- ✅ Token 保存到 **localStorage**（永久有效，除非手动清除）
- ✅ 关闭浏览器后仍然保留

**情况 B：不记住我（rememberMe = false）**
```typescript
sessionStorage.setItem('token', access_token)
sessionStorage.setItem('userInfo', JSON.stringify(newUserInfo))
localStorage.removeItem('token')
localStorage.removeItem('userInfo')
```
- ✅ Token 保存到 **sessionStorage**（关闭浏览器后自动清除）

---

#### 步骤 4.3：更新 Store 状态
```typescript
// 从 storage 重新读取，更新 store 状态
refreshFromStorage()

console.log('[Auth] Store 状态更新后:', {
  isAuthenticated,
  token: token.value ? 'exists' : 'null'
})
```

**`refreshFromStorage()` 做了什么**：
```typescript
function refreshFromStorage() {
  // 重新从 localStorage/sessionStorage 读取
  token.value = localStorage.getItem('token') || sessionStorage.getItem('token')

  // 重新解析 userInfo
  const stored = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')
  if (stored) {
    const parsed = JSON.parse(stored)
    userInfo.value = { ... }
  }
}
```

**为什么需要这个方法**：
- `token` 和 `userInfo` 是普通 `ref`，不是 `computed`
- 修改 storage 后需要手动更新 store
- 确保 `isAuthenticated` 变为 `true`

---

### 5️⃣ 前端：跳转到目标页面

**文件**：`frontend-vue/src/views/LoginView.vue`

#### 步骤 5.1：确定跳转目标
```typescript
// 获取 redirect 参数
let redirect = router.currentRoute.value.query.redirect as string

// 如果 redirect 是 "/"，跳转到 /predict（避免循环）
if (redirect === '/') {
  redirect = '/predict'
}

const targetPath = redirect || '/predict'
```

**跳转逻辑**：
- 如果有 `?redirect=xxx` 参数 → 跳转到该页面
- 如果 `redirect=/` → 跳转到 `/predict`
- 如果无参数 → 跳转到 `/predict`

---

#### 步骤 5.2：执行跳转
```typescript
// 方法 1：使用 window.location（强制刷新）
window.location.href = targetPath

// 方法 2：使用 router.push（单页应用模式）
// await router.push(targetPath)
```

**推荐使用 `window.location.href`**：
- ✅ 确保完全重新加载
- ✅ 触发完整的路由守卫检查
- ✅ 避免状态不同步问题

---

## 登出流程

### 1️⃣ 前端：用户点击登出

**文件**：`frontend-vue/src/components/layout/AppLayout.vue`

#### 步骤 1.1：触发登出
```vue
<el-dropdown-item @click="handleLogout">
  <el-icon><SwitchButton /></el-icon>
  退出登录
</el-dropdown-item>
```

---

#### 步骤 1.2：调用 AuthStore.logout()
```typescript
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
```

---

### 2️⃣ 前端：AuthStore 处理登出

**文件**：`frontend-vue/src/stores/auth.ts`

#### 步骤 2.1：发送登出请求（可选）
```typescript
async function logout() {
  try {
    await logoutApi()
    // 发送 POST 请求到 /api/v1/auth/logout
  } catch (error) {
    console.error('Logout error:', error)
  }
}
```

**注意**：后端登出接口只是返回成功消息，**实际的 Token 清除在前端完成**

---

#### 步骤 2.2：清除所有 Storage
```typescript
finally {
  // 清除本地状态
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('userInfo')

  // 重新读取 storage（确保状态为空）
  refreshFromStorage()
}
```

**清除内容**：
- ✅ `localStorage.token`
- ✅ `localStorage.userInfo`
- ✅ `sessionStorage.token`
- ✅ `sessionStorage.userInfo`

---

#### 步骤 2.3：更新 Store 状态
```typescript
// refreshFromStorage() 会设置：
token.value = null
userInfo.value = null
// isAuthenticated 自动变为 false
```

---

### 3️⃣ 前端：跳转到登录页

**文件**：`frontend-vue/src/components/layout/AppLayout.vue`

```typescript
function handleLogout() {
  authStore.logout()
  router.push('/login')
}
```

**跳转目标**：`/login`

---

## 路由守卫认证检查

**文件**：`frontend-vue/src/router/index.ts`

### 每次路由跳转时的检查

```typescript
router.beforeEach(async (to, _from) => {
  const store = getAuthStore()

  // 1. 根路径特殊处理
  if (to.path === '/') {
    if (store.isAuthenticated) {
      return { path: '/predict' }
    } else {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  // 2. 检查是否需要认证
  const matchedRoutes = to.matched
  const requiresAuth = matchedRoutes.some(route => route.meta.requiresAuth !== false)

  // 3. 如果需要认证，但未登录 → 跳转到登录页
  if (requiresAuth && !finalIsAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  // 4. 如果已登录，访问登录页 → 跳转到预测页
  if (to.path === '/login' && finalIsAuthenticated) {
    return { path: '/predict' }
  }

  // 5. 放行
  return true
})
```

---

## Token 管理

### Access Token（访问令牌）

**特性**：
- **类型**: JWT (JSON Web Token)
- **有效期**: 15 分钟
- **存储位置**: `localStorage` 或 `sessionStorage`
- **用途**: 访问受保护的 API 接口

**使用方式**：
```typescript
// 请求拦截器自动添加
const token = localStorage.getItem('token') || sessionStorage.getItem('token')
if (token) {
  config.headers.Authorization = `Bearer ${token}`
}
```

---

### Refresh Token（刷新令牌）

**特性**：
- **类型**: JWT
- **有效期**: 7 天（仅在选择"记住我"时生成）
- **存储位置**: `localStorage` 或 `sessionStorage`
- **用途**: 刷新过期的 Access Token

**注意**：当前代码中**没有实现自动刷新逻辑**，Access Token 过期后需要重新登录

---

### Token 过期处理

**文件**：`frontend-vue/src/api/request.ts`

```typescript
// 响应拦截器
if (error.response?.status === 401) {
  // Token 无效或过期
  this.getAuthStore().then(authStore => {
    authStore.logout()
    // 跳转到登录页
    if (window.location.pathname !== '/login') {
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    }
  })
}
```

**处理流程**：
1. 收到 401 响应
2. 自动清除认证数据
3. 跳转到登录页
4. 提示"登录已过期"

---

## 数据存储

### Storage 结构

#### localStorage（长期）

**键值对**：
```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userInfo": "{\"id\":1,\"username\":\"admin\",\"nickname\":\"管理员\",\"roles\":[\"user\"],\"permissions\":[...]}"
}
```

**生命周期**：
- ✅ 关闭浏览器后仍然保留
- ✅ 除非手动清除或调用 `localStorage.removeItem()`
- 适用场景：`rememberMe = true`

---

#### sessionStorage（临时）

**键值对**：
```javascript
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "userInfo": "{\"id\":1,\"username\":\"admin\",\"nickname\":\"管理员\",\"roles\":[\"user\"],\"permissions\":[...]}"
}
```

**生命周期**：
- ⚠️ 关闭浏览器标签页后自动清除
- ⚠️ 新标签页无法访问
- 适用场景：`rememberMe = false`

---

### Cookie

**当前实现**：未使用 Cookie 存储认证信息

**原因**：
- 使用 localStorage/sessionStorage 更灵活
- 避免 CSRF 攻击
- 前端完全控制 Token 生命周期

---

## 流程图

### 登录流程图

```
┌─────────────────┐
│  用户访问系统    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  是否有 Token?  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 否      │ 是
    ▼         ▼
┌─────────┐  ┌──────────────────────┐
│ 显示    │  │ 从 Storage 读取 Token │
│ 登录页  │  └──────────┬───────────┘
└─────────┘             │
                        ▼
               ┌──────────────────────┐
               │ Token 有效吗?         │
               └──────────┬───────────┘
                          │
                     ┌────┴────┐
                     │ 否      │ 是
                     ▼         ▼
               ┌─────────┐  ┌──────────────┐
               │ 重新    │  │ 更新 Store   │
               │ 登录    │  │ 状态         │
               └─────────┘  └──────┬───────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │   显示系统页面         │
                         └──────────────────────┘

┌──────────────────────────────────────────────────┐
│                  登录流程                          │
└──────────────────────────────────────────────────┘

用户输入账号密码
    │
    ▼
前端验证表单
    │
    ▼
发送 POST /api/v1/auth/login
    │
    ▼
后端查找用户
    │
    ▼
验证密码 (bcrypt)
    │
    ▼
检查账户状态
    │
    ▼
生成 Access Token + Refresh Token
    │
    ▼
返回 Token + 用户信息
    │
    ▼
前端保存到 localStorage/sessionStorage
    │
    ▼
调用 refreshFromStorage() 更新 Store
    │
    ▼
跳转到 /predict
    │
    ▼
显示预测页面
```

---

### 登出流程图

```
┌─────────────────┐
│  用户点击登出    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 调用 logout()   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 发送 POST       │
│ /api/v1/auth/   │
│ logout          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 清除 localStorage│
│ token + userInfo │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 清除 sessionStorage│
│ token + userInfo │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 调用            │
│ refreshFromStorage()│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ isAuthenticated │
│ = false         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 跳转到 /login   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  显示登录页      │
└─────────────────┘
```

---

### 路由守卫认证检查流程图

```
┌─────────────────────────────────────────┐
│         路由跳转触发路由守卫             │
└──────────────────┬──────────────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │ 目标路径是 "/" ?       │
         └──────────┬────────────┘
                    │
               ┌────┴────┐
               │ 是      │ 否
               ▼         ▼
         ┌─────────┐  ┌──────────────────────┐
         │ 检查     │  │ 获取目标路由配置       │
         │ isAuth  │  └──────────┬───────────┘
         └────┬────┘             │
              │                   ▼
         ┌────┴────┐      ┌──────────────────────┐
         │已登录?  │      │ requiresAuth = true?  │
         └────┬────┘      └──────────┬───────────┘
              │                   │
         ┌────┴────┐         ┌────┴────┐
         │ 是      │ 否      │ 是      │ 否
         ▼         ▼         ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │跳转     │ │跳转     │ │检查     │ │直接     │
    │/predict │ │/login   │ │isAuth   │ │放行     │
    └─────────┘ └─────────┘ └────┬────┘ └─────────┘
                                 │
                            ┌────┴────┐
                            │已登录?  │
                            └────┬────┘
                                 │
                            ┌────┴────┐
                            │ 是      │ 否
                            ▼         ▼
                       ┌─────────┐ ┌─────────┐
                       │跳转     │ │跳转     │
                       │/predict │ │/login   │
                       └─────────┘ └─────────┘
```

---

## 完整时序图

```
用户          前端页面        AuthStore      后端API       数据库
 │                │              │             │             │
 │─ 输入账号密码 ─►│              │             │             │
 │                │              │             │             │
 │◄─ 显示登录表单 ─│              │             │             │
 │                │              │             │             │
 │── 点击登录 ────►│              │             │             │
 │                │─ login() ──► │             │             │
 │                │              │─ POST /login─►│             │
 │                │              │             │─ 查询用户 ──►│
 │                │              │             │◄─ 返回用户 ──│
 │                │              │             │             │
 │                │              │             │─ 验证密码 ──►│
 │                │              │             │◄─ 验证结果 ──│
 │                │              │             │             │
 │                │              │◄─ Token + 用户信息 │         │
 │                │◄─ 保存到 storage ──│             │             │
 │                │              │             │             │
 │                │─ push('/predict')             │             │
 │◄─ 跳转到预测页 ─│              │             │             │
 │                │              │             │             │
```

---

## 关键代码位置

| 功能 | 文件路径 | 行号 |
|------|---------|------|
| 登录表单 | `frontend-vue/src/views/LoginView.vue` | 10-54 |
| 登录处理 | `frontend-vue/src/views/LoginView.vue` | 97-150 |
| AuthStore.login() | `frontend-vue/src/stores/auth.ts` | 41-81 |
| 后端登录接口 | `backend/app/api/v1/auth.py` | 153-202 |
| 密码验证 | `backend/app/services/auth.py` | bcrypt.checkpw() |
| Token 生成 | `backend/app/services/auth.py` | create_access_token() |
| 路由守卫 | `frontend-vue/src/router/index.ts` | 166-223 |
| 登出处理 | `frontend-vue/src/stores/auth.ts` | 83-95 |
| 请求拦截器 | `frontend-vue/src/api/request.ts` | 21-34 |
| 响应拦截器 | `frontend-vue/src/api/request.ts` | 37-70 |

---

## 测试账号

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| admin | admin123 | user | 全部权限 |

---

## 常见问题

### Q1: 登录成功但无法跳转？

**可能原因**：
1. `redirect` 参数是 `/`，导致循环
2. `window.location.href` 未执行
3. 浏览器缓存问题

**解决方案**：
```typescript
// 确保 redirect 不是 "/"
if (redirect === '/') {
  redirect = '/predict'
}

// 使用 window.location 强制跳转
window.location.href = targetPath
```

---

### Q2: 登录后 isAuthenticated 仍为 false？

**可能原因**：
- `computed` 不会自动响应 storage 变化

**解决方案**：
```typescript
// 登录成功后调用
refreshFromStorage()

// 强制从 storage 重新读取
```

---

### Q3: Token 过期如何重新登录？

**自动处理**：
- 后端返回 401
- 前端自动调用 `logout()`
- 跳转到登录页

**手动处理**：
- 点击右上角用户菜单
- 选择 "退出登录"
- 重新登录

---

### Q4: 记住我和不记住我的区别？

| 对比项 | 记住我 | 不记住我 |
|--------|--------|----------|
| Token 存储 | localStorage | sessionStorage |
| 关闭浏览器后 | ✅ 仍然登录 | ❌ 自动登出 |
| 新标签页 | ✅ 保持登录 | ❌ 需要重新登录 |
| 安全性 | 较低 | 较高 |

---

**文档版本**：2026-07-03
**最后更新**：修复完所有登录/登出问题后
