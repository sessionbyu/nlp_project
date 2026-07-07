<template>
  <div class="history-view">
    <div class="page-header">
      <h1>📊 历史记录查询</h1>
      <p class="subtitle">查看所有预测历史，支持多种筛选方式</p>
    </div>

    <el-card class="filter-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Filter /></el-icon>
            查询条件
          </span>
          <el-button type="danger" plain size="small" @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </template>

      <el-form :model="historyStore.filters" label-position="top">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="标签过滤">
              <el-select
                v-model="historyStore.filters.label"
                placeholder="选择标签"
                clearable
                class="custom-select"
              >
                <el-option label="全部" value="全部" />
                <el-option label="正面" value="正面" />
                <el-option label="负面" value="负面" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="关键词搜索">
              <el-input
                v-model="historyStore.filters.keyword"
                placeholder="输入关键词..."
                clearable
                class="custom-input"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="最低置信度">
              <div class="slider-wrapper">
                <el-slider
                  v-model="historyStore.filters.min_score"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :show-tooltip="true"
                  class="custom-slider"
                />
                <span class="slider-value">{{ historyStore.filters.min_score.toFixed(2) }}</span>
              </div>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="最高置信度">
              <div class="slider-wrapper">
                <el-slider
                  v-model="historyStore.filters.max_score"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :show-tooltip="true"
                  class="custom-slider"
                />
                <span class="slider-value">{{ historyStore.filters.max_score.toFixed(2) }}</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item>
              <el-checkbox v-model="historyStore.filters.useDateFilter" class="date-checkbox">
                启用时间范围过滤
              </el-checkbox>
            </el-form-item>
          </el-col>

          <el-col v-if="historyStore.filters.useDateFilter" :span="12">
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                class="custom-date-picker"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            :loading="historyStore.loading"
            @click="handleQuery"
            size="large"
            class="query-btn"
          >
            <el-icon><Search /></el-icon>
            查询历史
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card fade-in" v-loading="historyStore.loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><List /></el-icon>
            <span>查询结果</span>
            <el-badge :value="historyStore.total" type="primary" class="result-badge" />
          </div>
          <div v-if="historyStore.hasRecords" class="export-actions">
            <el-button type="success" @click="handleExport('csv')">
              <el-icon><Download /></el-icon>
              导出 CSV
            </el-button>
            <el-dropdown @command="(cmd) => handleExport(cmd as 'csv' | 'json' | 'excel')">
              <el-button type="primary" plain>
                更多格式
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="csv">
                    <el-icon><Document /></el-icon>
                    CSV 格式
                  </el-dropdown-item>
                  <el-dropdown-item command="json">
                    <el-icon><Document /></el-icon>
                    JSON 格式
                  </el-dropdown-item>
                  <el-dropdown-item command="excel">
                    <el-icon><Grid /></el-icon>
                    Excel 格式
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <el-table
        :data="historyStore.records"
        stripe
        :row-style="{ height: '56px' }"
        :header-cell-style="{ background: '#F8F9FA', fontWeight: 600 }"
      >
        <el-table-column prop="id" label="编号" width="80" align="center" />

        <el-table-column prop="input_text" label="输入文本" min-width="250">
          <template #default="{ row }">
            <div class="text-cell">
              {{ truncateText(row.input_text, 80) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="label" label="预测标签" width="140" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getLabelType(row.label)"
              size="large"
              effect="light"
              round
            >
              {{ formatLabel(row.label).text }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="score" label="置信度" width="140" align="center">
          <template #default="{ row }">
            <div class="score-cell">
              <span class="score-value">{{ formatScore(row.score) }}</span>
              <el-progress
                :percentage="Math.round(row.score * 100)"
                :color="getScoreColor(row.score)"
                :stroke-width="6"
                :show-text="false"
                class="score-progress"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="model_key" label="模型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.model_key === 'bert' ? 'primary' : 'info'" size="small">
              {{ row.model_key?.toUpperCase() || '-' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <div class="datetime-cell">
              <el-icon class="time-icon"><Clock /></el-icon>
              <span>{{ formatDateTime(row.created_at) }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="historyStore.currentPage"
          :page-size="historyStore.filters.page_size"
          :total="historyStore.total"
          layout="total, prev, pager, next, sizes"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
          background
        />
      </div>
    </el-card>

    <el-card v-if="historyStore.hasRecentRecords" class="recent-card fade-in">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Clock /></el-icon>
          <span>⚡ 最近 10 条记录</span>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="record in historyStore.recentRecords.slice(0, 10)"
          :key="record.id"
          :type="getLabelType(record.label)"
          placement="top"
        >
          <el-card class="recent-item" shadow="hover">
            <div class="recent-header">
              <el-tag :type="getLabelType(record.label)" size="small">
                {{ formatLabel(record.label).text }}
              </el-tag>
              <span class="recent-score">
                <el-icon><TrendCharts /></el-icon>
                {{ formatScore(record.score) }}
              </span>
            </div>
            <div class="recent-text">
              {{ truncateText(record.input_text, 80) }}
            </div>
            <div class="recent-time">
              <el-icon><Clock /></el-icon>
              {{ formatDateTime(record.created_at) }}
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useHistoryStore } from '@/stores/history'
import {
  Filter,
  RefreshLeft,
  Search,
  List,
  Download,
  ArrowDown,
  Clock,
  TrendCharts,
  Document,
  Grid,
} from '@element-plus/icons-vue'
import { formatScore, formatDateTime, formatLabel, truncateText } from '@/utils/format'
import { exportToCSV, exportToJSON, exportToExcel, formatFilename } from '@/utils/export'

const historyStore = useHistoryStore()

const dateRange = ref<[string, string]>()

onMounted(() => {
  historyStore.fetchRecentHistory(10)
})

watch(
  () => historyStore.filters.useDateFilter,
  (enabled) => {
    if (!enabled) {
      dateRange.value = undefined
      historyStore.filters.startDate = ''
      historyStore.filters.endDate = ''
    }
  }
)

watch(dateRange, (range) => {
  if (range && range.length === 2) {
    historyStore.filters.startDate = range[0]
    historyStore.filters.endDate = range[1]
  }
})

function handleQuery() {
  historyStore.fetchHistory()
}

function handleReset() {
  historyStore.resetFilters()
  dateRange.value = undefined
  ElMessage.success('已重置筛选条件')
}

function handleExportClick() {
  // 显示格式选择提示
  ElMessage.info('请选择导出格式：点击导出按钮选择 CSV/JSON/Excel')
}

function handleExport(format: 'csv' | 'json' | 'excel') {
  const data = historyStore.records.map((record) => ({
    ID: record.id,
    文本: record.input_text,
    标签: record.label,
    置信度: record.score,
    模型: record.model_key || '',
    IP: record.source_ip || '',
    时间: record.created_at,
  }))

  const filename = formatFilename('history', format)

  try {
    switch (format) {
      case 'csv':
        exportToCSV(data, historyStore.records.map((record) => ({
          ID: record.id,
          文本: record.input_text,
          标签: record.label,
          置信度: record.score,
          模型: record.model_key || '',
          IP: record.source_ip || '',
          时间: record.created_at,
        })), filename)
        break
      case 'json':
        exportToJSON(data, filename)
        break
      case 'excel':
        exportToExcel(data, historyStore.records.map((record) => ({
          ID: record.id,
          文本: record.input_text,
          标签: record.label,
          置信度: record.score,
          模型: record.model_key || '',
          IP: record.source_ip || '',
          时间: record.created_at,
        })), filename)
        break
    }
    ElMessage.success(`${format.toUpperCase()} 导出成功`)
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

function handlePageChange(page: number) {
  historyStore.setPage(page)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function handleSizeChange(size: number) {
  historyStore.updateFilters({ page_size: size, page: 1 })
  historyStore.fetchHistory()
}

function getLabelType(label: string): 'success' | 'danger' | 'info' {
  return formatLabel(label).type
}

function getScoreColor(score: number): string {
  if (score >= 0.7) return '#68C3A0'
  if (score >= 0.5) return '#E8B87C'
  return '#E87C7C'
}
</script>

<style scoped lang="scss">
.history-view {
  .page-header {
    margin-bottom: 24px;

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

  .filter-card,
  .table-card,
  .recent-card {
    margin-bottom: 24px;
    border-radius: 16px;
    transition: all 0.3s ease;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;

      .header-icon {
        color: #5B9A8B;
      }

      .result-badge {
        margin-left: 8px;
      }
    }

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }
  }

  .filter-card {
    :deep(.el-form-item__label) {
      font-weight: 500;
      color: #5A6878;
    }

    .slider-wrapper {
      display: flex;
      align-items: center;
      gap: 12px;

      .custom-slider {
        flex: 1;
      }

      .slider-value {
        min-width: 50px;
        text-align: right;
        font-weight: 600;
        color: #5B9A8B;
      }
    }

    .query-btn {
      min-width: 160px;
      height: 44px;
      border-radius: 22px;
      background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
      border: none;
      font-weight: 600;
    }
  }

  .table-card {
    .text-cell {
      max-width: 400px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .score-cell {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: center;

      .score-value {
        font-weight: 600;
        color: #5B9A8B;
        font-size: 16px;
      }

      .score-progress {
        width: 100%;
        max-width: 120px;
      }
    }

    .datetime-cell {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: #8A98A8;

      .time-icon {
        font-size: 14px;
      }
    }

    .pagination-wrapper {
      margin-top: 24px;
      display: flex;
      justify-content: center;
    }
  }

  .recent-card {
    .recent-item {
      transition: all 0.3s ease;

      &:hover {
        transform: translateX(4px);
      }

      .recent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .recent-score {
          display: flex;
          align-items: center;
          gap: 4px;
          font-weight: 600;
          color: #5B9A8B;
        }
      }

      .recent-text {
        font-size: 14px;
        color: #5A6878;
        margin-bottom: 8px;
        line-height: 1.6;
      }

      .recent-time {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #8A98A8;
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .history-view {
    .page-header {
      h1 {
        font-size: 24px;
      }

      .subtitle {
        font-size: 14px;
      }
    }

    .filter-card {
      :deep(.el-form-item__label) {
        font-size: 12px;
      }
    }

    .table-card {
      .text-cell {
        max-width: 200px;
        font-size: 12px;
      }
    }
  }
}
</style>
