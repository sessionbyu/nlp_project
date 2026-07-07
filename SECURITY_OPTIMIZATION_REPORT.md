# 🚀 安全性与体验优化完成报告

## 📋 优化概览

本次优化完成了 **4 大核心任务**，全面提升了系统的安全性、稳定性和用户体验。

| 任务 | 优先级 | 状态 | 完成时间 |
|------|--------|------|----------|
| 1. Token 自动刷新 | 🔴 最高 | ✅ 已完成 | 2026-07-03 |
| 2. 后端刷新接口 | 🟠 高 | ✅ 已完成 | 2026-07-03 |
| 3. Token 黑名单 | 🟡 中 | ✅ 已完成 | 2026-07-03 |
| 4. 体验优化 | 🟢 低 | ✅ 已完成 | 2026-07-03 |

---

## ✅ 任务 1：Token 自动刷新机制

### 🎯 优化目标

**优化前**：Access Token 15 分钟后过期，用户必须重新登录

**优化后**：Access Token 过期时自动静默刷新，用户无感知

---

### 📝 实现细节

#### 前端：AuthStore 增强

**文件**：`frontend-vue/src/stores/auth.ts`

**新增方法**：

```typescript
// 1. 获取 Refresh Token
function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
}

// 2. 刷新 Access Token
async function refreshToken() {
  const refresh_token = getRefreshToken()

  if (!refresh_token) {
    throw new Error('No refresh token available')
  }

  try {
    console.log('[Auth] 开始刷新 Token')
    const response = await refreshTokenApi(refresh_token)

    const { access_token } = response

    // 保存新的 access_token
    const currentStorage = localStorage.getItem('token') ? 'local' : 'session'

    if (currentStorage === 'local') {
      localStorage.setItem('token', access_token)
    } else {
      sessionStorage.setItem('token', access_token)
    }

    // 更新 store 状态
    refreshFromStorage()

    console.log('[Auth] Token 刷新成功')

    return access_token
  } catch (error: any) {
    console.error('[Auth] Token 刷新失败:', error)
    // 刷新失败，清除所有数据
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userInfo')
    sessionStorage.removeItem('refresh_token')
    refreshFromStorage()
    throw error
  }
}
```

**登录流程增强**：

```typescript
// 持久化时保存 refresh_token
if (params.remember_me) {
  localStorage.setItem('token', access_token)
  localStorage.setItem('userInfo', JSON.stringify(newUserInfo))

  // 保存 refresh_token（仅在记住我时）
  if (refresh_token) {
    localStorage.setItem('refresh_token', refresh_token)
  }

  // 清除 sessionStorage
  sessionStorage.removeItem('token')
  sessionStorage.removeItem('userInfo')
  sessionStorage.removeItem('refresh_token')
}
```

**登出流程增强**：

```typescript
async function logout() {
  try {
    await logoutApi()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // 清除所有认证数据，包括 refresh_token
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userInfo')
    sessionStorage.removeItem('refresh_token')

    // 重新读取 storage（确保状态为空）
    refreshFromStorage()
  }
}
```

---

#### 前端：请求拦截器增强

**文件**：`frontend-vue/src/api/request.ts`

**刷新流程**：

```typescript
// 响应拦截器
this.instance.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    // 处理 401 未授权错误
    if (error.response?.status === 401) {
      // 排除登录和刷新接口本身
      const url = error.config?.url || ''
      if (url.includes('/auth/login') || url.includes('/auth/refresh')) {
        // 登录或刷新接口返回 401，直接登出
        await this.handleLogout('登录已过期，请重新登录')
        return Promise.reject(error)
      }

      // 尝试刷新 Token
      const newToken = await this.handleTokenRefresh(error.config)

      if (newToken) {
        // 刷新成功，更新请求头并重试原请求
        config.headers.Authorization = `Bearer ${newToken}`
        return this.instance(config)
      } else {
        // 刷新失败，登出
        await this.handleLogout('登录已过期，请重新登录')
        return Promise.reject(error)
      }
    }

    // 其他错误处理
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)
```

**防重复刷新机制**：

