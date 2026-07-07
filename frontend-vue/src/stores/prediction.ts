import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { predict, getAvailableModels } from '@/api/predict'
import type { PredictResponse, ModelsResponse } from '@/types/predict'

export const usePredictionStore = defineStore('prediction', () => {
  const result = ref<PredictResponse | null>(null)
  const loading = ref(false)
  const models = ref<string[]>([])
  const selectedModel = ref('bert')
  const error = ref<string | null>(null)

  const hasResult = computed(() => result.value !== null)
  const confidence = computed(() => result.value?.score || 0)
  const label = computed(() => result.value?.label || '')

  async function predictText(text: string) {
    if (!text.trim()) {
      error.value = '请输入文本'
      return
    }

    loading.value = true
    error.value = null

    try {
      result.value = await predict({
        text: text.trim(),
        model_key: selectedModel.value,
      })
    } catch (e) {
      error.value = '预测失败，请重试'
      console.error('预测失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchModels() {
    try {
      const data: ModelsResponse = await getAvailableModels()
      models.value = data.available_models
      selectedModel.value = data.default_model
    } catch (e) {
      console.error('获取模型列表失败:', e)
    }
  }

  function setModel(modelKey: string) {
    selectedModel.value = modelKey
  }

  function clearResult() {
    result.value = null
    error.value = null
  }

  return {
    result,
    loading,
    models,
    selectedModel,
    error,
    hasResult,
    confidence,
    label,
    predictText,
    fetchModels,
    setModel,
    clearResult,
  }
})
