import { request } from './request'
import type { StatsResponse } from '@/types/predict'

export function getStats(): Promise<StatsResponse> {
  return request.get('/api/v1/history/stats')
}
