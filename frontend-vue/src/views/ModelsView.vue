<template>
  <div class="models-view">
    <div class="page-header">
      <h1>🤖 模型管理</h1>
      <p class="subtitle">管理和监控 NLP 模型</p>
    </div>

    <el-row :gutter="20" class="models-grid">
      <el-col
        v-for="model in models"
        :key="model.key"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
      >
        <el-card class="model-card" shadow="hover">
          <div class="model-header">
            <div class="model-icon" :class="model.status">
              <el-icon><Cpu /></el-icon>
            </div>
            <el-tag :type="model.status === 'active' ? 'success' : 'danger'" size="small">
              {{ model.status === 'active' ? '运行中' : '已停止' }}
            </el-tag>
          </div>

          <div class="model-info">
            <h3>{{ model.name }}</h3>
            <p class="model-key">{{ model.key }}</p>
            <p class="model-desc">{{ model.description }}</p>
          </div>

          <div class="model-stats">
            <div class="stat-item">
              <span class="stat-label">版本</span>
              <span class="stat-value">{{ model.version }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">调用次数</span>
              <span class="stat-value">{{ formatNumber(model.calls) }}</span>
            </div>
          </div>

          <div class="model-actions">
            <el-button
              v-if="model.status === 'active'"
              type="danger"
              size="small"
              plain
              @click="handleStop(model.key)"
            >
              停止
            </el-button>
            <el-button
              v-else
              type="primary"
              size="small"
              @click="handleStart(model.key)"
            >
              启动
            </el-button>
            <el-button size="small" @click="handleViewDetail(model)">
              详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="models.length === 0 && !loading" description="暂无模型" />

    <!-- 模型详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`模型详情 - ${selectedModel?.name}`"
      width="600px"
    >
      <div v-if="selectedModel" class="model-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="模型名称">
            {{ selectedModel.name }}
          </el-descriptions-item>
          <el-descriptions-item label="模型 Key">
            <code>{{ selectedModel.key }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedModel.status === 'active' ? 'success' : 'danger'">
              {{ selectedModel.status === 'active' ? '运行中' : '已停止' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ selectedModel.version }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedModel.description }}
          </el-descriptions-item>
          <el-descriptions-item label="调用次数">
            {{ formatNumber(selectedModel.calls) }}
          </el-descriptions-item>
          <el-descriptions-item label="平均耗时">
            {{ selectedModel.avgTime }}ms
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ selectedModel.createdAt }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ selectedModel.updatedAt }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button type="primary" @click="handleReload(selectedModel.key)">
            <el-icon><Refresh /></el-icon>
            重新加载
          </el-button>
          <el-button type="warning" @click="handleClearCache(selectedModel.key)">
            <el-icon><Delete /></el-icon>
            清空缓存
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Cpu, Refresh, Delete } from '@element-plus/icons-vue'
import type { ModelInfo } from '@/types/model'

// 模拟数据
const models = ref<ModelInfo[]>([
  {
    key: 'bert',
    name: 'BERT 情感分析',
    description: '基于 BERT 的中文情感分类模型，准确率高',
    version: '1.0.0',
    status: 'active',
    calls: 1234,
    avgTime: 245,
    createdAt: '2024-01-01 00:00:00',
    updatedAt: '2024-01-15 10:30:00',
  },
  {
    key: 'vader',
    name: 'VADER 情感分析',
    description: '基于词典的情感分析模型，速度快',
    version: '1.0.0',
    status: 'active',
    calls: 5678,
    avgTime: 12,
    createdAt: '2024-01-01 00:00:00',
    updatedAt: '2024-01-10 14:20:00',
  },
])

const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedModel = ref<ModelInfo | null>(null)

onMounted(() => {
  fetchModels()
})

async function fetchModels() {
  loading.value = true
  try {
    // TODO: 调用真实 API
    // const data = await getModelsApi()
    // models.value = data

    // 演示模式
    await new Promise(resolve => setTimeout(resolve, 500))
  } catch (error) {
    ElMessage.error('获取模型列表失败')
  } finally {
    loading.value = false
  }
}

async function handleStart(key: string) {
  try {
    // TODO: 调用真实 API
    // await startModelApi(key)

    const model = models.value.find(m => m.key === key)
    if (model) {
      model.status = 'active'
      ElMessage.success(`模型 ${model.name} 已启动`)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '启动失败')
  }
}

async function handleStop(key: string) {
  try {
    await ElMessageBox.confirm('确定要停止该模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用真实 API
    // await stopModelApi(key)

    const model = models.value.find(m => m.key === key)
    if (model) {
      model.status = 'stopped'
      ElMessage.success(`模型 ${model.name} 已停止`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('停止失败')
    }
  }
}

function handleViewDetail(model: ModelInfo) {
  selectedModel.value = model
  detailDialogVisible.value = true
}

async function handleReload(key: string) {
  try {
    await ElMessageBox.confirm('确定要重新加载该模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用真实 API
    // await reloadModelApi(key)

    ElMessage.success('模型重新加载成功')
    detailDialogVisible.value = false
    await fetchModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重新加载失败')
    }
  }
}

async function handleClearCache(key: string) {
  try {
    await ElMessageBox.confirm('确定要清空该模型的缓存吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用真实 API
    // await clearCacheApi(key)

    ElMessage.success('缓存已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空缓存失败')
    }
  }
}

function formatNumber(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}
</script>

<style scoped lang="scss">
.models-view {
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

  .models-grid {
    .model-card {
      margin-bottom: 20px;
      border-radius: 12px;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }

      .model-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        .model-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          transition: all 0.3s ease;

          &.active {
            background: linear-gradient(135deg, #7BA3C4 0%, #6B93B4 100%);
            color: white;
          }

          &.stopped {
            background: #F8F9FA;
            color: #8A98A8;
          }
        }
      }

      .model-info {
        margin-bottom: 16px;

        h3 {
          font-size: 18px;
          font-weight: 600;
          margin: 0 0 4px 0;
          color: #2C3E50;
        }

        .model-key {
          font-size: 12px;
          color: #8A98A8;
          font-family: 'Courier New', monospace;
          margin: 0 0 8px 0;
        }

        .model-desc {
          font-size: 13px;
          color: #5A6878;
          line-height: 1.6;
          margin: 0;
        }
      }

      .model-stats {
        display: flex;
        gap: 16px;
        padding: 12px;
        background: #F8F9FA;
        border-radius: 8px;
        margin-bottom: 16px;

        .stat-item {
          flex: 1;
          text-align: center;

          .stat-label {
            font-size: 12px;
            color: #8A98A8;
            margin-bottom: 4px;
          }

          .stat-value {
            font-size: 16px;
            font-weight: 600;
            color: #5B9A8B;
          }
        }
      }

      .model-actions {
        display: flex;
        gap: 8px;

        .el-button {
          flex: 1;
        }
      }
    }
  }

  .model-detail {
    .detail-actions {
      margin-top: 24px;
      display: flex;
      gap: 12px;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .models-view {
    .page-header {
      h1 {
        font-size: 24px;
      }
    }

    .models-grid {
      .model-card {
        .model-actions {
          flex-direction: column;
        }
      }
    }
  }
}
</style>