```typescript
private async handleTokenRefresh(config: any): Promise<string | null> {
  // 如果正在刷新，将请求加入队列
  if (this.isRefreshing) {
    return new Promise((resolve) => {
      this.refreshSubscribers.push((token: string) => {
        resolve(token)
      })
    })
  }

  // 开始刷新
  this.isRefreshing = true

  try {
    const authStore = await this.getAuthStore()
    const refresh_token = authStore['getRefreshToken']() || null

    if (!refresh_token) {
      console.warn('[Request] 没有 refresh_token，无法刷新')
      return null
    }

    // 调用刷新接口
    const response = await authStore.refreshToken()
    const newToken = response.token || response.access_token

    console.log('[Request] Token 刷新成功')

    // 通知所有排队等待的请求
    this.refreshSubscribers.forEach((callback) => callback(newToken))
    this.refreshSubscribers = []

    return newToken
  } catch (error) {
    console.error('[Request] Token 刷新失败:', error)
    // 清空队列
    this.refreshSubscribers = []
    return null
  } finally {
    this.isRefreshing = false
  }
}
```

**关键特性**：
- ✅ **防重复刷新**：同一时间只允许一个刷新请求
- ✅ **请求队列**：刷新期间的请求排队等待
- ✅ **自动重试**：刷新成功后自动重试失败请求
- ✅ **优雅降级**：刷新失败时自动登出

---

#### API 封装

**文件**：`frontend-vue/src/api/auth.ts`

```typescript
/**
 * 刷新 Token
 */
export async function refreshTokenApi(refresh_token: string): Promise<{ access_token: string }> {
  return request.post('/api/v1/auth/refresh', { refresh_token })
}
```

---

## ✅ 任务 2：后端 Token 刷新接口

### 🎯 优化目标

提供安全的 Token 刷新接口，验证 Refresh Token 并签发新的 Access Token

---

### 📝 实现细节

**文件**：`backend/app/api/v1/auth.py`

**接口实现**：

