import { request } from './request'
import type {
  HistoryRecord,
  HistoryQueryParams,
  PaginatedResponse,
  RecentResponse,
} from '@/types/predict'

export function queryHistory(
  params: HistoryQueryParams
): Promise<PaginatedResponse<HistoryRecord>> {
  return request.get('/api/v1/history', { params })
}

export function getRecentHistory(limit: number = 10): Promise<RecentResponse> {
  return request.get('/api/v1/history/recent', { params: { limit } })
}
