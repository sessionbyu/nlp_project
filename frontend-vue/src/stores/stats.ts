import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getStats } from '@/api/stats'
import type { StatsResponse } from '@/types/predict'

export const useStatsStore = defineStore('stats', () => {
  const stats = ref<StatsResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const totalPredictions = computed(() => stats.value?.total_predictions || 0)
  const averageScore = computed(() => stats.value?.average_score || 0)
  const labelDistribution = computed(() => stats.value?.label_distribution || {})

  const positiveCount = computed(() => labelDistribution.value['正面'] || 0)
  const negativeCount = computed(() => labelDistribution.value['负面'] || 0)
  const totalCount = computed(() => positiveCount.value + negativeCount.value)
  const positiveRatio = computed(() =>
    totalCount.value > 0 ? (positiveCount.value / totalCount.value) * 100 : 0
  )

  async function fetchStats() {
    loading.value = true
    error.value = null

    try {
      stats.value = await getStats()
    } catch (e) {
      error.value = '获取统计数据失败'
      console.error('获取统计失败:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    stats,
    loading,
    error,
    totalPredictions,
    averageScore,
    labelDistribution,
    positiveCount,
    negativeCount,
    totalCount,
    positiveRatio,
    fetchStats,
  }
})
