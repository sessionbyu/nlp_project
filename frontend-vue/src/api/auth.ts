import { request } from './request'
import type { LoginParams, LoginResponse, UserInfo } from '@/types/auth'

/**
 * 登录
 */
export async function loginApi(data: LoginParams): Promise<LoginResponse> {
  return request.post('/api/v1/auth/login', data)
}

/**
 * 登出
 */
export async function logoutApi(): Promise<void> {
  await request.post('/api/v1/auth/logout')
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(): Promise<UserInfo> {
  return request.get('/api/v1/auth/me')
}

/**
 * 刷新 Token
 */
export async function refreshToken(): Promise<{ token: string }> {
  return request.post('/api/v1/auth/refresh')
}

/**
 * 刷新 Token
 */
export async function refreshTokenApi(refresh_token: string): Promise<{ access_token: string }> {
  return request.post('/api/v1/auth/refresh', { refresh_token })
}

/**
 * 修改密码
 */
export async function changePassword(data: {
  current_password: string
  new_password: string
}): Promise<void> {
  return request.post('/api/v1/auth/change-password', data)
}

/**
 * 更新用户信息
 */
export async function updateProfile(data: {
  nickname?: string
  email?: string
  phone?: string
}): Promise<UserInfo> {
  return request.put('/api/v1/auth/profile', data)
}

/**
 * API Key 响应
 */
export interface APIKeyResponse {
  id: number
  name: string
  key_prefix: string
  permissions: string
  is_active: boolean
  expires_at?: string
  last_used_at?: string
  created_at: string
}

/**
 * 创建 API Key 请求
 */
export interface APIKeyCreateRequest {
  name: string
  permissions?: string
  expires_in_days?: number
}

/**
 * 创建 API Key 响应
 */
export interface APIKeyCreateResponse {
  id: number
  name: string
  api_key: string
  key_prefix: string
  permissions: string
  is_active: boolean
  expires_at?: string
  created_at: string
  message: string
}

/**
 * 获取用户的 API Keys
 */
export async function getUserAPIKeys(): Promise<APIKeyResponse[]> {
  return request.get('/api/v1/auth/api-keys')
}

/**
 * 创建 API Key
 */
export async function createAPIKey(data: APIKeyCreateRequest): Promise<APIKeyCreateResponse> {
  return request.post('/api/v1/auth/api-keys', data)
}

/**
 * 撤销 API Key
 */
export async function revokeAPIKey(keyId: number): Promise<{ message: string }> {
  return request.delete(`/api/v1/auth/api-keys/${keyId}`)
}
