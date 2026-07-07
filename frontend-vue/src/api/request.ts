import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/api'

class Request {
  private instance: AxiosInstance
  private authStore: ReturnType<typeof import('@/stores/auth').useAuthStore> | null = null
  private isRefreshing = false
  private refreshSubscribers: Array<(token: string) => void> = []

  constructor() {
    // 开发环境和生产环境都使用相对路径
    // API 路径已包含 /api/v1/ 前缀，不需要额外的 baseURL
    this.instance = axios.create({
      baseURL: '',
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加 token 到请求头
        const token = localStorage.getItem('token') || sessionStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        console.error('请求错误:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response) => {
        return response.data
      },
      async (error) => {
        console.error('响应错误:', error)

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

        const message = error.response?.data?.detail || error.message || '请求失败'
        ElMessage.error(message)
        return Promise.reject(error)
      }
    )
  }

  /**
   * 处理 Token 刷新
   */
  private async handleTokenRefresh(config: any): Promise<string | null> {
    // 如果正在刷新，将请求加入队列
    if (this.isRefreshing) {
      return new Promise((resolve) => {
        this.refreshSubscribers.push((token: string) => {
          resolve(token)
        })
      })
    }

    // 获取 authStore
    const authStore = await this.getAuthStore()

    // 检查是否有 refresh_token
    // 直接访问 authStore 的方法
    const refresh_token = authStore['getRefreshToken'] ? authStore['getRefreshToken']() : null

    if (!refresh_token) {
      console.warn('[Request] 没有 refresh_token，无法刷新')
      return null
    }

    // 开始刷新
    this.isRefreshing = true

    try {
      console.log('[Request] 开始刷新 Token')

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

      // 清空队列，所有请求都将失败
      this.refreshSubscribers = []

      return null
    } finally {
      this.isRefreshing = false
    }
  }

  /**
   * 处理登出
   */
  private async handleLogout(message: string) {
    try {
      const authStore = await this.getAuthStore()
      authStore.logout()

      // 跳转到登录页
      if (window.location.pathname !== '/login') {
        ElMessage.error(message)
        window.location.href = '/login'
      }
    } catch (err) {
      console.error('Logout error:', err)
      // 如果无法获取 store，直接跳转
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
  }

  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config)
  }

  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config)
  }

  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config)
  }

  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config)
  }

  // 延迟获取 authStore，避免循环依赖
  private async getAuthStore(): Promise<ReturnType<typeof import('@/stores/auth').useAuthStore>> {
    if (!this.authStore) {
      const module = await import('@/stores/auth')
      this.authStore = module.useAuthStore()
    }
    return this.authStore
  }
}

export const request = new Request()
