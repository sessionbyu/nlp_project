/**
 * 批量预测 API
 *
 * 功能：
 * 1. 同步批量预测
 * 2. 异步批量预测（通过Celery任务）
 */

import { request } from './request'

/**
 * 批量预测请求参数
 */
export interface BatchPredictRequest {
  texts: string[]
  model_key?: string
  use_async?: boolean // 是否使用异步任务
}

/**
 * 批量预测单项结果
 */
export interface BatchPredictItem {
  text: string
  success: boolean
  result?: {
    label: string
    score: number
    model_key: string
  }
  error?: string
}

/**
 * 批量预测响应
 */
export interface BatchPredictResponse {
  results: BatchPredictItem[]
  total: number
  success: number
  failed: number
}

/**
 * 同步批量预测
 *
 * @param data - 批量预测请求参数
 * @returns 批量预测结果
 */
export function batchPredict(data: BatchPredictRequest) {
  return request.post<BatchPredictResponse>('/api/v1/batch-predict', data)
}

/**
 * 异步批量预测（通过Celery任务）
 *
 * @param data - 批量预测请求参数
 * @returns 任务ID
 */
export function asyncBatchPredict(data: BatchPredictRequest) {
  return request.post<{ task_id: string; message: string }>('/api/v1/batch-predict/async', data)
}
