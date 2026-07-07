/**
 * 文件上传 API
 *
 * 功能：
 * 1. 上传文件并提取文本
 * 2. 批量分析
 * 3. 异步分析
 */

import { request } from './request'

/**
 * 文件上传响应
 */
export interface FileUploadResponse {
  filename: string
  file_size: number
  file_type: string
  texts: string[]
  text_count: number
  message: string
}

/**
 * 批量分析响应
 */
export interface BatchAnalyzeResponse {
  task_id?: string
  results: Array<{
    text: string
    success: boolean
    result?: {
      label: string
      score: number
      model_key: string
    }
    error?: string
  }>
  total: number
  success: number
  failed: number
}

/**
 * 异步分析响应
 */
export interface AsyncAnalyzeResponse {
  task_id: string
  message: string
}

/**
 * 上传文件并提取文本
 *
 * @param file - 文件对象
 * @returns 提取的文本列表
 */
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post<FileUploadResponse>('/api/v1/upload/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/**
 * 批量分析（同步）
 *
 * @param texts - 文本列表
 * @param modelKey - 模型key
 * @returns 批量分析结果
 */
export function batchAnalyze(data: {
  texts: string[]
  model_key?: string
}) {
  return request.post<BatchAnalyzeResponse>('/api/v1/upload/batch-analyze', data)
}

/**
 * 异步分析（后台任务）
 *
 * @param texts - 文本列表
 * @param modelKey - 模型key
 * @returns 任务ID
 */
export function asyncAnalyze(data: {
  texts: string[]
  model_key?: string
}) {
  return request.post<AsyncAnalyzeResponse>('/api/v1/upload/async-analyze', data)
}
