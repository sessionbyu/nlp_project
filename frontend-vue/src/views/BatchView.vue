<template>
  <div class="batch-view">
    <div class="page-header">
      <h1>📦 批量文本预测</h1>
      <p class="subtitle">一次性预测多条文本，提高效率</p>
    </div>

    <el-card class="config-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Setting /></el-icon>
            批量配置
          </span>
        </div>
      </template>

      <el-form :model="form" label-position="top">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="选择模型">
              <el-select
                v-model="form.modelKey"
                placeholder="选择模型"
                style="width: 100%"
                :disabled="isProcessing"
              >
                <el-option label="🤖 BERT（准确度高）" value="bert" />
                <el-option label="⚡ VADER（速度快）" value="vader" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8">
            <el-form-item label="每批处理数量">
              <el-input-number
                v-model="form.batchSize"
                :min="1"
                :max="100"
                :disabled="isProcessing"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8">
            <el-form-item label="处理模式">
              <el-radio-group v-model="form.useAsync" :disabled="isProcessing">
                <el-radio-button :value="false">同步</el-radio-button>
                <el-radio-button :value="true">异步任务</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="input-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Edit /></el-icon>
            文本输入
          </span>
          <div class="header-actions">
            <el-button
              type="text"
              @click="handleClear"
              :disabled="isProcessing || !form.texts.length"
            >
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
            <el-button
              type="primary"
              plain
              @click="handleLoadExample"
              :disabled="isProcessing"
            >
              <el-icon><Document /></el-icon>
              加载示例
            </el-button>
          </div>
        </div>
      </template>

      <div class="text-input-wrapper">
        <el-input
          v-model="textInput"
          type="textarea"
          :rows="12"
          placeholder="请输入要批量预测的文本，每行一条...&#10;&#10;示例：&#10;今天天气真好，心情很愉快&#10;这个产品质量太差了，非常失望&#10;服务态度很好，下次还会再来"
          :disabled="isProcessing"
          @input="handleTextInput"
        />
        <div class="input-stats">
          <el-tag type="info" effect="plain">
            共 {{ form.texts.length }} 条文本
          </el-tag>
          <el-tag v-if="form.texts.length > 0" type="success" effect="plain">
            预计耗时: {{ estimatedTime }}秒
          </el-tag>
        </div>
      </div>
    </el-card>

    <div class="action-section">
      <el-button
        type="primary"
        size="large"
        :loading="isProcessing"
        @click="handleBatchPredict"
        :disabled="!canSubmit"
        class="predict-btn"
      >
        <el-icon v-if="!isProcessing"><MagicStick /></el-icon>
        {{ isProcessing ? '批量预测中...' : '🚀 开始批量预测' }}
      </el-button>

      <el-button
        v-if="isProcessing"
        type="danger"
        size="large"
        @click="handleCancel"
        class="cancel-btn"
      >
        <el-icon><Close /></el-icon>
        取消
      </el-button>
    </div>

    <transition name="slide-up">
      <div v-if="isProcessing" class="progress-card fade-in">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Loading /></el-icon>
                处理进度
              </span>
              <el-tag :type="progressType" effect="dark">
                {{ progress.current }} / {{ progress.total }}
              </el-tag>
            </div>
          </template>

          <div class="progress-content">
            <el-progress
              :percentage="progress.percentage"
              :color="progressColor"
              :stroke-width="20"
              :show-text="true"
            />
            <div class="progress-stats">
              <div class="stat-item">
                <span class="stat-label">✅ 成功</span>
                <span class="stat-value success">{{ progress.success }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">❌ 失败</span>
                <span class="stat-value danger">{{ progress.failed }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">⏱️ 耗时</span>
                <span class="stat-value">{{ progress.elapsedTime }}秒</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </transition>

    <transition name="slide-up">
      <div v-if="result" class="result-card fade-in">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Trophy /></el-icon>
                预测结果
              </span>
              <el-button
                type="success"
                @click="handleExport"
                :disabled="!result.results.length"
              >
                <el-icon><Download /></el-icon>
                导出 CSV
              </el-button>
            </div>
          </template>

          <div class="result-summary">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="summary-item total">
                  <div class="summary-label">总计</div>
                  <div class="summary-value">{{ result.total }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="summary-item success">
                  <div class="summary-label">成功</div>
                  <div class="summary-value">{{ result.success }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="summary-item danger">
                  <div class="summary-label">失败</div>
                  <div class="summary-value">{{ result.failed }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="summary-item info">
                  <div class="summary-label">成功率</div>
                  <div class="summary-value">
                    {{ result.total > 0 ? ((result.success / result.total) * 100).toFixed(1) : 0 }}%
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="result-list">
            <div class="result-list-header">
              <span>详细结果</span>
              <el-checkbox v-model="showAllResults">显示全部</el-checkbox>
            </div>

            <el-scrollbar height="400px">
              <div
                v-for="(item, index) in displayResults"
                :key="index"
                class="result-item"
                :class="{ failed: !item.success }"
              >
                <div class="result-header" @click="toggleResult(index)">
                  <div class="result-index">{{ index + 1 }}</div>
                  <div class="result-text">
                    {{ item.text }}
                  </div>
                  <div class="result-status">
                    <el-tag
                      v-if="item.success"
                      :type="getLabelType(item.result!.label)"
                      size="small"
                    >
                      {{ item.result!.label }}
                    </el-tag>
                    <el-tag v-else type="danger" size="small">
                      失败
                    </el-tag>
                  </div>
                  <div class="result-expand">
                    <el-icon>
                      <ArrowDown v-if="expandedResults.includes(index)" />
                      <ArrowRight v-else />
                    </el-icon>
                  </div>
                </div>

                <el-collapse-transition>
                  <div v-if="item.success && expandedResults.includes(index)" class="result-detail">
                    <div class="detail-content">
                      <div class="detail-row">
                        <span class="detail-label">置信度</span>
                        <el-progress
                          :percentage="Math.round(item.result!.score * 100)"
                          :color="getScoreColor(item.result!.score)"
                          :stroke-width="8"
                          :show-text="true"
                        />
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">模型</span>
                        <el-tag size="small" type="info">
                          {{ item.result!.model_key.toUpperCase() }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </el-collapse-transition>

                <el-collapse-transition>
                  <div v-if="!item.success && expandedResults.includes(index)" class="result-detail error">
                    <div class="detail-content">
                      <div class="detail-row">
                        <span class="detail-label">错误信息</span>
                        <el-text type="danger">{{ item.error }}</el-text>
                      </div>
                    </div>
                  </div>
                </el-collapse-transition>
              </div>
            </el-scrollbar>
          </div>

          <div v-if="!showAllResults && result.results.length > 20" class="show-more">
            <el-button type="text" @click="showAllResults = true">
              显示全部 {{ result.results.length }} 条结果
            </el-button>
          </div>
        </el-card>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Edit,
  Delete,
  Document,
  MagicStick,
  Close,
  Loading,
  Trophy,
  Download,
  ArrowDown,
  ArrowRight,
} from '@element-plus/icons-vue'
import { batchPredict, asyncBatchPredict, getTaskStatus, type BatchPredictResponse } from '@/api'
import { useTaskStore } from '@/stores/task'
import { useWebSocket } from '@/composables/useWebSocket'

const router = useRouter()
const taskStore = useTaskStore()

interface Progress {
  current: number
  total: number
  success: number
  failed: number
  percentage: number
  elapsedTime: number
}

const form = ref({
  modelKey: 'bert',
  batchSize: 10,
  texts: [] as string[],
  useAsync: false, // 是否使用异步任务
})

const textInput = ref('')
const isProcessing = ref(false)
const cancelRequested = ref(false)
const result = ref<BatchPredictResponse | null>(null)
const currentTaskId = ref<string | null>(null)
const progress = ref<Progress>({
  current: 0,
  total: 0,
  success: 0,
  failed: 0,
  percentage: 0,
  elapsedTime: 0,
})
const expandedResults = ref<number[]>([])
const showAllResults = ref(false)
const startTime = ref(0)
let timer: number | null = null

const exampleTexts = [
  '今天天气真好，阳光明媚，心情非常愉快',
  '这个产品质量太差了，用了一次就坏了，非常失望',
  '服务态度很好，客服耐心解答，下次还会再来',
  '电影情节紧凑，演员演技在线，强烈推荐',
  '配送速度太慢了，等了一个星期才到',
  '性价比很高，功能齐全，物超所值',
  '设计很漂亮，材质也不错，很满意',
  '操作太复杂了，说明书也看不懂，用户体验差',
  '味道很棒，食材新鲜，下次还来',
  '噪音太大，严重影响休息，不建议购买',
]

const canSubmit = computed(() => {
  return form.value.texts.length > 0 && !isProcessing.value
})

const estimatedTime = computed(() => {
  const count = form.value.texts.length
  if (count === 0) return 0
  // 预估每条文本 0.5 秒
  return Math.ceil(count * 0.5)
})

const displayResults = computed(() => {
  if (!result.value) return []
  return showAllResults.value
    ? result.value.results
    : result.value.results.slice(0, 20)
})

const progressType = computed(() => {
  const pct = progress.value.percentage
  if (pct < 30) return 'warning'
  if (pct < 70) return 'primary'
  if (pct < 100) return 'success'
  return 'success'
})

const progressColor = computed(() => {
  if (progress.value.failed > 0) return ['#E87C7C', '#E8B87C', '#68C3A0']
  return '#68C3A0'
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

function handleTextInput() {
  const texts = textInput.value
    .split('\n')
    .map(t => t.trim())
    .filter(t => t.length > 0)
  form.value.texts = texts
}

function handleClear() {
  textInput.value = ''
  form.value.texts = []
  result.value = null
  expandedResults.value = []
}

function handleLoadExample() {
  textInput.value = exampleTexts.join('\n')
  handleTextInput()
  ElMessage.success('已加载示例文本')
}

async function handleBatchPredict() {
  if (form.value.texts.length === 0) {
    ElMessage.warning('请先输入文本')
    return
  }

  try {
    cancelRequested.value = false
    isProcessing.value = true
    result.value = null
    startTime.value = Date.now()

    // 开始计时
    timer = window.setInterval(() => {
      progress.value.elapsedTime = Math.floor((Date.now() - startTime.value) / 1000)
    }, 1000)

    if (form.value.useAsync) {
      // 使用异步任务 + WebSocket
      const asyncResponse = await asyncBatchPredict({
        texts: form.value.texts,
        model_key: form.value.modelKey,
      })

      currentTaskId.value = asyncResponse.task_id

      // 添加到任务管理
      taskStore.startPolling(asyncResponse.task_id, 2000)

      // 建立 WebSocket 连接
      const { onMessage, disconnect } = useWebSocket(asyncResponse.task_id, {
        onMessage: (message) => {
          if (message.type === 'progress') {
            // 更新进度
            progress.value = {
              current: message.current || 0,
              total: message.total || form.value.texts.length,
              success: progress.value.success,
              failed: progress.value.failed,
              percentage: message.progress_percent || 0,
              elapsedTime: progress.value.elapsedTime,
            }
          } else if (message.type === 'notification') {
            // 显示通知
            if (message.notification_type === 'success') {
              ElMessage.success(message.message)
            } else if (message.notification_type === 'error') {
              ElMessage.error(message.message)
            }
          }
        },
        onConnected: () => {
          ElMessage.info('已连接到任务，等待处理...')
        },
        onDisconnected: () => {
          console.log('WebSocket 连接断开')
        },
      })

      // 等待任务完成（通过轮询）
      const checkTask = setInterval(() => {
        const task = taskStore.getTask(asyncResponse.task_id)
        if (task && (task.status === 'SUCCESS' || task.status === 'FAILURE')) {
          clearInterval(checkTask)
          disconnect()
          taskStore.stopPolling(asyncResponse.task_id)

          if (task.status === 'SUCCESS' && task.result) {
            result.value = task.result as BatchPredictResponse
            ElMessage.success(
              `批量预测完成：成功 ${task.result.success || 0} 条，失败 ${task.result.failed || 0} 条`
            )
          } else {
            ElMessage.error(task.error || '批量预测失败')
          }

          isProcessing.value = false
          currentTaskId.value = null
          if (timer) {
            clearInterval(timer)
            timer = null
          }
        }
      }, 2000)
    } else {
      // 同步模式
      const response = await batchPredict({
        texts: form.value.texts,
        model_key: form.value.modelKey,
      })

      if (cancelRequested.value) {
        ElMessage.info('批量预测已取消')
        return
      }

      result.value = response
      ElMessage.success(
        `批量预测完成：成功 ${response.success} 条，失败 ${response.failed} 条`
      )
    }
  } catch (error: any) {
    if (!cancelRequested.value) {
      ElMessage.error(error.message || '批量预测失败')
    }
  } finally {
    if (!form.value.useAsync) {
      isProcessing.value = false
    }
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }
}

function handleCancel() {
  cancelRequested.value = true
  isProcessing.value = false

  // 如果有异步任务，取消任务
  if (currentTaskId.value) {
    taskStore.cancelTask(currentTaskId.value).catch(() => {})
    currentTaskId.value = null
  }

  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function toggleResult(index: number) {
  const idx = expandedResults.value.indexOf(index)
  if (idx > -1) {
    expandedResults.value.splice(idx, 1)
  } else {
    expandedResults.value.push(index)
  }
}

function handleExport() {
  if (!result.value) return

  const headers = ['ID', '文本', '标签', '置信度', '模型', '状态']
  const rows = result.value.results.map((item, index) => {
    if (item.success) {
      return [
        (index + 1).toString(),
        item.text,
        item.result!.label,
        formatScore(item.result!.score),
        item.result!.model_key.toUpperCase(),
        '成功',
      ]
    } else {
      return [
        (index + 1).toString(),
        item.text,
        '错误',
        '0',
        '-',
        '失败',
      ]
    }
  })

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
  ].join('\n')

  const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `batch_predict_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success('导出成功')
}

function getLabelType(label: string): 'success' | 'danger' | 'info' {
  if (label.includes('正面') || label.toLowerCase().includes('positive')) {
    return 'success'
  }
  if (label.includes('负面') || label.toLowerCase().includes('negative')) {
    return 'danger'
  }
  return 'info'
}

function getScoreColor(score: number): string {
  if (score >= 0.7) return '#68C3A0'
  if (score >= 0.5) return '#E8B87C'
  return '#E87C7C'
}
</script>

<style scoped lang="scss">
.batch-view {
  .page-header {
    margin-bottom: 32px;
    text-align: center;

    h1 {
      font-size: 32px;
      font-weight: 700;
      background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
    }

    .subtitle {
      font-size: 16px;
      color: #5A6878;
    }
  }

  .config-card,
  .input-card,
  .progress-card,
  .result-card {
    margin-bottom: 24px;
    border-radius: 16px;
    transition: all 0.3s ease;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 16px;

      .header-icon {
        color: #5B9A8B;
      }
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }

  .input-card {
    .text-input-wrapper {
      margin-bottom: 16px;
    }

    .input-stats {
      display: flex;
      gap: 12px;
    }
  }

  .action-section {
    margin-bottom: 24px;
    display: flex;
    gap: 16px;
    justify-content: center;

    .predict-btn {
      min-width: 200px;
      height: 52px;
      font-size: 18px;
      font-weight: 600;
      border-radius: 26px;
      background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
      border: none;
      box-shadow: 0 8px 16px rgba(91, 154, 139, 0.3);
      transition: all 0.3s ease;

      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(91, 154, 139, 0.4);
      }

      &:disabled {
        opacity: 0.6;
      }
    }

    .cancel-btn {
      min-width: 140px;
      height: 52px;
      font-size: 16px;
      font-weight: 600;
      border-radius: 26px;
    }
  }

  .progress-card {
    .progress-content {
      .progress-stats {
        display: flex;
        gap: 24px;
        margin-top: 24px;
        padding: 20px;
        background: #F8F9FA;
        border-radius: 12px;

        .stat-item {
          flex: 1;
          text-align: center;

          .stat-label {
            font-size: 14px;
            color: #5A6878;
            margin-bottom: 8px;
          }

          .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #303133;

            &.success {
              color: #67c23a;
            }

            &.danger {
              color: #f56c6c;
            }
          }
        }
      }
    }
  }

  .result-card {
    .result-summary {
      margin-bottom: 24px;

      .summary-item {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;

        &.total {
          background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
          color: white;
        }

        &.success {
          background: linear-gradient(135deg, #7BA3C4 0%, #6B93B4 100%);
          color: white;
        }

        &.danger {
          background: linear-gradient(135deg, #E8A87C 0%, #D4906A 100%);
          color: white;
        }

        &.info {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          color: white;
        }

        .summary-label {
          font-size: 14px;
          opacity: 0.9;
          margin-bottom: 8px;
        }

        .summary-value {
          font-size: 32px;
          font-weight: 700;
        }
      }
    }

    .result-list {
      .result-list-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding: 0 8px;
      }

      .result-item {
        margin-bottom: 12px;
        border-radius: 8px;
        overflow: hidden;
        background: #F8F9FA;
        transition: all 0.3s ease;
        border: 2px solid transparent;

        &:hover {
          background: #f0f2f5;
        }

        &.failed {
          border-color: #f56c6c;
          background: #fef0f0;
        }

        .result-header {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          cursor: pointer;
          transition: all 0.3s ease;

          &:hover {
            background: rgba(91, 154, 139, 0.05);
          }

          .result-index {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            flex-shrink: 0;
          }

          .result-text {
            flex: 1;
            font-size: 14px;
            color: #303133;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .result-status {
            flex-shrink: 0;
          }

          .result-expand {
            flex-shrink: 0;
            color: #8A98A8;
            transition: transform 0.3s ease;
          }
        }

        .result-detail {
          padding: 0 16px 16px 60px;

          &.error {
            background: #fef0f0;
            padding: 16px;
          }

          .detail-content {
            .detail-row {
              display: flex;
              align-items: center;
              gap: 16px;
              margin-bottom: 12px;

              &:last-child {
                margin-bottom: 0;
              }

              .detail-label {
                min-width: 80px;
                font-size: 14px;
                color: #5A6878;
              }

              .el-progress {
                flex: 1;
              }
            }
          }
        }
      }
    }

    .show-more {
      margin-top: 16px;
      text-align: center;
    }
  }
}

// 动画
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.4s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

// 响应式
@media (max-width: 768px) {
  .batch-view {
    .page-header {
      h1 {
        font-size: 24px;
      }

      .subtitle {
        font-size: 14px;
      }
    }

    .action-section {
      flex-direction: column;

      .predict-btn,
      .cancel-btn {
        width: 100%;
      }
    }

    .progress-card {
      .progress-stats {
        flex-direction: column;
        gap: 12px;
      }
    }

    .result-card {
      .result-summary {
        .summary-item {
          margin-bottom: 12px;
        }
      }

      .result-list {
        .result-item {
          .result-header {
            flex-wrap: wrap;

            .result-text {
              order: 1;
              width: 100%;
              margin-top: 8px;
            }

            .result-index {
              order: 0;
            }

            .result-status {
              order: 2;
            }

            .result-expand {
              order: 3;
            }
          }

          .result-detail {
            padding-left: 16px;
          }
        }
      }
    }
  }
}
</style>
