export interface PredictRequest {
  text: string
  model_key?: string
}

export interface PredictResponse {
  label: string
  score: number
  model_key: string
  input_text?: string
}

export interface ModelsResponse {
  available_models: string[]
  default_model: string
}

export interface HistoryRecord {
  id: number
  input_text: string
  label: string
  score: number
  model_key?: string
  source_ip?: string
  created_at: string
}

export interface HistoryQueryParams {
  page?: number
  page_size?: number
  label?: string
  min_score?: number
  max_score?: number
  keyword?: string
  start_date?: string
  end_date?: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  total_pages: number
  records: T[]
}

export interface RecentResponse {
  records: HistoryRecord[]
}

export interface StatsResponse {
  total_predictions: number
  label_distribution: Record<string, number>
  average_score: number
}

export interface BatchPredictItem {
  text: string
  success: boolean
  result?: {
    label: string
    score: number
    model_key: string
  }
  error?: string
}

export interface BatchPredictResponse {
  results: BatchPredictItem[]
  total: number
  success: number
  failed: number
}
