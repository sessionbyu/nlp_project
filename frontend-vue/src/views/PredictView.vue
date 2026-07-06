<template>
  <div class="predict-view">
    <div class="page-header">
      <h1>📝 文本情感预测</h1>
      <p class="subtitle">输入文本，AI 自动分析情感倾向</p>
    </div>

    <el-row :gutter="24" class="main-content">
      <el-col :xs="24" :lg="18">
        <el-card class="input-card fade-in">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Edit /></el-icon>
                文本输入
              </span>
              <el-tag type="info" effect="plain">
                {{ inputText.length }} 字符
              </el-tag>
            </div>
          </template>

          <div class="input-wrapper">
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="6"
              placeholder="请输入要分析的文本...&#10;&#10;支持中文、英文等多种语言&#10;建议输入 10-500 字符以获得最佳效果"
              :disabled="predictionStore.loading"
              class="text-input"
            />
          </div>

          <div class="action-row">
            <el-select
              v-model="predictionStore.selectedModel"
              placeholder="选择模型"
              style="width: 220px"
              :disabled="predictionStore.loading"
              class="model-select"
            >
              <el-option label="🤖 BERT（准确度高）" value="bert" />
              <el-option label="⚡ VADER（速度快）" value="vader" />
            </el-select>

            <el-button
              type="primary"
              :loading="predictionStore.loading"
              @click="handlePredict"
              size="large"
              class="predict-btn"
            >
              <el-icon v-if="!predictionStore.loading"><MagicStick /></el-icon>
              {{ predictionStore.loading ? '预测中...' : '🚀 开始预测' }}
            </el-button>
          </div>
        </el-card>

        <transition name="slide-up">
          <el-card v-if="predictionStore.hasResult" class="result-card">
            <template #header>
              <div class="card-header">
                <span class="header-title">
                  <el-icon class="header-icon"><Trophy /></el-icon>
                  预测结果
                </span>
                <el-tag :type="resultIconType" effect="dark" size="large">
                  {{ predictionStore.label }}
                </el-tag>
              </div>
            </template>

            <div class="result-content">
              <el-row :gutter="24">
                <el-col :span="14">
                  <div class="result-main">
                    <div class="result-label">情感标签</div>
                    <div class="result-value">
                      <el-result
                        :icon="resultIcon"
                        :title="predictionStore.label"
                        :sub-title="`使用模型: ${predictionStore.result?.model_key?.toUpperCase()}`"
                      />
                    </div>
                  </div>
                </el-col>

                <el-col :span="10">
                  <div class="confidence-section">
                    <div class="confidence-header">
                      <span class="confidence-label">置信度</span>
                      <span class="confidence-value">{{ formatScore(predictionStore.confidence) }}</span>
                    </div>
                    <el-progress
                      :percentage="Math.round(predictionStore.confidence * 100)"
                      :color="confidenceColor"
                      :stroke-width="24"
                      :show-text="false"
                      class="confidence-bar"
                    />
                    <div class="confidence-badge" :style="{ background: confidenceColor }">
                      {{ (predictionStore.confidence * 100).toFixed(1) }}%
                    </div>
                  </div>

                  <div class="quality-indicator">
                    <div class="quality-label">质量评级</div>
                    <div class="quality-stars">
                      <el-rate
                        :model-value="Math.round(predictionStore.confidence * 5)"
                        disabled
                        show-score
                        text-color="#ff9900"
                      />
                    </div>
                  </div>
                </el-col>
              </el-row>

              <div class="result-actions" v-if="predictionStore.hasResult">
                <el-button type="success" plain round @click="handleCopyResult">
                  <el-icon><DocumentCopy /></el-icon>
                  复制结果
                </el-button>
                <el-button type="primary" plain round @click="handlePredictAnother">
                  <el-icon><Refresh /></el-icon>
                  再次预测
                </el-button>
              </div>
            </div>
          </el-card>
        </transition>
      </el-col>

      <el-col :xs="24" :lg="6">
        <el-card class="guide-card slide-in">
          <template #header>
            <span class="card-header">
              <el-icon class="header-icon"><InfoFilled /></el-icon>
              使用说明
            </span>
          </template>

          <div class="guide-list">
            <div v-for="(item, index) in guideItems" :key="index" class="guide-item">
              <div class="guide-number">{{ index + 1 }}</div>
              <div class="guide-text">{{ item }}</div>
            </div>
          </div>

          <el-divider />

          <div class="model-info">
            <h4>模型对比</h4>
            <div class="model-comparison">
              <div class="model-item">
                <div class="model-name">BERT</div>
                <div class="model-desc">准确率高，适合复杂文本</div>
                <el-tag type="success" size="small">推荐</el-tag>
              </div>
              <div class="model-item">
                <div class="model-name">VADER</div>
                <div class="model-desc">速度快，适合实时预测</div>
                <el-tag type="info" size="small">快速</el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 文本增强分析 -->
        <el-card class="analysis-card fade-in" v-if="predictionStore.hasResult">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Cpu /></el-icon>
                文本增强分析
              </span>
              <el-button
                type="primary"
                size="small"
                @click="handleDeepAnalysis"
                :loading="analyzing"
              >
                <el-icon><MagicStick /></el-icon>
                {{ analyzing ? '分析中...' : '深度分析' }}
              </el-button>
            </div>
          </template>

          <div v-if="!analysisResult && !analyzing" class="analysis-prompt">
            <el-empty description="点击「深度分析」按钮查看文本关键词、情感强度等增强信息">
              <el-button type="primary" @click="handleDeepAnalysis" :loading="analyzing">
                <el-icon><MagicStick /></el-icon>
                开始深度分析
              </el-button>
            </el-empty>
          </div>

          <div v-else-if="analyzing" class="analyzing-state">
            <Loading :visible="true" text="正在进行深度分析..." />
          </div>

          <div v-else-if="analysisResult" class="analysis-content">
            <!-- 关键词 -->
            <div class="analysis-section">
              <h4>
                <el-icon><Key /></el-icon>
                关键词提取
              </h4>
              <div class="keywords-list">
                <el-tag
                  v-for="keyword in analysisResult.keywords.slice(0, 10)"
                  :key="keyword.keyword"
                  :type="getKeywordType(keyword.weight)"
                  effect="plain"
                  class="keyword-item"
                >
                  {{ keyword.keyword }}
                  <el-tag type="info" size="small" effect="plain">
                    {{ keyword.weight }}
                  </el-tag>
                </el-tag>
                <el-text v-if="analysisResult.keywords.length === 0" type="info" size="small">
                  暂无关键词
                </el-text>
              </div>
            </div>

            <!-- 文本统计 -->
            <div class="analysis-section">
              <h4>
                <el-icon><DataAnalysis /></el-icon>
                文本统计
              </h4>
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="字符数">
                  {{ analysisResult.stats.char_count }}
                </el-descriptions-item>
                <el-descriptions-item label="词数">
                  {{ analysisResult.stats.word_count }}
                </el-descriptions-item>
                <el-descriptions-item label="句子数">
                  {{ analysisResult.stats.sentence_count }}
                </el-descriptions-item>
                <el-descriptions-item label="段落数">
                  {{ analysisResult.stats.paragraph_count }}
                </el-descriptions-item>
                <el-descriptions-item label="平均句长">
                  {{ analysisResult.stats.avg_sentence_length.toFixed(1) }} 词
                </el-descriptions-item>
                <el-descriptions-item label="平均词长">
                  {{ analysisResult.stats.avg_word_length.toFixed(1) }} 字符
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 文本摘要 -->
            <div v-if="analysisResult.summary" class="analysis-section">
              <h4>
                <el-icon><Document /></el-icon>
                文本摘要
              </h4>
              <div class="summary-box">
                <el-text>{{ analysisResult.summary }}</el-text>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="stats-card" v-if="predictionStore.hasResult">
          <template #header>
            <span class="card-header">
              <el-icon class="header-icon"><DataAnalysis /></el-icon>
              快速统计
            </span>
          </template>

          <div class="mini-stats">
            <div class="mini-stat">
              <div class="mini-stat-label">输入长度</div>
              <div class="mini-stat-value">{{ inputText.length }} 字</div>
            </div>
            <div class="mini-stat">
              <div class="mini-stat-label">预测耗时</div>
              <div class="mini-stat-value">< 1s</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check,
  Edit,
  MagicStick,
  Trophy,
  InfoFilled,
  DocumentCopy,
  Refresh,
  DataAnalysis,
  Cpu,
  Key,
  Document,
} from '@element-plus/icons-vue'
import { usePredictionStore } from '@/stores/prediction'
import { analyzeText, type TextAnalysisResponse } from '@/api/text-analysis'
import { formatScore } from '@/utils/format'
import Loading from '@/components/common/Loading.vue'

