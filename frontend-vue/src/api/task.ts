/**
 * 任务管理 API
 *
 * 功能：
 * 1. 查询任务状态
 * 2. 获取任务结果
 * 3. 取消任务
 * 4. 列出活跃任务
 */

import { request } from './request'

/**
 * 任务状态响应
 */
export interface TaskStatusResponse {
  task_id: string
  status: 'PENDING' | 'STARTED' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'
  progress?: {
    current: number
    total: number
    status: string
  }
  result?: any
  error?: string
}

/**
 * 任务列表响应
 */
export interface TaskListResponse {
  active_tasks: TaskStatusResponse[]
}

/**
 * 查询任务状态
 *
 * @param taskId - 任务ID
 * @returns 任务状态
 */
export function getTaskStatus(taskId: string) {
  return request.get<TaskStatusResponse>(`/api/v1/tasks/${taskId}`)
}

/**
 * 取消任务
 *
 * @param taskId - 任务ID
 * @returns 取消结果
 */
export function cancelTask(taskId: string) {
  return request.post<{ message: string }>(`/api/v1/tasks/${taskId}/cancel`)
}

/**
 * 获取活跃任务列表
 *
 * @returns 活跃任务列表
 */
export function getActiveTasks() {
  return request.get<TaskListResponse>('/api/v1/tasks/')
}
