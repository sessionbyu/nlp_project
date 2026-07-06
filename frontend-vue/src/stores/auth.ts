import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo, LoginParams } from '@/types/auth'
import { loginApi, getCurrentUser, logoutApi, updateProfile as updateProfileApi, changePassword as changePasswordApi, refreshTokenApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State - 使用普通 ref，每次需要时手动从 storage 读取
  const token = ref<string | null>(() => {
    return localStorage.getItem('token') || sessionStorage.getItem('token')
  })
  const userInfo = ref<UserInfo | null>(() => {
    const stored = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        return {
          id: parsed.id || 0,
          username: parsed.username || '',
          nickname: parsed.nickname || parsed.username || '',
          email: parsed.email || '',
          avatar: parsed.avatar || '',
          roles: Array.isArray(parsed.roles) ? parsed.roles : [],
          permissions: Array.isArray(parsed.permissions) ? parsed.permissions : [],
        }
      } catch (e) {
        console.error('Failed to parse userInfo from storage:', e)
        return null
      }
    }
    return null
  })
  const loading = ref(false)

  // 获取 Refresh Token
  function getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
  }

  // 从 storage 重新读取的方法
  function refreshFromStorage() {
    token.value = localStorage.getItem('token') || sessionStorage.getItem('token')
    const stored = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        userInfo.value = {
          id: parsed.id || 0,
          username: parsed.username || '',
          nickname: parsed.nickname || parsed.username || '',
          email: parsed.email || '',
          avatar: parsed.avatar || '',
          roles: Array.isArray(parsed.roles) ? parsed.roles : [],
          permissions: Array.isArray(parsed.permissions) ? parsed.permissions : [],
        }
      } catch (e) {
        console.error('Failed to parse userInfo from storage:', e)
        userInfo.value = null
      }
    } else {
      userInfo.value = null
    }
  }

  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(params: LoginParams) {
    loading.value = true
    try {
      console.log('[Auth] 开始登录请求:', { username: params.username, remember_me: params.remember_me })

      // 调用真实的登录API
      const response = await loginApi(params)

      console.log('[Auth] 登录响应:', response)

      const { access_token, user, refresh_token } = response

      console.log('[Auth] 解构后的数据:', {
        hasAccessToken: !!access_token,
        hasUser: !!user,
        hasRefreshToken: !!refresh_token,
        username: user?.username
      })

      // 构造 userInfo 对象
      const newUserInfo = {
        id: user.id,
        username: user.username,
        email: user.email || '',
        nickname: user.nickname || user.username,
        avatar: '',
        roles: [user.role],
        permissions: ['predict', 'batch', 'history', 'stats', 'model', 'upload', 'tasks', 'monitoring', 'text_analysis'],
      }

      // 持久化
      if (params.remember_me) {
        localStorage.setItem('token', access_token)
        localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
        // 保存 refresh_token（仅在记住我时）
        if (refresh_token) {
          localStorage.setItem('refresh_token', refresh_token)
        }
        // 清除 sessionStorage 中的旧数据
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('userInfo')
        sessionStorage.removeItem('refresh_token')
        console.log('[Auth] Token 已保存到 localStorage')
      } else {
        sessionStorage.setItem('token', access_token)
        sessionStorage.setItem('userInfo', JSON.stringify(newUserInfo))
        // 不保存 refresh_token（sessionStorage 模式不持久化）
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('refresh_token')
        console.log('[Auth] Token 已保存到 sessionStorage')
      }

      // 从 storage 重新读取，更新 store 状态
      refreshFromStorage()

      console.log('[Auth] 登录成功:', { token: access_token.substring(0, 30) + '...', userInfo: newUserInfo })
      console.log('[Auth] Store 状态更新后:', { isAuthenticated, token: token.value ? 'exists' : 'null' })

      return { token: access_token, userInfo: newUserInfo }
    } catch (error: any) {
      console.error('[Auth] 登录失败:', error)
      console.error('[Auth] 错误详情:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      })
      throw new Error(error.response?.data?.detail || '登录失败')
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      console.log('[Auth] 开始退出登录，调用 API')
      await logoutApi()
      console.log('[Auth] 退出登录 API 调用完成')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // 清除本地状态
      console.log('[Auth] 清除本地存储')
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('refresh_token')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('userInfo')
      sessionStorage.removeItem('refresh_token')

      // 重新读取 storage（确保状态为空）
      console.log('[Auth] 更新 store 状态')
      refreshFromStorage()
      console.log('[Auth] 退出登录完成，当前状态:', {
        isAuthenticated: isAuthenticated.value,
        hasToken: !!token.value,
        hasUserInfo: !!userInfo.value
      })
    }
  }

  // 刷新 Access Token
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
        console.log('[Auth] 新 Token 已保存到 localStorage')
      } else {
        sessionStorage.setItem('token', access_token)
        console.log('[Auth] 新 Token 已保存到 sessionStorage')
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

  async function fetchUser() {
    try {
      loading.value = true
      const user = await getCurrentUser()

      // 构造 userInfo 对象
      const newUserInfo = {
        id: user.id,
        username: user.username,
        email: user.email || '',
        nickname: user.nickname || user.username,
        avatar: '',
        roles: [user.role],
        permissions: ['predict', 'batch', 'history', 'stats', 'model', 'upload', 'tasks', 'monitoring', 'text_analysis'],
      }

      // 持久化
      const currentToken = getToken()
      if (currentToken) {
        localStorage.setItem('userInfo', JSON.stringify(newUserInfo))
      }

      return newUserInfo
    } catch (error: any) {
      console.error('Failed to fetch user:', error)

      // 只在 401 未授权错误时清除 token
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('refresh_token')
        sessionStorage.removeItem('token')
        sessionStorage.removeItem('userInfo')
        sessionStorage.removeItem('refresh_token')
        refreshFromStorage()
      }

      throw error
    } finally {
      loading.value = false
    }
  }

  function hasPermission(permission: string): boolean {
    const info = userInfo.value
    if (!info) return false
    const permissions = info.permissions
    const roles = info.roles
    // 检查数组是否存在且包含权限或admin角色
    return (Array.isArray(permissions) && permissions.includes(permission)) ||
           (Array.isArray(roles) && roles.includes('admin'))
  }

  function hasRole(role: string): boolean {
    const info = userInfo.value
    if (!info) return false
    const roles = info.roles
    // 检查数组是否存在且包含角色或admin角色
    return (Array.isArray(roles) && (roles.includes(role) || roles.includes('admin')))
  }

  return {
    token,
    userInfo,
    loading,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    refreshToken,         // 新增：刷新 Token
    getRefreshToken,      // 新增：获取 Refresh Token
    refreshFromStorage,   // 新增：手动刷新状态
    hasPermission,
    hasRole,
  }
})
