import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import AppLayout from '@/components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/',
    component: AppLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: 'predict',
        name: 'Predict',
        component: () => import('@/views/PredictView.vue'),
        meta: {
          title: '文本预测',
          icon: 'Document',
          permission: 'predict',
        },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/HistoryView.vue'),
        meta: {
          title: '历史记录',
          icon: 'Timer',
          permission: 'history',
        },
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/StatisticsView.vue'),
        meta: {
          title: '统计概览',
          icon: 'DataAnalysis',
          permission: 'stats',
        },
      },
      {
        path: 'batch',
        name: 'Batch',
        component: () => import('@/views/BatchView.vue'),
        meta: {
          title: '批量处理',
          icon: 'List',
          permission: 'batch',
        },
      },
      {
        path: 'upload',
        name: 'FileUpload',
        component: () => import('@/views/FileUploadView.vue'),
        meta: {
          title: '文件上传',
          icon: 'Upload',
          permission: 'upload',
        },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/TasksView.vue'),
        meta: {
          title: '任务管理',
          icon: 'Management',
          permission: 'tasks',
        },
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/ModelsView.vue'),
        meta: {
          title: '模型管理',
          icon: 'Cpu',
          permission: 'model',
        },
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/views/MonitoringView.vue'),
        meta: {
          title: '系统监控',
          icon: 'Monitor',
          permission: 'monitoring',
        },
      },
      {
        path: 'text-analysis',
        name: 'TextAnalysis',
        component: () => import('@/views/TextAnalysisView.vue'),
        meta: {
          title: '文本增强分析',
          icon: 'Cpu',
          permission: 'text_analysis',
        },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: {
          title: '个人设置',
          icon: 'User',
          hideInMenu: true, // 在菜单中隐藏
        },
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/components/layout/AdminLayout.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,
    },
    children: [
      {
        path: '',
        redirect: '/admin/users',
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/AdminUsersView.vue'),
        meta: {
          title: '用户管理',
          requiresAdmin: true,
        },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 缓存 store 实例（延迟初始化，确保 pinia 已安装）
let authStore: ReturnType<typeof useAuthStore> | null = null

function getAuthStore() {
  if (!authStore) {
    authStore = useAuthStore()
  }
  return authStore
}

// 全局路由守卫
router.beforeEach(async (to, _from) => {
  document.title = `${to.meta.title || 'NLP'} - NLP 预测平台`

  // 获取 store 实例（延迟初始化）
  const store = getAuthStore()

  console.log('[Router] 路由守卫触发:', {
    path: to.path,
    isAuthenticated: store.isAuthenticated,
    hasToken: !!store.token,
    hasUserInfo: !!store.userInfo
  })

  // 根路径重定向到登录页（未认证时）或预测页（已认证时）
  if (to.path === '/') {
    if (store.isAuthenticated) {
      console.log('[Router] 根路径，已认证，跳转到 /predict')
      return { path: '/predict' }
    } else {
      console.log('[Router] 根路径，未认证，跳转到 /login')
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  // 检查是否需要认证（检查当前路由及其所有父路由）
  const matchedRoutes = to.matched
  const requiresAuth = matchedRoutes.some(route => route.meta.requiresAuth !== false)
  const isAuthenticated = store.isAuthenticated

  console.log('[Router] 认证检查:', {
    requiresAuth,
    isAuthenticated,
    path: to.path,
    hasUserInfo: !!store.userInfo,
    userRoles: store.userInfo?.roles
  })

  // 检查是否需要管理员权限
  const requiresAdmin = matchedRoutes.some(route => route.meta.requiresAdmin === true)
  const isAdmin = store.userInfo?.roles?.includes('admin') || false

  // 如果需要认证，确保认证状态已完全加载
  if (requiresAuth && isAuthenticated && !store.userInfo) {
    console.log('[Router] 需要认证且已认证，但缺少用户信息，尝试获取')
    try {
      // 等待用户信息加载完成
      await store.fetchUser()
      console.log('[Router] 用户信息获取成功:', store.userInfo?.username)
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      // fetchUser 内部已经处理了 401 错误并清除了 token
    }
  }

  // 重新检查认证状态（可能在 fetchUser 后被更新）
  const finalIsAuthenticated = store.isAuthenticated
  const finalIsAdmin = store.userInfo?.roles?.includes('admin') || false

  console.log('[Router] 最终认证状态:', {
    finalIsAuthenticated,
    finalIsAdmin,
    path: to.path
  })

  if (requiresAuth && !finalIsAuthenticated) {
    console.log('[Router] 未登录，跳转到登录页')
    // 未登录，跳转到登录页
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  } else if (requiresAdmin && !finalIsAdmin) {
    // 不是管理员，拒绝访问
    ElMessage.error('权限不足，仅管理员可访问')
    console.log('[Router] 权限不足，跳转到首页')
    return { path: '/' }
  } else if (to.path === '/login' && finalIsAuthenticated) {
    // 已登录，跳转到预测页面
    console.log('[Router] 已登录用户访问登录页，跳转到预测页')
    return { path: '/predict' }
  } else {
    // 继续导航
    console.log('[Router] 允许导航到:', to.path)
    return true
  }
})

export default router
