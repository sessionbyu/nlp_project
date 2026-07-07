<template>
  <div class="tasks-view">
    <div class="page-header">
      <h1>📋 任务管理</h1>
      <p class="subtitle">查看和管理异步任务</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="List"
          label="活跃任务"
          :value="activeTaskCount"
          color-type="primary"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="Loading"
          label="进行中"
          :value="runningTaskCount"
          color-type="warning"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="CircleCheck"
          label="已完成"
          :value="completedTaskCount"
          color-type="success"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="CircleClose"
          label="失败"
          :value="failedTaskCount"
          color-type="danger"
          size="medium"
        />
      </el-col>
    </el-row>

    <!-- 过滤器 -->
    <el-card class="filter-card fade-in">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索任务ID..."
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-select
            v-model="statusFilter"
            placeholder="任务状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="等待中" value="PENDING" />
            <el-option label="进行中" value="STARTED" />
            <el-option label="进度" value="PROGRESS" />
            <el-option label="成功" value="SUCCESS" />
            <el-option label="失败" value="FAILURE" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="10">
          <div class="filter-actions">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button
              type="primary"
              plain
              @click="handleRefresh"
              :loading="refreshing"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 任务列表 -->
    <div class="task-list">
      <transition name="slide-up">
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <el-empty description="暂无任务">
            <el-button type="primary" @click="goToUpload">上传文件分析</el-button>
          </el-empty>
        </div>

        <div v-else class="task-items">
          <div
            v-for="task in filteredTasks"
            :key="task.task_id"
            class="task-item fade-in"
          >
            <el-card>
              <div class="task-header">
                <div class="task-info">
                  <div class="task-id">
                    <el-text type="info" size="small">ID:</el-text>
                    <el-text code>{{ task.task_id }}</el-text>
                  </div>
                  <div class="task-time">
                    <el-icon><Clock /></el-icon>
                    <el-text size="small" type="info">
                      {{ formatTime(task.timestamp) }}
                    </el-text>
                  </div>
                </div>
                <el-tag
                  :type="getStatusType(task.status)"
                  effect="dark"
                  size="large"
                >
                  <el-icon v-if="task.status === 'PROGRESS' || task.status === 'STARTED'">
                    <Loading />
                  </el-icon>
                  {{ getStatusText(task.status) }}
                </el-tag>
              </div>

              <!-- 进度条 -->
              <div v-if="task.status === 'PROGRESS' && task.progress" class="task-progress">
                <el-progress
                  :percentage="task.progress.total > 0
                    ? Math.round((task.progress.current / task.progress.total) * 100)
                    : 0"
                  :status="task.progress.total > 0 && task.progress.current >= task.progress.total ? 'success' : undefined"
                >
                  <template #default="{ percentage }">
                    <span class="progress-text">
                      {{ task.progress.current }} / {{ task.progress.total }}
                    </span>
                  </template>
                </el-progress>
              </div>

              <!-- 错误信息 -->
              <div v-if="task.error" class="task-error">
                <el-alert
                  :title="task.error"
                  type="error"
                  :closable="false"
                  show-icon
                />
              </div>

              <!-- 任务操作 -->
              <div class="task-actions">
                <el-button
                  v-if="task.status === 'PROGRESS' || task.status === 'STARTED'"
                  type="danger"
                  size="small"
                  @click="handleCancel(task.task_id)"
                  :loading="cancelling === task.task_id"
                >
                  <el-icon><CircleClose /></el-icon>
                  取消
                </el-button>

                <el-button
                  v-if="task.status === 'SUCCESS'"
                  type="primary"
                  size="small"
                  @click="handleViewResult(task.task_id)"
                >
                  <el-icon><View /></el-icon>
                  查看结果
                </el-button>

                <el-button
                  v-if="task.status === 'SUCCESS' && task.result"
                  type="success"
                  size="small"
                  @click="handleExportResult(task.task_id)"
                >
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>

                <el-button
                  size="small"
                  @click="handleViewDetails(task)"
                >
                  <el-icon><InfoFilled /></el-icon>
                  详情
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </transition>
    </div>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="600px"
    >
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务 ID">
            <el-text code>{{ selectedTask.task_id }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedTask.status)">
              {{ getStatusText(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedTask.progress" label="进度">
            {{ selectedTask.progress.current }} / {{ selectedTask.progress.total }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedTask.progress" label="进度状态">
            {{ selectedTask.progress.status }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedTask.result" label="结果">
            <el-text type="success">成功</el-text>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedTask.error" label="错误">
            <el-text type="danger">{{ selectedTask.error }}</el-text>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 结果预览 -->
        <div v-if="selectedTask.result && selectedTask.result.results" class="result-preview">
          <h4>结果预览</h4>
          <el-table :data="selectedTask.result.results.slice(0, 5)" max-height="300">
            <el-table-column
              prop="text"
              label="文本"
              min-width="200"
              show-overflow-tooltip
            />
            <el-table-column
              prop="result.label"
              label="标签"
              width="100"
            />
            <el-table-column
              prop="result.score"
              label="分数"
              width="100"
            />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ElMessage,
  ElMessageBox,
} from 'element-plus'
import {
  List,
  Loading,
  CircleCheck,
  CircleClose,
  Search,
  RefreshLeft,
  Refresh,
  Clock,
  View,
  Download,
  InfoFilled,
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { cancelTask } from '@/api/task'
import type { TaskStatusResponse } from '@/api/task'

const router = useRouter()
const taskStore = useTaskStore()

// 状态
const searchKeyword = ref('')
const statusFilter = ref('')
const detailDialogVisible = ref(false)
const selectedTask = ref<TaskStatusResponse | null>(null)
const cancelling = ref<string | null>(null)
const refreshing = ref(false)
let pollingTimer: NodeJS.Timeout | null = null

// 计算属性
const activeTaskCount = computed(() => taskStore.activeTasks.length)
const runningTaskCount = computed(() => taskStore.pendingTasks.length)
const completedTaskCount = computed(() => taskStore.completedTasks.length)

const failedTaskCount = computed(() =>
  taskStore.completedTasks.filter((t) => t.status === 'FAILURE').length
)

const filteredTasks = computed(() => {
  let tasks = taskStore.taskList

  // 按状态过滤
  if (statusFilter.value) {
    tasks = tasks.filter((t) => t.status === statusFilter.value)
  }

  // 按关键词搜索
  if (searchKeyword.value) {
    tasks = tasks.filter((t) =>
      t.task_id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  // 按时间倒序
  return tasks.sort((a, b) => {
    const timeA = new Date(a.timestamp || 0).getTime()
    const timeB = new Date(b.timestamp || 0).getTime()
    return timeB - timeA
  })
})

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    PENDING: 'info',
    STARTED: 'primary',
    PROGRESS: 'warning',
    SUCCESS: 'success',
    FAILURE: 'danger',
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    PENDING: '等待中',
    STARTED: '进行中',
    PROGRESS: '进度',
    SUCCESS: '成功',
    FAILURE: '失败',
  }
  return textMap[status] || status
}

// 格式化时间
const formatTime = (timestamp?: string | number) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 小于1小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000))
    return `${minutes}分钟前`
  }
  // 小于1天
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000))
    return `${hours}小时前`
  }
  // 大于1天
  return date.toLocaleString('zh-CN')
}

