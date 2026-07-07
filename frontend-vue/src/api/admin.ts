/**
 * 管理员 API
 *
 * 功能：
 * 1. 用户管理
 * 2. API Key 管理
 * 3. 系统统计
 */

import { request } from './request'

/**
 * 用户响应
 */
export interface AdminUserResponse {
  id: number
  username: string
  email: string
  nickname?: string
  role: 'admin' | 'user'
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

/**
 * 更新用户请求
 */
export interface UserUpdateRequest {
  role?: 'admin' | 'user'
  is_active?: boolean
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
 * 创建 API Key 响应（包含明文 key）
 */
export interface APIKeyCreateResponse {
  id: number
  name: string
  api_key: string // 仅创建时返回
  key_prefix: string
  permissions: string
  is_active: boolean
  expires_at?: string
  created_at: string
  message: string
}

/**
 * 管理员统计
 */
export interface AdminStatsResponse {
  total_users: number
  active_users: number
  total_predictions: number
  total_api_keys: number
  recent_registrations: number
}

/**
 * 获取用户列表
 *
 * @param page 页码
 * @param page_size 每页数量
 * @returns 用户列表
 */
export function getUsers(page: number = 1, page_size: number = 20) {
  return request.get<{
    total: number
    page: number
    page_size: number
    users: AdminUserResponse[]
  }>('/api/v1/admin/users', { params: { page, page_size } })
}

/**
 * 获取用户详情
 *
 * @param userId 用户ID
 * @returns 用户详情
 */
export function getUserById(userId: number) {
  return request.get<AdminUserResponse>(`/api/v1/admin/users/${userId}`)
}

/**
 * 更新用户信息
 *
 * @param userId 用户ID
 * @param data 更新数据
 * @returns 更新后的用户
 */
export function updateUser(userId: number, data: UserUpdateRequest) {
  return request.put<AdminUserResponse>(`/api/v1/admin/users/${userId}`, data)
}

/**
 * 删除用户（软删除）
 *
 * @param userId 用户ID
 * @returns 删除结果
 */
export function deleteUser(userId: number) {
  return request.delete<{ message: string }>(`/api/v1/admin/users/${userId}`)
}

/**
 * 获取用户的 API Keys
 *
 * @param userId 用户ID
 * @returns API Key 列表
 */
export function getUserAPIKeys(userId: number) {
  return request.get<APIKeyResponse[]>(`/api/v1/admin/users/${userId}/api-keys`)
}

/**
 * 为用户创建 API Key
 *
 * @param userId 用户ID
 * @param data API Key 信息
 * @returns 创建的 API Key（包含明文）
 */
export function createAPIKeyForUser(userId: number, data: APIKeyCreateRequest) {
  return request.post<APIKeyCreateResponse>(`/api/v1/admin/users/${userId}/api-keys`, data)
}

/**
 * 撤销 API Key
 *
 * @param keyId API Key ID
 * @returns 撤销结果
 */
export function revokeAPIKey(keyId: number) {
  return request.delete<{ message: string }>(`/api/v1/admin/api-keys/${keyId}`)
}

/**
 * 获取管理员统计信息
 *
 * @returns 统计信息
 */
export function getAdminStats() {
  return request.get<AdminStatsResponse>('/api/v1/admin/stats/overview')
}