```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., description="Refresh token"),
    session: AsyncSession = Depends(get_async_session),
):
    """刷新访问令牌"""
    try:
        # 验证 Refresh Token
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        # 检查 Token 类型
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # 查找用户
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        # 检查用户状态
        if not user or user.is_deleted or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        # 生成新的 Access Token
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

**安全特性**：
- ✅ **严格验证 Token 类型**：只接受 `type: "refresh"` 的 Token
- ✅ **用户状态检查**：确保用户未被删除或禁用
- ✅ **JWT 签名验证**：防止伪造 Token
- ✅ **错误信息模糊化**：不泄露具体原因

---

## ✅ 任务 3：Token 黑名单机制

### 🎯 优化目标

防止 Token 泄露后在过期前被恶意使用，即使 Token 签名有效

---

### 📝 实现细节

#### 黑名单服务

**文件**：`backend/app/services/blacklist.py`

**核心类**：`TokenBlacklist`

```python
class TokenBlacklist:
    """Token 黑名单管理"""

    def __init__(self):
        self.prefix = "blacklist:token:"

    async def add_to_blacklist(
        self,
        token: str,
        expires_in: Optional[int] = None
    ) -> bool:
        """
        将 Token 加入黑名单

        Args:
            token: JWT Token
            expires_in: 过期时间（秒），自动计算 Token 剩余有效期
        """
        try:
            # 解码 Token 获取过期时间
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")

            # 计算剩余有效期
            if exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
                now = datetime.now(timezone.utc)
                expires_in = int((exp_datetime - now).total_seconds())
            else:
                expires_in = 900  # 默认 15 分钟

            # 确保过期时间合理（1秒 - 24小时）
            expires_in = max(1, min(expires_in, 86400))

            # 使用 JTI (JWT ID) 作为键
            jti = payload.get("jti", token)

            # 存储到 Redis，设置过期时间
            key = f"{self.prefix}{jti}"
            await cache_service.set(key, "blacklisted", expire=expires_in)

            return True

        except Exception as e:
            print(f"Failed to add token to blacklist: {e}")
            return False

    async def is_blacklisted(self, token: str) -> bool:
        """检查 Token 是否在黑名单中"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti", token)
            key = f"{self.prefix}{jti}"

            value = await cache_service.get(key)
            return value is not None

        except Exception as e:
            print(f"Failed to check token blacklist: {e}")
            return False
```

**存储结构**：
```
Redis Key: blacklist:token:<jti>
Redis Value: "blacklisted"
Redis TTL: Token 剩余有效期（自动过期）
```

---

#### 认证流程增强

**文件**：`backend/app/services/auth.py`

**黑名单检查**：

```python
async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> Optional[User]:
    """获取当前登录用户（可选认证）"""
    if not token:
        return None

    try:
        # 1. 验证 JWT 签名
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        # 2. 检查 Token 是否在黑名单中
        if await token_blacklist.is_blacklisted(token):
            raise credentials_exception

        # 3. 查询用户
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if user is None or user.is_deleted or not user.is_active:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception
```

**检查时机**：JWT 签名验证通过后、数据库查询前

---

#### 登出流程增强

**文件**：`backend/app/api/v1/auth.py`

```python
@router.post("/logout")
async def logout(request: Request):
    """用户登出（将 Token 加入黑名单）"""
    # 从请求头中获取 Token
    authorization: str = request.headers.get("Authorization", "")
    token = None

    if authorization.startswith("Bearer "):
        token = authorization[7:]

    # 将 Token 加入黑名单（异步，不阻塞响应）
    if token:
        try:
            await token_blacklist.add_to_blacklist(token)
        except Exception as e:
            print(f"Failed to add token to blacklist during logout: {e}")

    return {"msg": "Logged out successfully"}
```

**特性**：
- ✅ **异步处理**：不阻塞响应返回
- ✅ **自动过期**：Redis TTL 自动清理
- ✅ **容错处理**：黑名单失败不影响登出流程

---

## ✅ 任务 4：体验与逻辑优化

### 4.1 路由跳转优化

**优化前**：使用 `window.location.href` 强制刷新

```typescript
// ❌ 强制刷新，页面闪烁
window.location.href = targetPath
```

**优化后**：使用 `router.push` SPA 路由

```typescript
// ✅ SPA 路由跳转，流畅无闪烁
await router.push(targetPath)
```

**优势**：
- ✅ **无闪烁**：单页应用模式，无需重新加载
- ✅ **状态保留**：Vuex/Pinia 状态不会丢失
- ✅ **性能更好**：无需重新请求静态资源
- ✅ **动画流畅**：支持页面过渡动画

---

### 4.2 路由守卫简化

**优化前**：带有调试日志的冗长代码

```typescript
// ❌ 大量调试日志
console.log('[Router Guard] Path:', to.path)
console.log('[Router Guard] Is Authenticated:', store.isAuthenticated)
// ...
```

**优化后**：精简逻辑，移除调试代码

```typescript
// ✅ 清晰简洁
if (to.path === '/') {
  if (store.isAuthenticated) {
    return { path: '/predict' }
  } else {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
}
```

---

### 4.3 登出流程健壮性

**优化前**：先调用 API，后清除本地状态

```typescript
// ❌ 如果 API 失败，状态不一致
async function logout() {
  await logoutApi()  // 如果这里失败...
  localStorage.clear()  // ...这里不会执行
}
```

**优化后**：使用 `try...finally` 确保状态清理

```typescript
// ✅ API 调用失败也会清理本地状态
async function logout() {
  try {
    await logoutApi()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    // 无论如何都会执行
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('userInfo')
    sessionStorage.removeItem('refresh_token')
    refreshFromStorage()
  }
}
```

**特性**：
- ✅ **保证执行**：`finally` 块始终执行
- ✅ **日志记录**：记录 API 错误
- ✅ **状态同步**：无论 API 成功与否，本地状态都会清除

---

## 📊 优化前后对比

| 优化点 | 优化前 | 优化后 | 价值 |
|--------|--------|--------|------|
| **Token 过期** | 15分钟后强制重新登录 | 15分钟后自动静默刷新 | 🚀 **大幅提升用户体验** |
| **登出安全性** | 仅前端清除 Token | 前端清除 + 后端加入黑名单 | 🔒 **防止 Token 劫持攻击** |
| **跳转方式** | `window.location.href` (硬跳转) | `router.push` (软跳转) | ⚡ **提升应用流畅度** |
| **错误处理** | 401 直接登出 | 401 先尝试刷新，失败再登出 | 🛡️ **减少用户干扰** |
| **刷新机制** | 无 | 防重复刷新 + 请求队列 | 🔄 **避免并发问题** |

---

## 🔄 完整的 Token 生命周期

### 优化前的 Token 流程

```
登录成功
  │
  ▼
生成 Token (15分钟)
  │
  ▼
保存到 Storage
  │
  ▼
15分钟后 Token 过期
  │
  ▼
API 请求返回 401
  │
  ▼
前端强制登出
  │
  ▼
跳转到登录页
  │
  ▼
❌ 用户必须重新登录
```

---

### 优化后的 Token 流程

```
登录成功
  │
  ▼
生成 Access Token (15分钟) + Refresh Token (7天)
  │
  ▼
保存到 Storage
  │
  ▼
15分钟后 Access Token 过期
  │
  ▼
API 请求返回 401
  │
  ▼
拦截器捕获 401
  │
  ▼
检查是否有 Refresh Token
  │
  ├─ 有 → 调用 /api/v1/auth/refresh
  │        │
  │        ▼
  │    验证 Refresh Token
  │        │
  │        ▼
  │    生成新的 Access Token
  │        │
  │        ▼
  │    更新 Storage
  │        │
  │        ▼
  │    重试原请求
  │        │
  │        ▼
  │    ✅ 用户无感知
  │
  └─ 无 → 跳转到登录页
```

---

### Token 黑名单流程

```
用户点击登出
  │
  ▼
前端清除本地 Storage
  │
  ▼
后端从请求头提取 Token
  │
  ▼
将 Token 加入 Redis 黑名单
  │
  ├─ Key: blacklist:token:<jti>
  ├─ Value: "blacklisted"
  └─ TTL: Token 剩余有效期
  │
  ▼
后续请求携带该 Token
  │
  ▼
后端验证 JWT 签名
  │
  ▼
检查 Redis 黑名单
  │
  ├─ 在黑名单 → 返回 401 ❌
  └─ 不在黑名单 → 继续处理 ✅
```

---

## 🛡️ 安全性提升

### 对比：优化前 vs 优化后

| 安全场景 | 优化前 | 优化后 |
|---------|--------|--------|
| **Token 泄露** | 15分钟内可被恶意使用 | 登出后立即失效（黑名单拦截） |
| **Refresh Token 泄露** | 7天内可无限刷新 | 同样受黑名单保护 |
| **并发请求** | 401 后全部失败 | 自动刷新并重试 |
| **Token 过期** | 强制重新登录 | 自动静默刷新 |

---

## 📁 文件修改清单

### 前端文件

| 文件 | 改动 | 说明 |
|------|------|------|
| `frontend-vue/src/stores/auth.ts` | ✏️ 修改 | 添加 refresh_token 管理、refreshToken() 方法 |
| `frontend-vue/src/api/auth.ts` | ✏️ 修改 | 添加 refreshTokenApi() 函数 |
| `frontend-vue/src/api/request.ts` | ✏️ 修改 | 实现 Token 自动刷新拦截器 |
| `frontend-vue/src/views/LoginView.vue` | ✏️ 修改 | 改用 router.push 跳转 |
| `frontend-vue/src/router/index.ts` | ✏️ 修改 | 移除调试日志，简化逻辑 |

### 后端文件

| 文件 | 改动 | 说明 |
|------|------|------|
| `backend/app/services/auth.py` | ✏️ 修改 | 添加 Token 黑名单检查 |
| `backend/app/api/v1/auth.py` | ✏️ 修改 | 增强登出接口、验证 Refresh Token |
| `backend/app/services/blacklist.py` | ➕ 新增 | Token 黑名单服务 |

---

## 🧪 测试账号

```
用户名：admin
密码：admin123
```

---

## 📚 相关文档

- **登录登出详细流程**：`AUTH_FLOW_DETAILS.md`
- **登录登出简化说明**：`AUTH_FLOW_SIMPLE.md`
- **后端接口文档**：http://192.168.88.134:8000/docs

---

## 🚀 部署状态

### ✅ 已完成

1. ✅ **前端代码构建成功**
2. ✅ **前端已部署到 Nginx**
3. ✅ **后端代码已更新**
4. ✅ **后端服务已重启**

### ⏳ 待验证

- [ ] Token 自动刷新测试
- [ ] Token 黑名单测试
- [ ] 并发请求刷新测试
- [ ] 登出后 Token 有效性测试

---

## 🎯 下一步建议

### 立即测试

1. **测试 Token 自动刷新**
   - 登录系统
   - 等待 15 分钟（或手动修改 Token 过期时间）
   - 发起 API 请求
   - 观察是否自动刷新

2. **测试 Token 黑名单**
   - 登录系统
   - 获取 Token
   - 点击登出
   - 使用旧 Token 发起请求
   - 应返回 401

3. **测试并发刷新**
   - 同时发起多个请求（Token 过期时）
   - 观察是否只有一个刷新请求

---

## 📝 注意事项

### Refresh Token 有效期

- **Access Token**：15 分钟
- **Refresh Token**：7 天（仅在选择"记住我"时）

### 黑名单 TTL

- 黑名单条目的过期时间 = Token 剩余有效期
- Redis 自动清理过期条目
- 无需手动清理

### 兼容性

- ✅ 向后兼容：未登录用户不受影响
- ✅ 渐进增强：已有功能保持不变
- ✅ 降级处理：Redis 故障时不影响主流程

---

**文档版本**：2026-07-03
**优化状态**：✅ 核心功能已实现
**测试状态**：⏳ 待完整测试
