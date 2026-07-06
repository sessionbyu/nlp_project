/**
 * 任务状态管理
 *
 * 功能：
 * 1. 任务列表管理
 * 2. 任务状态追踪
 * 3. 任务取消
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getTaskStatus,
  cancelTask as cancelTaskApi,
  getActiveTasks,
  type TaskStatusResponse,
} from '@/api/task'

export const useTaskStore = defineStore('task', () => {
  // 状态
  const tasks = ref<Map<string, TaskStatusResponse>>(new Map())
  const activeTasks = ref<TaskStatusResponse[]>([])
  const pollingIntervals = ref<Map<string, NodeJS.Timeout>>(new Map())

  // 计算属性
  const taskList = computed(() => Array.from(tasks.value.values()))

  const pendingTasks = computed(() =>
    taskList.value.filter((t) => t.status === 'PENDING' || t.status === 'STARTED' || t.status === 'PROGRESS')
  )

  const completedTasks = computed(() =>
    taskList.value.filter((t) => t.status === 'SUCCESS' || t.status === 'FAILURE')
  )

  // 获取活跃任务列表
  const fetchActiveTasks = async () => {
    try {
      const response = await getActiveTasks()
      activeTasks.value = response.active_tasks

      // 同步到 tasks map
      response.active_tasks.forEach((task) => {
        tasks.value.set(task.task_id, task)
      })
    } catch (error) {
      console.error('获取活跃任务列表失败:', error)
    }
  }

  // 查询任务状态
  const fetchTaskStatus = async (taskId: string) => {
    try {
      const status = await getTaskStatus(taskId)
      tasks.value.set(taskId, status)

      // 如果任务完成，停止轮询
      if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
        stopPolling(taskId)
      }

      return status
    } catch (error) {
      console.error('获取任务状态失败:', error)
      throw error
    }
  }

  // 开始轮询任务状态
  const startPolling = (taskId: string, interval: number = 2000) => {
    // 如果已经在轮询，先停止
    if (pollingIntervals.value.has(taskId)) {
      stopPolling(taskId)
    }

    // 立即查询一次
    fetchTaskStatus(taskId)

    // 设置定时轮询
    const timer = setInterval(() => {
      fetchTaskStatus(taskId)
    }, interval)

    pollingIntervals.value.set(taskId, timer)
  }

  // 停止轮询任务状态
  const stopPolling = (taskId: string) => {
    const timer = pollingIntervals.value.get(taskId)
    if (timer) {
      clearInterval(timer)
      pollingIntervals.value.delete(taskId)
    }
  }

  // 取消任务
  const cancelTask = async (taskId: string) => {
    try {
      await cancelTaskApi(taskId)
      stopPolling(taskId)

      // 更新任务状态
      const task = tasks.value.get(taskId)
      if (task) {
        tasks.value.set(taskId, {
          ...task,
          status: 'FAILURE',
          error: '用户取消',
        })
      }

      return true
    } catch (error) {
      console.error('取消任务失败:', error)
      throw error
    }
  }

  // 获取任务
  const getTask = (taskId: string) => {
    return tasks.value.get(taskId)
  }

  // 清空任务
  const clearTask = (taskId: string) => {
    stopPolling(taskId)
    tasks.value.delete(taskId)
  }

  // 清空所有任务
  const clearAllTasks = () => {
    // 停止所有轮询
    pollingIntervals.value.forEach((_, taskId) => {
      stopPolling(taskId)
    })

    // 清空任务
    tasks.value.clear()
    activeTasks.value = []
  }

  return {
    // 状态
    tasks,
    activeTasks,
    // 计算属性
    taskList,
    pendingTasks,
    completedTasks,
    // 方法
    fetchActiveTasks,
    fetchTaskStatus,
    startPolling,
    stopPolling,
    cancelTask,
    getTask,
    clearTask,
    clearAllTasks,
  }
})
