export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  page_size: number
  total_pages: number
  records: T[]
}