// 搜索
const handleSearch = () => {
  // 前端过滤已经实现，这里可以添加后端搜索
}

// 重置
const handleReset = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
}

// 刷新
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await taskStore.fetchActiveTasks()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 取消任务
const handleCancel = async (taskId: string) => {
  try {
    await ElMessageBox.confirm('确定要取消这个任务吗？', '确认取消', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    cancelling.value = taskId
    await taskStore.cancelTask(taskId)
    ElMessage.success('任务已取消')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  } finally {
    cancelling.value = null
  }
}

// 查看结果
const handleViewResult = (taskId: string) => {
  const task = taskStore.getTask(taskId)
  if (task?.result) {
    selectedTask.value = task
    detailDialogVisible.value = true
  }
}

// 导出结果
const handleExportResult = (taskId: string) => {
  const task = taskStore.getTask(taskId)
  if (task?.result?.results) {
    exportToCSV(task.result.results, `task-${taskId}.csv`)
  }
}

// 查看详情
const handleViewDetails = (task: TaskStatusResponse) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

// 跳转到上传页面
const goToUpload = () => {
  router.push('/batch')
}

// 导出 CSV
const exportToCSV = (results: any[], filename: string) => {
  const headers = ['文本', '情感标签', '置信度', '是否成功', '错误信息']
  const rows = results.map((r) => [
    r.text,
    r.result?.label || '',
    r.result?.score ? `${(r.result.score * 100).toFixed(1)}%` : '',
    r.success ? '是' : '否',
    r.error || '',
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
  ].join('\n')

  const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)

  ElMessage.success('导出成功')
}

// 轮询活跃任务
const startPolling = () => {
  // 立即查询一次
  taskStore.fetchActiveTasks()

  // 每5秒查询一次
  pollingTimer = setInterval(() => {
    taskStore.fetchActiveTasks()
  }, 5000)
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 生命周期
onMounted(() => {
  taskStore.fetchActiveTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.tasks-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.stats-row {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-actions {
    display: flex;
    gap: 8px;
  }
}

.task-list {
  min-height: 400px;
}

.empty-state {
  padding: 60px 0;
}

.task-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-item {
  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .task-info {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .task-id {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .task-time {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .task-progress {
    margin: 16px 0;

    .progress-text {
      font-weight: 600;
    }
  }

  .task-error {
    margin: 16px 0;
  }

  .task-actions {
    margin-top: 16px;
    display: flex;
    gap: 8px;
  }
}

.task-detail {
  .result-preview {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
    }
  }
}
</style>
