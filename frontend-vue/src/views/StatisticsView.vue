<template>
  <div class="statistics-view">
    <el-card class="stats-header">
      <template #header>
        <div class="card-header">
          <h2>📈 统计概览</h2>
          <div class="actions">
            <el-button
              type="primary"
              :loading="statsStore.loading"
              @click="handleRefresh"
            >
              🔄 刷新数据
            </el-button>
            <el-checkbox v-model="autoRefresh">自动刷新 (60s)</el-checkbox>
          </div>
        </div>
      </template>
    </el-card>

    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">总预测次数</div>
              <div class="stat-value">{{ formatNumber(statsStore.totalPredictions) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon score">
              <el-icon :size="30"><DataAnalysis /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">平均置信度</div>
              <div class="stat-value">{{ formatScore(statsStore.averageScore) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon positive">
              <el-icon :size="30"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">正面 / 负面</div>
              <div class="stat-value">
                {{ statsStore.positiveCount }} / {{ statsStore.negativeCount }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon ratio">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">正面比例</div>
              <div class="stat-value">{{ statsStore.positiveRatio.toFixed(1) }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <h3>标签分布 - 柱状图</h3>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>
            <h3>标签分布 - 饼图</h3>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="info-card">
      <template #header>
        <h3>📝 数据说明</h3>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="总预测次数">
          {{ formatNumber(statsStore.totalPredictions) }}
        </el-descriptions-item>
        <el-descriptions-item label="平均置信度">
          {{ formatScore(statsStore.averageScore) }}
        </el-descriptions-item>
        <el-descriptions-item label="正面评价">
          <el-tag type="success">{{ statsStore.positiveCount }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="负面评价">
          <el-tag type="danger">{{ statsStore.negativeCount }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="正面比例">
          {{ statsStore.positiveRatio.toFixed(1) }}%
        </el-descriptions-item>
        <el-descriptions-item label="负面比例">
          {{ (100 - statsStore.positiveRatio).toFixed(1) }}%
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Document,
  DataAnalysis,
  CircleCheck,
  TrendCharts,
} from '@element-plus/icons-vue'
import { useStatsStore } from '@/stores/stats'
import { formatScore, formatNumber } from '@/utils/format'

const statsStore = useStatsStore()
const autoRefresh = ref(false)
const barChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let barChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let refreshTimer: number | null = null

onMounted(() => {
  statsStore.fetchStats()

  nextTick(() => {
    initCharts()
  })
})

watch(
  () => statsStore.stats,
  () => {
    nextTick(() => {
      updateCharts()
    })
  }
)

watch(autoRefresh, (enabled) => {
  if (enabled) {
    refreshTimer = window.setInterval(() => {
      statsStore.fetchStats()
    }, 60000)
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (barChart) {
    barChart.dispose()
  }
  if (pieChart) {
    pieChart.dispose()
  }
})

function handleRefresh() {
  statsStore.fetchStats()
}

function initCharts() {
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }

  updateCharts()
}

function updateCharts() {
  const distribution = statsStore.labelDistribution
  const labels = Object.keys(distribution)
  const values = Object.values(distribution)

  // 柱状图配置
  const barOption: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: labels,
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: values,
        type: 'bar',
        itemStyle: {
          color: (params: { dataIndex: number }) => {
            const label = labels[params.dataIndex]
            if (label.includes('正面') || label.includes('positive')) {
              return '#68C3A0'
            }
            if (label.includes('负面') || label.includes('negative')) {
              return '#E87C7C'
            }
            return '#7BA3C4'
          },
        },
        label: {
          show: true,
          position: 'top',
        },
      },
    ],
  }

  // 饼图配置
  const pieOption: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'horizontal',
      bottom: '0%',
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)',
        },
        data: labels.map((label, index) => ({
          name: label,
          value: values[index],
          itemStyle: {
            color:
              label.includes('正面') || label.includes('positive')
                ? '#68C3A0'
                : label.includes('负面') || label.includes('negative')
                  ? '#E87C7C'
                  : '#7BA3C4',
          },
        })),
      },
    ],
  }

  if (barChart) {
    barChart.setOption(barOption, true)
  }

  if (pieChart) {
    pieChart.setOption(pieOption, true)
  }
}
</script>

<style scoped lang="scss">
.statistics-view {
  .stats-header {
    margin-bottom: 24px;
    border-radius: 16px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }

      .actions {
        display: flex;
        align-items: center;
        gap: 12px;

        .el-button {
          border-radius: 20px;
          font-weight: 600;
        }
      }
    }
  }

  .stats-cards {
    margin-bottom: 24px;

    .stat-card {
      margin-bottom: 24px;
      border-radius: 16px;
      overflow: hidden;
      transition: all 0.3s ease;
      background: linear-gradient(135deg, #F8F9FA 0%, #ffffff 100%);

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 24px;

        .stat-icon {
          width: 72px;
          height: 72px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;

          &.total {
            background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
            color: white;
            box-shadow: 0 8px 16px rgba(91, 154, 139, 0.3);
          }

          &.score {
            background: linear-gradient(135deg, #E8A87C 0%, #D4906A 100%);
            color: white;
            box-shadow: 0 8px 16px rgba(240, 147, 251, 0.3);
          }

          &.positive {
            background: linear-gradient(135deg, #7BA3C4 0%, #6B93B4 100%);
            color: white;
            box-shadow: 0 8px 16px rgba(79, 172, 254, 0.3);
          }

          &.ratio {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
            box-shadow: 0 8px 16px rgba(67, 233, 123, 0.3);
          }

          .el-icon {
            font-size: 32px;
          }
        }

        .stat-info {
          flex: 1;

          .stat-label {
            font-size: 14px;
            color: #8A98A8;
            margin-bottom: 8px;
          }

          .stat-value {
            font-size: 32px;
            font-weight: 700;
            color: #2C3E50;
            line-height: 1;
          }
        }
      }
    }
  }

  .charts-row {
    margin-bottom: 24px;

    .chart-container {
      height: 400px;
    }

    .el-card {
      border-radius: 16px;

      .el-card__header {
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }
    }
  }

  .info-card {
    border-radius: 16px;

    .el-card__header {
      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    :deep(.el-descriptions) {
      .el-descriptions-item__label {
        font-weight: 500;
        background: #F8F9FA;
        border-radius: 8px 0 0 8px;
      }

      .el-descriptions-item__content {
        border-radius: 0 8px 8px 0;
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .statistics-view {
    .stats-header {
      .card-header {
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;

        h2 {
          font-size: 20px;
        }

        .actions {
          width: 100%;
          flex-direction: column;

          .el-button {
            width: 100%;
          }
        }
      }
    }

    .stats-cards {
      .stat-card {
        .stat-content {
          padding: 16px;
          gap: 16px;

          .stat-icon {
            width: 56px;
            height: 56px;
            border-radius: 12px;
          }

          .stat-info {
            .stat-value {
              font-size: 24px;
            }
          }
        }
      }
    }
  }
}
</style>
