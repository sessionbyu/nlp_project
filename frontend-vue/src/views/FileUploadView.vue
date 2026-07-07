<template>
  <div class="file-upload-view">
    <div class="page-header">
      <h1>📁 文件上传分析</h1>
      <p class="subtitle">上传 CSV、Excel、JSON 或文本文件进行批量情感分析</p>
    </div>

    <!-- 文件上传区域 -->
    <el-card class="upload-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Upload /></el-icon>
            选择文件
          </span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        :action="uploadUrl"
        :headers="headers"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :on-remove="handleRemove"
        :file-list="fileList"
        :limit="1"
        accept=".csv,.xlsx,.xls,.txt,.json"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            <el-tag type="info" size="small" effect="plain">CSV</el-tag>
            <el-tag type="info" size="small" effect="plain">Excel</el-tag>
            <el-tag type="info" size="small" effect="plain">JSON</el-tag>
            <el-tag type="info" size="small" effect="plain">TXT</el-tag>
            <div class="upload-limit">最大文件大小: 50MB</div>
          </div>
        </template>
      </el-upload>
    </el-card>

    <!-- 配置选项 -->
    <el-card v-if="uploadedFile" class="config-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Setting /></el-icon>
            分析配置
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
            <el-form-item label="文本列名（可选）">
              <el-input
                v-model="form.textColumn"
                placeholder="留空自动检测"
                :disabled="isProcessing"
              >
                <template #prepend>列名</template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 文本预览 -->
    <el-card v-if="extractedTexts.length > 0" class="preview-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><View /></el-icon>
            文本预览
          </span>
          <el-tag type="info" effect="plain">
            共 {{ extractedTexts.length }} 条文本
          </el-tag>
        </div>
      </template>

      <div class="text-preview">
        <div
          v-for="(text, index) in previewTexts"
          :key="index"
          class="text-item"
        >
          <el-text line-clamp="2">{{ text }}</el-text>
        </div>
        <div v-if="extractedTexts.length > previewCount" class="more-text">
          ... 还有 {{ extractedTexts.length - previewCount }} 条文本
        </div>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div v-if="extractedTexts.length > 0" class="action-section">
      <el-button
        type="primary"
        size="large"
        :loading="isProcessing"
        @click="handleBatchAnalyze"
        :disabled="!canSubmit"
        class="predict-btn"
      >
        <el-icon v-if="!isProcessing"><MagicStick /></el-icon>
        {{ isProcessing ? '分析中...' : '🚀 开始批量分析' }}
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

      <el-button
        v-if="!isProcessing && extractedTexts.length > 0"
        size="large"
        @click="handleReset"
      >
        <el-icon><RefreshLeft /></el-icon>
        重新上传
      </el-button>
    </div>

    <!-- 进度条 -->
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

    <!-- 分析结果 -->
    <transition name="slide-up">
      <div v-if="result" class="result-card fade-in">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Trophy /></el-icon>
                分析结果
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

          <el-table
            :data="result.results.slice(0, 100)"
            style="width: 100%"
            max-height="500"
          >
            <el-table-column
              type="index"
              label="#"
              width="60"
            />
            <el-table-column
              prop="text"
              label="文本"
              min-width="300"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <el-text line-clamp="2">{{ row.text }}</el-text>
              </template>
            </el-table-column>
            <el-table-column
              prop="result.label"
              label="情感标签"
              width="120"
            >
              <template #default="{ row }">
                <el-tag
                  v-if="row.success && row.result"
                  :type="getLabelType(row.result.label)"
                  effect="dark"
                >
                  {{ getLabelText(row.result.label) }}
                </el-tag>
                <el-tag v-else type="info" effect="plain">-</el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="result.score"
              label="置信度"
              width="120"
            >
              <template #default="{ row }">
                <span v-if="row.success && row.result">
                  {{ (row.result.score * 100).toFixed(1) }}%
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="error"
              label="错误信息"
              width="200"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <el-text v-if="row.error" type="danger" size="small">
                  {{ row.error }}
                </el-text>
                <el-text v-else type="info">-</el-text>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="result.results.length > 100" class="table-tip">
            <el-text type="info" size="small">
              仅显示前 100 条结果，完整结果请导出查看
            </el-text>
          </div>
        </el-card>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElUpload } from 'element-plus'