const predictionStore = usePredictionStore()
const inputText = ref('')

// 深度分析
const analyzing = ref(false)
const analysisResult = ref<TextAnalysisResponse | null>(null)

const guideItems = [
  '输入任意中文或英文文本',
  '选择推理模型（BERT 或 VADER）',
  '点击「开始预测」按钮',
  '查看情感分析结果',
  '结果会自动保存到历史记录',
]

const resultIcon = computed(() => {
  const label = predictionStore.label.toLowerCase()
  if (label.includes('正面') || label.includes('positive')) {
    return 'success'
  }
  if (label.includes('负面') || label.includes('negative')) {
    return 'error'
  }
  return 'warning'
})

const resultIconType = computed(() => {
  const label = predictionStore.label.toLowerCase()
  if (label.includes('正面') || label.includes('positive')) {
    return 'success'
  }
  if (label.includes('负面') || label.includes('negative')) {
    return 'danger'
  }
  return 'warning'
})

const confidenceColor = computed(() => {
  const score = predictionStore.confidence
  if (score >= 0.7) return '#68C3A0'
  if (score >= 0.5) return '#E8B87C'
  return '#E87C7C'
})

onMounted(() => {
  predictionStore.fetchModels()
})

async function handlePredict() {
  await predictionStore.predictText(inputText.value)
}

