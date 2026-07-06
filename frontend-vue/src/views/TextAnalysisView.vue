<template>
  <div class="text-analysis-view">
    <div class="page-header">
      <h1>📝 文本增强分析</h1>
      <p class="subtitle">深度分析文本内容，提取关键信息</p>
    </div>

    <!-- 文本输入 -->
    <el-card class="input-card fade-in">
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon class="header-icon"><Edit /></el-icon>
            文本输入
          </span>
          <el-button
            type="primary"
            @click="handleAnalyze"
            :loading="analyzing"
            :disabled="!text.trim()"
          >
            <el-icon><MagicStick /></el-icon>
            开始分析
          </el-button>
        </div>
      </template>

      <el-input
        v-model="text"
        type="textarea"
        :rows="6"
        placeholder="请输入要分析的文本..."
        @input="handleTextChange"
      />
      <div class="input-tip">
        <el-text type="info" size="small">
          已输入 {{ charCount }} 字符，{{ wordCount }} 词
        </el-text>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <div v-if="analyzing" class="analyzing-state">
      <Loading :visible="true" text="正在分析文本..." />
    </div>

    <!-- 分析结果 -->
    <div v-else-if="result" class="analysis-results">
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="6">
          <StatCard
            :icon="Document"
            label="字符数"
            :value="result.stats.char_count"
            color-type="primary"
            size="small"
          />
        </el-col>
        <el-col :xs="24" :sm="6">
          <StatCard
            :icon="Coin"
            label="词数"
            :value="result.stats.word_count"
            color-type="success"
            size="small"
          />
        </el-col>
        <el-col :xs="24" :sm="6">
          <StatCard
            :icon="ChatDotRound"
            label="句子数"
            :value="result.stats.sentence_count"
            color-type="warning"
            size="small"
          />
        </el-col>
        <el-col :xs="24" :sm="6">
          <StatCard
            :icon="Histogram"
            label="段落数"
            :value="result.stats.paragraph_count"
            color-type="info"
            size="small"
          />
        </el-col>
      </el-row>

      <!-- 情感分析 -->
      <el-card v-if="result.sentiment" class="sentiment-card fade-in">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon class="header-icon"><Cpu /></el-icon>
              情感分析
            </span>
          </div>
        </template>

        <div class="sentiment-content">
          <el-row :gutter="30">
            <el-col :xs="24" :sm="8">
              <div class="sentiment-main">
                <div class="sentiment-label">情感标签</div>
                <el-tag
                  :type="getSentimentType(result.sentiment.label)"
                  effect="dark"
                  size="large"
                  class="sentiment-tag"
                >
                  {{ getSentimentText(result.sentiment.label) }}
                </el-tag>
                <div class="sentiment-score">
                  置信度: {{ (result.sentiment.score * 100).toFixed(1) }}%
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="8">
              <div class="sentiment-intensity">
                <div class="intensity-label">情感强度</div>
                <el-progress
                  :percentage="getIntensityPercent(result.sentiment.intensity)"
                  :color="getIntensityColor(result.sentiment.intensity)"
                  :stroke-width="20"
                />
                <div class="intensity-text">{{ result.sentiment.intensity }}</div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="8">
              <div class="sentiment-summary">
                <div class="summary-label">分析摘要</div>
                <el-text class="summary-text">{{ result.sentiment.summary }}</el-text>
              </div>
            </el-col>
          </el-row>

          <!-- 关键词 -->
          <div v-if="result.sentiment.keywords.length > 0" class="sentiment-keywords">
            <div class="keywords-title">情感关键词</div>
            <div class="keywords-list">
              <el-tag
                v-for="keyword in result.sentiment.keywords"
                :key="keyword.keyword"
                :type="getKeywordType(keyword.weight)"
                effect="plain"
                class="keyword-tag"
              >
                {{ keyword.keyword }}
                <el-tag type="info" size="small" effect="plain">
                  {{ keyword.weight }}
                </el-tag>
              </el-tag>
            </div>
          </div>

          <!-- 积极/消极词汇 -->
          <el-row :gutter="20" class="words-row">
            <el-col :xs="24" :sm="12">
              <div class="words-section positive">
                <div class="words-title">
                  <el-icon><CircleCheck /></el-icon>
                  积极词汇 ({{ result.sentiment.positive_words.length }})
                </div>
                <div class="words-list">
                  <el-tag
                    v-for="word in result.sentiment.positive_words.slice(0, 10)"
                    :key="word"
                    type="success"
                    effect="plain"
                    size="small"
                  >
                    {{ word }}
                  </el-tag>
                  <el-text v-if="result.sentiment.positive_words.length === 0" type="info" size="small">
                    无
                  </el-text>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="12">
              <div class="words-section negative">
                <div class="words-title">
                  <el-icon><CircleClose /></el-icon>
                  消极词汇 ({{ result.sentiment.negative_words.length }})
                </div>
                <div class="words-list">
                  <el-tag
                    v-for="word in result.sentiment.negative_words.slice(0, 10)"
                    :key="word"
                    type="danger"
                    effect="plain"
                    size="small"
                  >
                    {{ word }}
                  </el-tag>
                  <el-text v-if="result.sentiment.negative_words.length === 0" type="info" size="small">
                    无
                  </el-text>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 关键词提取 -->
      <el-card v-if="result.keywords.length > 0" class="keywords-card fade-in">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon class="header-icon"><Key /></el-icon>
              关键词提取
            </span>
            <el-tag type="info" effect="plain">
              共 {{ result.keywords.length }} 个关键词
            </el-tag>
          </div>
        </template>

        <div class="keywords-cloud">
          <div
            v-for="keyword in result.keywords"
            :key="keyword.keyword"
            class="keyword-item"
            :style="{
              fontSize: `${12 + keyword.weight * 2}px`,
              opacity: 0.6 + keyword.weight * 0.4,
            }"
            :title="`权重: ${keyword.weight}, 频率: ${(keyword.frequency * 100).toFixed(1)}%`"
          >
            {{ keyword.keyword }}
          </div>
        </div>
      </el-card>

      <!-- 文本统计详情 -->
      <el-card class="stats-detail-card fade-in">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon class="header-icon"><DataAnalysis /></el-icon>
              文本统计详情
            </span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="字符数">
            {{ result.stats.char_count }}
          </el-descriptions-item>
          <el-descriptions-item label="词数">
            {{ result.stats.word_count }}
          </el-descriptions-item>
          <el-descriptions-item label="句子数">
            {{ result.stats.sentence_count }}
          </el-descriptions-item>
          <el-descriptions-item label="段落数">
            {{ result.stats.paragraph_count }}
          </el-descriptions-item>
          <el-descriptions-item label="平均句长">
            {{ result.stats.avg_sentence_length.toFixed(1) }} 词
          </el-descriptions-item>
          <el-descriptions-item label="平均词长">
            {{ result.stats.avg_word_length.toFixed(1) }} 字符
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 文本摘要 -->
      <el-card v-if="result.summary" class="summary-card fade-in">
        <template #header>
          <div class="card-header">
            <span class="header-title">
              <el-icon class="header-icon"><Document /></el-icon>
              文本摘要
            </span>
          </div>
        </template>

        <div class="summary-content">
          <el-text>{{ result.summary }}</el-text>
          <div class="summary-meta">
            <el-text type="info" size="small">
              原文 {{ result.stats.char_count }} 字，摘要 {{ result.summary.length }} 字
            </el-text>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="请输入文本并开始分析" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  MagicStick,
  Document,
  Coin,
  ChatDotRound,
  Histogram,
  Cpu,
  Key,
  CircleCheck,
  CircleClose,
  DataAnalysis,
} from '@element-plus/icons-vue'
import { analyzeText, type TextAnalysisResponse } from '@/api/text-analysis'
import StatCard from '@/components/common/StatCard.vue'
import Loading from '@/components/common/Loading.vue'

