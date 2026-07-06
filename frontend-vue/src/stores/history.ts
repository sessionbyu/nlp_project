import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { queryHistory, getRecentHistory } from '@/api/history'
import type { HistoryRecord, HistoryQueryParams, PaginatedResponse } from '@/types/predict'

interface FilterState {
  page: number
  page_size: number
  label: string
  keyword: string
  min_score: number
  max_score: number
  useDateFilter: boolean
  startDate: string
  endDate: string
}

export const useHistoryStore = defineStore('history', () => {
  const records = ref<HistoryRecord[]>([])
  const recentRecords = ref<HistoryRecord[]>([])
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const totalPages = ref(0)
  const error = ref<string | null>(null)

  const filters = ref<FilterState>({
    page: 1,
    page_size: 20,
    label: '全部',
    keyword: '',
    min_score: 0,
    max_score: 1,
    useDateFilter: false,
    startDate: '',
    endDate: '',
  })

  const hasRecords = computed(() => records.value.length > 0)
  const hasRecentRecords = computed(() => recentRecords.value.length > 0)

  async function fetchHistory() {
    loading.value = true
    error.value = null

    try {
      const params: HistoryQueryParams = {
        page: filters.value.page,
        page_size: filters.value.page_size,
      }

      if (filters.value.label && filters.value.label !== '全部') {
        params.label = filters.value.label
      }

      if (filters.value.keyword) {
        params.keyword = filters.value.keyword
      }

      if (filters.value.min_score > 0) {
        params.min_score = filters.value.min_score
      }

      if (filters.value.max_score < 1) {
        params.max_score = filters.value.max_score
      }

      if (filters.value.useDateFilter) {
        if (filters.value.startDate) {
          params.start_date = filters.value.startDate
        }
        if (filters.value.endDate) {
          params.end_date = filters.value.endDate
        }
      }

      const data: PaginatedResponse<HistoryRecord> = await queryHistory(params)

      records.value = data.records
      total.value = data.total
      currentPage.value = data.page
      totalPages.value = data.total_pages
    } catch (e) {
      error.value = '查询失败，请重试'
      console.error('查询历史记录失败:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchRecentHistory(limit: number = 10) {
    try {
      const data = await getRecentHistory(limit)
      recentRecords.value = data.records
    } catch (e) {
      console.error('获取最近记录失败:', e)
    }
  }

  function updateFilters(newFilters: Partial<FilterState>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function setPage(page: number) {
    filters.value.page = page
    fetchHistory()
  }

  function resetFilters() {
    filters.value = {
      page: 1,
      page_size: 20,
      label: '全部',
      keyword: '',
      min_score: 0,
      max_score: 1,
      useDateFilter: false,
      startDate: '',
      endDate: '',
    }
  }

  return {
    records,
    recentRecords,
    loading,
    total,
    currentPage,
    totalPages,
    error,
    filters,
    hasRecords,
    hasRecentRecords,
    fetchHistory,
    fetchRecentHistory,
    updateFilters,
    setPage,
    resetFilters,
  }
})
