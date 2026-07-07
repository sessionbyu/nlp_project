import { request } from './request'
import type { PredictRequest, PredictResponse, ModelsResponse } from '@/types/predict'

export function predict(data: PredictRequest): Promise<PredictResponse> {
  return request.post('/api/v1/predict', data)
}

export function getAvailableModels(): Promise<ModelsResponse> {
  return request.get('/api/v1/models')
}