import { Upload, UploadFilled, Setting, View, MagicStick, Close, RefreshLeft, Download } from '@element-plus/icons-vue'
import { useTaskStore } from '@/stores/task'
import { uploadFile, batchAnalyze, type BatchAnalyzeResponse } from '@/api/upload'
import type { UploadFile } from 'element-plus'

const route = useRoute()
const taskStore = useTaskStore()

// 状态
const fileList = ref<UploadFile[]>([])
const uploadedFile = ref<File | null>(null)
const extractedTexts = ref<string[]>([])
const isProcessing = ref(false)
const result = ref<BatchAnalyzeResponse | null>(null)
const startTime = ref<number>(0)

// 表单
const form = ref({
  modelKey: 'bert',
  textColumn: '',
})

// 预览配置
const previewCount = 10

// 进度
const progress = ref({
  current: 0,
  total: 0,
  success: 0,
  failed: 0,
  elapsedTime: 0,
  percentage: 0,
})

// 计算属性
const uploadUrl = computed(() => {
  // 使用环境变量或默认相对路径 /api，通过 nginx 代理到后端
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  // 确保不以 / 结尾，避免双斜杠
  const cleanBase = baseURL.replace(/\/$/, '')
  return `${cleanBase}/api/v1/upload/file`
})

const headers = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

const previewTexts = computed(() => {
  return extractedTexts.value.slice(0, previewCount)
})

const canSubmit = computed(() => {
  return extractedTexts.value.length > 0 && !isProcessing.value
})

const progressType = computed(() => {
  if (progress.value.percentage >= 100) return 'success'
  if (progress.value.failed > 0) return 'warning'
  return 'primary'
})

const progressColor = computed(() => {
  if (progress.value.percentage >= 100) return '#67c23a'
  if (progress.value.failed > 0) return '#e6a23c'
  return '#409eff'
})

// 上传前验证
const beforeUpload = (file: File) => {
  const maxSize = 50 * 1024 * 1024 // 50MB

  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }

  // 验证文件类型
  const validTypes = [
    'text/csv',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'application/json',
    'text/plain',
  ]
  const validExtensions = ['.csv', '.xlsx', '.xls', '.json', '.txt']
  const fileName = file.name.toLowerCase()
  const isValidExtension = validExtensions.some((ext) => fileName.endsWith(ext))

  if (!isValidExtension) {
    ElMessage.error('仅支持 CSV、Excel、JSON、TXT 格式')
    return false
  }

  return true
}

