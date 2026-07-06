/**
 * 用户认证相关类型定义
 */

export interface UserInfo {
  id: number
  username: string
  nickname: string
  email?: string
  avatar?: string
  roles: string[]
  permissions: string[]
}

export interface LoginParams {
  username: string
  password: string
  rememberMe?: boolean
}

export interface LoginResponse {
  token: string
  userInfo: UserInfo
  expiresIn: number
}

export interface ChangePasswordParams {
  oldPassword: string
  newPassword: string
}

export interface UpdateProfileParams {
  nickname?: string
  email?: string
  avatar?: string
}