// 状态
const text = ref('')
const analyzing = ref(false)
const result = ref<TextAnalysisResponse | null>(null)

// 计算属性
const charCount = computed(() => text.value.length)

const wordCount = computed(() => {
  if (!text.value.trim()) return 0
  return text.value.trim().split(/\s+/).length
})

// 文本变化
const handleTextChange = () => {
  // 可以添加防抖
}

// 开始分析
const handleAnalyze = async () => {
  if (!text.value.trim()) {
    ElMessage.warning('请输入文本')
    return
  }

  try {
    analyzing.value = true
    result.value = null

    const data = await analyzeText(text.value)
    result.value = data

    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error(error.message || '分析失败')
  } finally {
    analyzing.value = false
  }
}

// 获取情感类型
const getSentimentType = (label: string) => {
  const typeMap: Record<string, string> = {
    positive: 'success',
    negative: 'danger',
    neutral: 'info',
  }
  return typeMap[label] || 'info'
}

// 获取情感文本
const getSentimentText = (label: string) => {
  const textMap: Record<string, string> = {
    positive: '正面',
    negative: '负面',
    neutral: '中性',
  }
  return textMap[label] || label
}

// 获取情感强度百分比
const getIntensityPercent = (intensity: string) => {
  const intensityMap: Record<string, number> = {
    '弱': 33,
    '中': 66,
    '强': 100,
    'weak': 33,
    'medium': 66,
    'strong': 100,
  }
  return intensityMap[intensity] || 50
}