// 上传成功
const handleUploadSuccess = (response: any, uploadFile: UploadFile) => {
  if (response.code === 200 || response.success) {
    uploadedFile.value = uploadFile.raw!
    extractedTexts.value = response.texts || []
    ElMessage.success(`成功提取 ${extractedTexts.value.length} 条文本`)
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 上传失败
const handleUploadError = (error: any) => {
  console.error('上传失败:', error)
  ElMessage.error('上传失败，请重试')
}

// 移除文件
const handleRemove = () => {
  uploadedFile.value = null
  extractedTexts.value = []
  result.value = null
}

// 批量分析
const handleBatchAnalyze = async () => {
  if (!extractedTexts.value.length) {
    ElMessage.warning('请先上传文件')
    return
  }

  try {
    isProcessing.value = true
    startTime.value = Date.now()
    result.value = null

    // 重置进度
    progress.value = {
      current: 0,
      total: extractedTexts.value.length,
      success: 0,
      failed: 0,
      elapsedTime: 0,
      percentage: 0,
    }

    // 模拟进度更新
    const progressTimer = setInterval(() => {
      progress.value.elapsedTime = Math.floor((Date.now() - startTime.value) / 1000)
    }, 1000)

    // 调用批量分析
    const response = await batchAnalyze({
      texts: extractedTexts.value,
      model_key: form.value.modelKey,
    })

    clearInterval(progressTimer)

    // 更新结果
    result.value = response
    progress.value = {
      current: response.total,
      total: response.total,
      success: response.success,
      failed: response.failed,
      elapsedTime: Math.floor((Date.now() - startTime.value) / 1000),
      percentage: 100,
    }

    ElMessage.success(`分析完成：成功 ${response.success} 条，失败 ${response.failed} 条`)
  } catch (error) {
    console.error('批量分析失败:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

// 取消分析
const handleCancel = () => {
  ElMessage.warning('分析已取消')
  isProcessing.value = false
}

// 重置
const handleReset = () => {
  fileList.value = []
  uploadedFile.value = null
  extractedTexts.value = []
  result.value = null
  progress.value = {
    current: 0,
    total: 0,
    success: 0,
    failed: 0,
    elapsedTime: 0,
    percentage: 0,
  }
}

// 导出 CSV
const handleExport = () => {
  if (!result.value) return

  const csvContent = convertToCSV(result.value.results)
  downloadCSV(csvContent, `file-analysis-result-${Date.now()}.csv`)
  ElMessage.success('导出成功')
}

// 转换为 CSV
const convertToCSV = (results: any[]) => {
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

  return '﻿' + csvContent // 添加 BOM 以支持中文
}

// 下载 CSV
const downloadCSV = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

// 获取标签类型
const getLabelType = (label: string) => {
  const typeMap: Record<string, string> = {
    positive: 'success',
    negative: 'danger',
    neutral: 'info',
  }
  return typeMap[label] || 'info'
}

// 获取标签文本
const getLabelText = (label: string) => {
  const textMap: Record<string, string> = {
    positive: '正面',
    negative: '负面',
    neutral: '中性',
  }
  return textMap[label] || label
}
</script>

<style scoped lang="scss">
.file-upload-view {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }

  .header-icon {
    font-size: 18px;
  }
}

.upload-card {
  margin-bottom: 20px;
}

.upload-limit {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.config-card {
  margin-bottom: 20px;
}

.preview-card {
  margin-bottom: 20px;
}

.text-preview {
  max-height: 300px;
  overflow-y: auto;

  .text-item {
    padding: 12px;
    border-bottom: 1px solid var(--el-border-color-light);

    &:last-child {
      border-bottom: none;
    }
  }

  .more-text {
    padding: 12px;
    text-align: center;
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }
}

.action-section {
  display: flex;
  gap: 12px;
  margin: 24px 0;
  justify-content: center;

  .predict-btn {
    min-width: 200px;
  }
}

.progress-card {
  margin: 24px 0;

  .progress-content {
    padding: 20px 0;

    .progress-stats {
      display: flex;
      gap: 40px;
      margin-top: 20px;

      .stat-item {
        display: flex;
        align-items: center;
        gap: 8px;

        .stat-label {
          color: var(--el-text-color-secondary);
        }

        .stat-value {
          font-weight: 600;
          font-size: 18px;

          &.success {
            color: var(--el-color-success);
          }

          &.danger {
            color: var(--el-color-danger);
          }
        }
      }
    }
  }
}

.result-card {
  margin-top: 24px;

  .result-summary {
    margin-bottom: 20px;
    padding: 20px;
    background: var(--el-bg-color-page);
    border-radius: 8px;

    .summary-item {
      text-align: center;

      .summary-label {
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }

      .summary-value {
        font-size: 28px;
        font-weight: 700;

        &.total {
          color: var(--el-color-primary);
        }

        &.success {
          color: var(--el-color-success);
        }

        &.danger {
          color: var(--el-color-danger);
        }

        &.info {
          color: var(--el-color-info);
        }
      }
    }
  }

  .table-tip {
    margin-top: 12px;
    text-align: center;
  }
}
</style>
