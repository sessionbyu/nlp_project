<template>
  <div class="monitoring-view">
    <div class="page-header">
      <h1>📊 系统监控</h1>
      <p class="subtitle">实时监控系统健康状态和资源使用情况</p>
    </div>

    <!-- 健康状态卡片 -->
    <el-row :gutter="20" class="health-cards">
      <el-col :xs="24" :sm="8">
        <el-card class="health-card" :class="{ healthy: healthStatus.status === 'healthy' }">
          <div class="health-content">
            <div class="health-icon">
              <el-icon :size="40" :color="healthIconColor">
                <component :is="healthIcon" />
              </el-icon>
            </div>
            <div class="health-info">
              <div class="health-label">健康检查</div>
              <el-tag
                :type="getHealthType(healthStatus.status)"
                effect="dark"
                size="large"
              >
                {{ healthStatus.status || '检查中...' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card class="health-card" :class="{ ready: readinessStatus.status === 'ready' }">
          <div class="health-content">
            <div class="health-icon">
              <el-icon :size="40" :color="readinessIconColor">
                <component :is="readinessIcon" />
              </el-icon>
            </div>
            <div class="health-info">
              <div class="health-label">就绪检查</div>
              <el-tag
                :type="getHealthType(readinessStatus.status)"
                effect="dark"
                size="large"
              >
                {{ readinessStatus.status || '检查中...' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card class="health-card" :class="{ alive: livenessStatus.status === 'alive' }">
          <div class="health-content">
            <div class="health-icon">
              <el-icon :size="40" :color="livenessIconColor">
                <component :is="livenessIcon" />
              </el-icon>
            </div>
            <div class="health-info">
              <div class="health-label">存活检查</div>
              <el-tag
                :type="getHealthType(livenessStatus.status)"
                effect="dark"
                size="large"
              >
                {{ livenessStatus.status || '检查中...' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态 -->
    <el-card v-if="systemStatus" class="system-status-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Cpu /></el-icon>
            系统状态
          </span>
          <el-button
            type="primary"
            plain
            @click="refreshStatus"
            :loading="refreshing"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-row :gutter="30">
        <!-- CPU 使用率 -->
        <el-col :xs="24" :sm="12" :md="8">
          <div class="metric-card">
            <div class="metric-header">
              <el-icon><Cpu /></el-icon>
              <span>CPU 使用率</span>
            </div>
            <div class="metric-value" :class="getCpuClass(systemStatus.system.cpu_percent)">
              {{ formatPercent(systemStatus.system.cpu_percent) }}
            </div>
            <el-progress
              :percentage="systemStatus.system.cpu_percent"
              :color="getCpuColor(systemStatus.system.cpu_percent)"
              :stroke-width="12"
              :show-text="false"
            />
          </div>
        </el-col>

        <!-- 内存使用 -->
        <el-col :xs="24" :sm="12" :md="8">
          <div class="metric-card">
            <div class="metric-header">
              <el-icon><Memo /></el-icon>
              <span>内存使用</span>
            </div>
            <div class="metric-value">
              {{ formatBytes((systemStatus.system.memory.total - systemStatus.system.memory.available) || 0) }} / {{ formatBytes(systemStatus.system.memory.total) }}
            </div>
            <div class="metric-sub">
              {{ formatPercent(systemStatus.system.memory.percent) }}
            </div>
            <el-progress
              :percentage="systemStatus.system.memory.percent"
              :color="getMemoryColor(systemStatus.system.memory.percent)"
              :stroke-width="12"
              :show-text="false"
            />
          </div>
        </el-col>

        <!-- 磁盘使用 -->
        <el-col v-if="systemStatus.system.disk" :xs="24" :sm="12" :md="8">
          <div class="metric-card">
            <div class="metric-header">
              <el-icon><Files /></el-icon>
              <span>磁盘使用</span>
            </div>
            <div class="metric-value">
              {{ formatBytes(systemStatus.system.disk.free) }} / {{ formatBytes(systemStatus.system.disk.total) }}
            </div>
            <div class="metric-sub">
              {{ formatPercent(systemStatus.system.disk.percent) }}
            </div>
            <el-progress
              :percentage="systemStatus.system.disk.percent"
              :color="getDiskColor(systemStatus.system.disk.percent)"
              :stroke-width="12"
              :show-text="false"
            />
          </div>
        </el-col>
      </el-row>

      <!-- 数据库状态 -->
      <el-divider />
      <div class="db-status">
        <div class="status-item">
          <span class="status-label">数据库状态:</span>
          <el-tag
            :type="systemStatus.database.status === 'connected' ? 'success' : 'danger'"
            effect="dark"
          >
            {{ systemStatus.database.status === 'connected' ? '已连接' : '未连接' }}
          </el-tag>
        </div>
        <div v-if="systemStatus.database.prediction_count !== undefined" class="status-item">
          <span class="status-label">预测记录数:</span>
          <el-text strong>{{ systemStatus.database.prediction_count }}</el-text>
        </div>
        <div v-if="systemStatus.database.error" class="status-item">
          <span class="status-label">错误信息:</span>
          <el-text type="danger">{{ systemStatus.database.error }}</el-text>
        </div>
      </div>

      <!-- 配置信息 -->
      <el-divider />
      <div class="config-info">
        <h4>系统配置</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="默认模型">
            {{ systemStatus.config.default_model }}
          </el-descriptions-item>
          <el-descriptions-item label="Redis 主机">
            {{ systemStatus.config.redis_host || '未配置' }}
          </el-descriptions-item>
          <el-descriptions-item label="限流">
            <el-tag :type="systemStatus.config.rate_limit_enabled ? 'success' : 'info'" size="small">
              {{ systemStatus.config.rate_limit_enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(systemStatus.timestamp) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- Prometheus 指标 -->
    <el-card class="metrics-card fade-in" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><TrendCharts /></el-icon>
            Prometheus 指标
          </span>
          <div class="header-actions">
            <el-button
              type="primary"
              plain
              @click="fetchMetrics"
              :loading="loadingMetrics"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button
              v-if="metrics"
              type="success"
              plain
              @click="downloadMetrics"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loadingMetrics" class="metrics-loading">
        <Loading :visible="true" text="加载指标..." />
      </div>

      <div v-else-if="metrics" class="metrics-content">
        <el-input
          v-model="metricsFilter"
          placeholder="过滤指标..."
          clearable
          style="margin-bottom: 16px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-scrollbar height="600px">
          <pre class="metrics-text">{{ filteredMetrics }}</pre>
        </el-scrollbar>
      </div>

      <div v-else class="metrics-empty">
        <el-empty description="暂无指标数据">
          <el-button type="primary" @click="fetchMetrics">加载指标</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  User,
  CircleCheck,
  Cpu,
  Refresh,
  Search,
  Download,
  Memo,
  Files,
  TrendCharts,
  CircleCheckFilled,
  CircleCloseFilled,
  QuestionFilled,
} from '@element-plus/icons-vue'
import { healthCheck, getSystemStatus, getMetrics, formatBytes, formatPercent, getStatusType } from '@/api/monitoring'
import StatCard from '@/components/common/StatCard.vue'
import Loading from '@/components/common/Loading.vue'

// 健康状态
const healthStatus = ref({ status: '' })
const readinessStatus = ref({ status: '' })
const livenessStatus = ref({ status: '' })

// 系统状态
const systemStatus = ref<any>(null)
const refreshing = ref(false)

// 指标
const metrics = ref<string>('')
const loadingMetrics = ref(false)
const metricsFilter = ref('')

// 定时器
let statusTimer: NodeJS.Timeout | null = null
let healthTimer: NodeJS.Timeout | null = null

// 计算属性
const healthIconColor = computed(() => {
  if (healthStatus.value.status === 'healthy') return 'var(--el-color-success)'
  if (healthStatus.value.status === 'unhealthy') return 'var(--el-color-danger)'
  return 'var(--el-color-warning)'
})

const healthIcon = computed(() => {
  if (healthStatus.value.status === 'healthy') return CircleCheckFilled
  if (healthStatus.value.status === 'unhealthy') return CircleCloseFilled
  return QuestionFilled
})

const readinessIconColor = computed(() => {
  if (readinessStatus.value.status === 'ready') return 'var(--el-color-success)'
  if (readinessStatus.value.status === 'not ready') return 'var(--el-color-danger)'
  return 'var(--el-color-warning)'
})

const readinessIcon = computed(() => {
  if (readinessStatus.value.status === 'ready') return CircleCheckFilled
  if (readinessStatus.value.status === 'not ready') return CircleCloseFilled
  return QuestionFilled
})

const livenessIconColor = computed(() => {
  if (livenessStatus.value.status === 'alive') return 'var(--el-color-success)'
  return 'var(--el-color-warning)'
})

const livenessIcon = computed(() => {
  if (livenessStatus.value.status === 'alive') return CircleCheckFilled
  return QuestionFilled
})

const filteredMetrics = computed(() => {
  if (!metricsFilter.value || !metrics.value) return metrics.value
  const lines = metrics.value.split('\n')
  return lines
    .filter((line) => line.toLowerCase().includes(metricsFilter.value.toLowerCase()))
    .join('\n')
})

// 获取健康状态
const fetchHealth = async () => {
  try {
    const [health, readiness, liveness] = await Promise.all([
      healthCheck(),
      healthCheck(),
      healthCheck(),
    ])
    healthStatus.value = health
    readinessStatus.value = readiness
    livenessStatus.value = liveness
  } catch (error) {
    console.error('健康检查失败:', error)
  }
}

// 获取系统状态
const refreshStatus = async () => {
  try {
    refreshing.value = true
    const data = await getSystemStatus()
    systemStatus.value = data
  } catch (error) {
    ElMessage.error('获取系统状态失败')
  } finally {
    refreshing.value = false
  }
}

// 获取指标
const fetchMetrics = async () => {
  try {
    loadingMetrics.value = true
    const data = await getMetrics()
    metrics.value = data
  } catch (error) {
    ElMessage.error('获取指标失败')
  } finally {
    loadingMetrics.value = false
  }
}

// 下载指标
const downloadMetrics = () => {
  if (!metrics.value) return

  const blob = new Blob([metrics.value], { type: 'text/plain' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `metrics-${new Date().toISOString().split('T')[0]}.txt`
  link.click()
  URL.revokeObjectURL(link.href)

  ElMessage.success('下载成功')
}

// 获取健康类型
const getHealthType = (status: string) => {
  if (status === 'healthy' || status === 'ready' || status === 'alive') return 'success'
  if (status === 'unhealthy' || status === 'not ready') return 'danger'
  return 'warning'
}

// 获取CPU颜色
const getCpuColor = (percent: number) => {
  if (percent >= 90) return 'var(--el-color-danger)'
  if (percent >= 70) return 'var(--el-color-warning)'
  return 'var(--el-color-success)'
}

// 获取CPU类
const getCpuClass = (percent: number) => {
  if (percent >= 90) return 'danger'
  if (percent >= 70) return 'warning'
  return 'success'
}

// 获取内存颜色
const getMemoryColor = (percent: number) => {
  if (percent >= 90) return 'var(--el-color-danger)'
  if (percent >= 70) return 'var(--el-color-warning)'
  return 'var(--el-color-success)'
}

// 获取磁盘颜色
const getDiskColor = (percent: number) => {
  if (percent >= 90) return 'var(--el-color-danger)'
  if (percent >= 70) return 'var(--el-color-warning)'
  return 'var(--el-color-success)'
}

// 格式化日期时间
const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 启动定时刷新
const startAutoRefresh = () => {
  // 每10秒刷新健康状态
  healthTimer = setInterval(fetchHealth, 10000)
  // 每30秒刷新系统状态
  statusTimer = setInterval(refreshStatus, 30000)
}

// 停止定时刷新
const stopAutoRefresh = () => {
  if (healthTimer) {
    clearInterval(healthTimer)
    healthTimer = null
  }
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
}

// 生命周期
onMounted(async () => {
  await Promise.all([fetchHealth(), refreshStatus(), fetchMetrics()])
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped lang="scss">
.monitoring-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.health-cards {
  margin-bottom: 20px;

  .health-card {
    transition: all 0.3s;

    &.healthy,
    &.ready,
    &.alive {
      border-color: var(--el-color-success);
    }

    .health-content {
      display: flex;
      align-items: center;
      gap: 20px;
      padding: 10px;

      .health-icon {
        flex-shrink: 0;
      }

      .health-info {
        flex: 1;

        .health-label {
          font-size: 14px;
          color: var(--el-text-color-secondary);
          margin-bottom: 8px;
        }
      }
    }
  }
}

.system-status-card,
.metrics-card {
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

    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.system-status-card {
  .metric-card {
    text-align: center;
    padding: 20px;
    background: var(--el-bg-color-page);
    border-radius: 8px;

    .metric-header {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 16px;
      color: var(--el-text-color-secondary);
    }

    .metric-value {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 8px;

      &.danger {
        color: var(--el-color-danger);
      }

      &.warning {
        color: var(--el-color-warning);
      }

      &.success {
        color: var(--el-color-success);
      }
    }

    .metric-sub {
      font-size: 14px;
      color: var(--el-text-color-secondary);
      margin-bottom: 12px;
    }
  }

  .db-status {
    display: flex;
    gap: 40px;
    flex-wrap: wrap;

    .status-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .status-label {
        color: var(--el-text-color-secondary);
      }
    }
  }

  .config-info {
    h4 {
      margin-bottom: 16px;
    }
  }
}

.metrics-loading,
.metrics-empty {
  padding: 60px 0;
}

.metrics-content {
  .metrics-text {
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0;
    padding: 16px;
    background: var(--el-bg-color-page);
    border-radius: 4px;
  }
}
</style>