// 获取情感强度颜色
const getIntensityColor = (intensity: string) => {
  const colorMap: Record<string, string> = {
    '弱': 'var(--el-color-info)',
    '中': 'var(--el-color-warning)',
    '强': 'var(--el-color-danger)',
    'weak': 'var(--el-color-info)',
    'medium': 'var(--el-color-warning)',
    'strong': 'var(--el-color-danger)',
  }
  return colorMap[intensity] || 'var(--el-color-primary)'
}

// 获取关键词类型
const getKeywordType = (weight: number) => {
  if (weight >= 8) return 'danger'
  if (weight >= 6) return 'warning'
  if (weight >= 4) return 'primary'
  return 'info'
}
</script>

<style scoped lang="scss">
.text-analysis-view {
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

.input-card {
  margin-bottom: 20px;

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

  .input-tip {
    margin-top: 8px;
  }
}

.analyzing-state {
  padding: 60px 0;
}

.analysis-results {
  .stats-row {
    margin-bottom: 20px;
  }

  .sentiment-card,
  .keywords-card,
  .stats-detail-card,
  .summary-card {
    margin-bottom: 20px;
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

  .sentiment-content {
    .sentiment-main {
      text-align: center;
      padding: 20px;

      .sentiment-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 12px;
      }

      .sentiment-tag {
        font-size: 18px;
        padding: 12px 24px;
      }

      .sentiment-score {
        margin-top: 12px;
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
    }

    .sentiment-intensity {
      text-align: center;
      padding: 20px;

      .intensity-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 12px;
      }

      .intensity-text {
        margin-top: 8px;
        font-weight: 600;
      }
    }

    .sentiment-summary {
      padding: 20px;

      .summary-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 12px;
      }

      .summary-text {
        line-height: 1.6;
      }
    }

    .sentiment-keywords {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid var(--el-border-color-light);

      .keywords-title {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 16px;
      }

      .keywords-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;

        .keyword-tag {
          font-size: 14px;
        }
      }
    }

    .words-row {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid var(--el-border-color-light);

      .words-section {
        &.positive {
          .words-title {
            color: var(--el-color-success);
          }
        }

        &.negative {
          .words-title {
            color: var(--el-color-danger);
          }
        }

        .words-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 12px;
        }

        .words-list {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }
      }
    }
  }

  .keywords-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 16px;
    background: var(--el-bg-color-page);
    border-radius: 8px;

    .keyword-item {
      padding: 8px 16px;
      background: var(--el-color-primary-light-9);
      color: var(--el-color-primary);
      border-radius: 20px;
      cursor: default;
      transition: all 0.3s;

      &:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    }
  }

  .summary-content {
    padding: 16px;
    background: var(--el-bg-color-page);
    border-radius: 8px;

    .summary-text {
      line-height: 1.8;
      font-size: 16px;
    }

    .summary-meta {
      margin-top: 12px;
      text-align: right;
    }
  }
}
</style>
