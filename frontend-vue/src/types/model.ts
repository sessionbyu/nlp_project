/**
 * 模型管理相关类型定义
 */

export interface ModelInfo {
  key: string
  name: string
  description: string
  version: string
  status: 'active' | 'stopped' | 'error'
  calls: number
  avgTime: number
  createdAt: string
  updatedAt: string
}

export interface ModelDetail extends ModelInfo {
  config: Record<string, any>
  metrics: {
    accuracy?: number
    precision?: number
    recall?: number
    f1Score?: number
  }
  lastUsed: string
  size: string
}

export interface ModelStats {
  totalCalls: number
  successRate: number
  avgResponseTime: number
  callsByDay: Array<{
    date: string
    count: number
  }>
}

export interface ReloadModelParams {
  modelKey: string
  force?: boolean
}
