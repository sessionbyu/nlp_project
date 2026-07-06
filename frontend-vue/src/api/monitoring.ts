/**
 * 监控 API
 *
 * 功能：
 * 1. 健康检查
 * 2. 系统状态
 * 3. Prometheus 指标
 */

import { request } from './request'

/**
 * 健康检查响应
 */
export interface HealthCheckResponse {
  status: string
  service: string
  timestamp?: string
}

/**
 * 系统状态响应
 */
export interface SystemStatusResponse {
  system: {
    cpu_percent: number
    memory: {
      total: number
      available: number
      percent: number
      used: number
    }
    disk?: {
      total: number
      free: number
      percent: number
    }
  }
  database: {
    status: string
    prediction_count?: number
    error?: string
  }
  config: {
    default_model: string
    redis_host?: string
    rate_limit_enabled: boolean
  }
  timestamp: string
}

/**
 * 基本健康检查
 *
 * @returns 健康状态
 */
export function healthCheck() {
  return request.get<HealthCheckResponse>('/api/v1/health')
}

/**
 * 就绪检查（数据库连接）
 *
 * @returns 就绪状态
 */
export function readinessCheck() {
  return request.get<HealthCheckResponse>('/api/v1/health/ready')
}

/**
 * 存活检查（K8s liveness）
 *
 * @returns 存活状态
 */
export function livenessCheck() {
  return request.get<HealthCheckResponse>('/api/v1/health/live')
}

/**
 * 获取系统状态
 *
 * @returns 系统状态信息
 */
export function getSystemStatus() {
  return request.get<SystemStatusResponse>('/api/v1/status')
}

/**
 * 获取 Prometheus 指标
 *
 * @returns 指标文本
 */
export function getMetrics() {
  return request.get<string>('/api/v1/metrics', {
    responseType: 'text',
  })
}

/**
 * 格式化字节大小
 *
 * @param bytes 字节数
 * @returns 格式化后的字符串
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 格式化百分比
 *
 * @param value 数值
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

/**
 * 获取状态类型
 *
 * @param status 状态值
 * @returns Element Plus 标签类型
 */
export function getStatusType(status: string): 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'healthy' || status === 'ready' || status === 'connected') {
    return 'success'
  }
  if (status === 'unhealthy' || status === 'not ready') {
    return 'danger'
  }
  return 'info'
}
