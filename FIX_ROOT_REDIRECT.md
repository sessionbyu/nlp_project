# 修复完成报告：根路径重定向问题

## 问题描述

在无痕窗口访问 `http://192.168.88.134:3000/` 时，预期重定向到 `/login`，但实际重定向到了 `/predict`。

## 根本原因

### 1. 路由配置冲突

`frontend-vue/src/router/index.ts` 中存在**两个 `path: '/'` 的路由定义**：

- **路由 A**（第 8-11 行）：重定向路由，`redirect: '/login'`，**没有 `meta` 字段**
- **路由 B**（第 22-128 行）：AppLayout 布局路由，`meta: { requiresAuth: true }`

当访问 `/` 时，`to.matched` 会包含**这两个路由**，导致认证检查逻辑混乱：

```typescript
const requiresAuth = matchedRoutes.some(route => route.meta.requiresAuth !== false)
// 路由 A 的 meta.requiresAuth 是 undefined
// undefined !== false = true
// 导致 requiresAuth 可能被错误计算为 true
```

### 2. 重复的认证检查

`AppLayout.vue` 组件在 `onMounted` 中有额外的认证检查（第 244-248 行），与路由守卫的认证逻辑重复，可能导致冲突。

## 修复内容

### ✅ 修改文件 1：`frontend-vue/src/router/index.ts`

**改动 1**：删除重复的根路径重定向路由

```diff
const routes: RouteRecordRaw[] = [
-  {
-    path: '/',
-    redirect: '/login',
-  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
```

**改动 2**：在路由守卫中添加根路径重定向逻辑

```typescript
// 全局路由守卫
router.beforeEach(async (to, _from) => {
  document.title = `${to.meta.title || 'NLP'} - NLP 预测平台`

  // 获取 store 实例（延迟初始化）
  const store = getAuthStore()

  // ✅ 新增：根路径重定向逻辑
  if (to.path === '/') {
    if (store.isAuthenticated) {
      return { path: '/predict' }
    } else {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  // ... 其余路由守卫逻辑
```

### ✅ 修改文件 2：`frontend-vue/src/components/layout/AppLayout.vue`

**改动**：删除组件内部的重复认证检查

```diff
onMounted(() => {
-  // 额外保护：如果用户未认证，跳转到登录页
-  if (!authStore.isAuthenticated) {
-    router.push('/login')
-  }
-
   window.addEventListener('resize', handleResize)
   document.addEventListener('click', handleClickOutside)
})
```

## 修复效果

### 访问流程（无痕窗口，未登录）

1. 用户访问 `http://192.168.88.134:3000/`
2. 路由守卫检查 `to.path === '/'` → `true`
3. 检查 `store.isAuthenticated` → `false`（无痕窗口无 token）
4. **重定向到 `/login`** ✅

### 访问流程（已登录）

1. 用户访问 `http://192.168.88.134:3000/`
2. 路由守卫检查 `to.path === '/'` → `true`
3. 检查 `store.isAuthenticated` → `true`
4. **重定向到 `/predict`** ✅

## 构建状态

- ✅ **前端代码构建成功**：`npm run build` 完成
- ✅ **构建产物已生成**：`frontend-vue/dist/` 目录
- ⚠️ **Docker 镜像构建失败**：网络问题无法拉取 `nginx:alpine` 基础镜像

## 下一步：部署到生产环境

由于 Docker Hub 网络连接问题，需要手动完成 Docker 镜像构建：

### 选项 1：使用 Docker 镜像构建（推荐）

在**网络环境良好**的终端执行：

```bash
cd /home/user/nlp_project

# 构建前端 Docker 镜像
docker compose build frontend-vue

# 启动前端服务
docker compose up -d frontend-vue

# 验证
docker compose ps frontend-vue
```

### 选项 2：手动复制构建产物

如果 Docker 镜像构建仍有问题，可以直接复制构建产物到 Nginx 容器：

```bash
# 查找正在运行的 Nginx 容器
docker ps | grep nlp_frontend

# 复制 dist 目录到容器
docker cp frontend-vue/dist nlp_frontend:/usr/share/nginx/html/

# 重启 Nginx
docker exec nlp_frontend nginx -s reload
```

### 选项 3：等待网络恢复后重新构建

```bash
# 运行构建脚本（会自动提示是否启动）
./build_vue_frontend.sh
```

## 验证步骤

部署完成后，请使用以下步骤验证：

1. **打开无痕窗口**（Ctrl+Shift+N 或 Cmd+Shift+N）
2. 访问 `http://192.168.88.134:3000/`
3. ✅ **预期结果**：自动重定向到 `http://192.168.88.134:3000/login`
4. ❌ **如果重定向到 `/predict`**：说明仍有问题，请检查：
   - 浏览器是否真的清除了所有缓存和 Cookie
   - 后端服务是否正常运行
   - Nginx 配置是否正确

## 相关文件

- `frontend-vue/src/router/index.ts` - 路由配置
- `frontend-vue/src/components/layout/AppLayout.vue` - 布局组件
- `frontend-vue/dist/` - 构建产物

## 其他说明

- 修复采用**方案 1：统一认证检查**，删除了重复的路由和组件内部检查
- 路由守卫现在是认证和重定向的唯一权威
- 代码更清晰，避免双重逻辑冲突
