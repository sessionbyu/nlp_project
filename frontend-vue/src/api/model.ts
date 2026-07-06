import { request } from './request'
import type { ModelInfo, ModelDetail, ModelStats } from '@/types/model'

/**
 * 获取模型列表
 */
export async function getModels(): Promise<ModelInfo[]> {
  return request.get('/api/v1/models')
}

/**
 * 获取模型详情
 */
export async function getModelDetail(modelKey: string): Promise<ModelDetail> {
  return request.get(`/api/v1/models/${modelKey}`)
}

/**
 * 启动模型
 */
export async function startModel(modelKey: string): Promise<void> {
  return request.post(`/api/v1/models/${modelKey}/start`)
}

/**
 * 停止模型
 */
export async function stopModel(modelKey: string): Promise<void> {
  return request.post(`/api/v1/models/${modelKey}/stop`)
}

/**
 * 重新加载模型
 */
export async function reloadModel(modelKey: string): Promise<void> {
  return request.post(`/api/v1/models/${modelKey}/reload`)
}

/**
 * 清空模型缓存
 */
export async function clearModelCache(modelKey: string): Promise<void> {
  return request.post(`/api/v1/models/${modelKey}/cache/clear`)
}

/**
 * 获取模型统计信息
 */
export async function getModelStats(modelKey: string): Promise<ModelStats> {
  return request.get(`/api/v1/models/${modelKey}/stats`)
}

/**
 * 获取所有模型的统计信息
 */
export async function getAllModelsStats(): Promise<Record<string, ModelStats>> {
  return request.get('/api/v1/models/stats')
}