// 深度分析
async function handleDeepAnalysis() {
  if (!inputText.value.trim()) {
    ElMessage.warning('请先输入文本')
    return
  }

  try {
    analyzing.value = true
    analysisResult.value = null

    const data = await analyzeText(inputText.value, predictionStore.selectedModel)
    analysisResult.value = data

    ElMessage.success('深度分析完成')
  } catch (error: any) {
    ElMessage.error(error.message || '深度分析失败')
  } finally {
    analyzing.value = false
  }
}

// 获取关键词类型
function getKeywordType(weight: number): 'success' | 'warning' | 'danger' | 'info' {
  if (weight >= 8) return 'danger'
  if (weight >= 6) return 'warning'
  if (weight >= 4) return 'primary'
  return 'info'
}

function handleCopyResult() {
  const text = `预测结果：${predictionStore.label}\n置信度：${formatScore(predictionStore.confidence)}`
  navigator.clipboard.writeText(text)
  ElMessage.success('结果已复制到剪贴板')
}

function handlePredictAnother() {
  inputText.value = ''
  predictionStore.clearResult()
  analysisResult.value = null
}
</script>

<style scoped lang="scss">
.predict-view {
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

  .main-content {
    .input-card,
    .result-card,
    .guide-card,
    .stats-card {
      margin-bottom: 24px;
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
    }

    .input-card {
      .input-wrapper {
        margin-bottom: 16px;
      }

      .action-row {
        display: flex;
        gap: 16px;
        align-items: center;

        .model-select {
          flex: 1;
          max-width: 280px;
        }

        .predict-btn {
          min-width: 160px;
          height: 48px;
          font-size: 16px;
          font-weight: 600;
          border-radius: 24px;
          background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
          border: none;
          box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }

    .result-card {
      background: linear-gradient(135deg, #F8F9FA 0%, #ffffff 100%);

      .result-content {
        .result-main {
          .result-label {
            font-size: 14px;
            color: #8A98A8;
            margin-bottom: 12px;
          }
        }

        .confidence-section {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

          .confidence-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;

            .confidence-label {
              font-size: 14px;
              color: #5A6878;
            }

            .confidence-value {
              font-size: 24px;
              font-weight: 700;
              color: #5B9A8B;
            }
          }

          .confidence-bar {
            margin-bottom: 16px;
          }

          .confidence-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            text-align: center;
            width: 100%;
          }
        }

        .quality-indicator {
          margin-top: 24px;
          padding: 16px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);

          .quality-label {
            font-size: 14px;
            color: #5A6878;
            margin-bottom: 8px;
          }

          .quality-stars {
            :deep(.el-rate) {
              height: 24px;
            }
          }
        }

        .result-actions {
          margin-top: 24px;
          display: flex;
          gap: 12px;

          .el-button {
            flex: 1;
            border-radius: 20px;
          }
        }
      }
    }

    .guide-card {
      .guide-list {
        .guide-item {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
          align-items: flex-start;

          &:last-child {
            margin-bottom: 0;
          }

          .guide-number {
            width: 28px;
            height: 28px;
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

          .guide-text {
            font-size: 14px;
            color: #5A6878;
            line-height: 28px;
          }
        }
      }

      .model-info {
        h4 {
          margin-bottom: 16px;
          font-size: 16px;
        }

        .model-comparison {
          .model-item {
            padding: 16px;
            border-radius: 8px;
            background: #F8F9FA;
            margin-bottom: 12px;
            transition: all 0.3s ease;

            &:hover {
              background: linear-gradient(135deg, rgba(91, 154, 139, 0.1) 0%, rgba(74, 139, 122, 0.1) 100%);
              transform: translateX(4px);
            }

            &:last-child {
              margin-bottom: 0;
            }

            .model-name {
              font-weight: 600;
              margin-bottom: 4px;
            }

            .model-desc {
              font-size: 12px;
              color: #8A98A8;
              margin-bottom: 8px;
            }
          }
        }
      }
    }

    .stats-card {
      .mini-stats {
        display: flex;
        gap: 16px;

        .mini-stat {
          flex: 1;
          padding: 16px;
          border-radius: 8px;
          background: linear-gradient(135deg, #F8F9FA 0%, #E8ECF0 100%);
          text-align: center;

          .mini-stat-label {
            font-size: 12px;
            color: #8A98A8;
            margin-bottom: 8px;
          }

          .mini-stat-value {
            font-size: 20px;
            font-weight: 700;
            color: #5B9A8B;
          }
        }
      }
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
  .predict-view {
    .page-header {
      h1 {
        font-size: 24px;
      }

      .subtitle {
        font-size: 14px;
      }
    }

    .main-content {
      .input-card {
        .action-row {
          flex-direction: column;

          .model-select {
            max-width: 100%;
          }

          .predict-btn {
            width: 100%;
          }
        }
      }

      .result-card {
        .result-content {
          .el-row {
            flex-direction: column;
          }
        }
      }
    }
  }

  // 分析卡片
  .analysis-card {
    .analysis-prompt {
      padding: 40px;
      text-align: center;
    }

    .analyzing-state {
      padding: 40px 0;
    }

    .analysis-content {
      .analysis-section {
        margin-bottom: 24px;

        &:last-child {
          margin-bottom: 0;
        }

        h4 {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 16px;
          color: var(--el-text-color-primary);
        }

        .keywords-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;

          .keyword-item {
            font-size: 14px;
          }
        }

        .summary-box {
          padding: 16px;
          background: var(--el-bg-color-page);
          border-radius: 8px;

          .el-text {
            line-height: 1.8;
            font-size: 15px;
          }
        }
      }
    }
  }
}
</style>
