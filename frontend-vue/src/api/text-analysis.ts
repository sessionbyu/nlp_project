/**
 * 文本分析 API
 *
 * 功能：
 * 1. 关键词提取
 * 2. 文本摘要
 * 3. 文本统计
 * 4. 详细情感分析
 */

import { request } from './request'

/**
 * 关键词
 */
export interface Keyword {
  keyword: string
  weight: number
  frequency: number
}

/**
 * 文本统计
 */
export interface TextStats {
  char_count: number
  word_count: number
  sentence_count: number
  paragraph_count: number
  avg_sentence_length: number
  avg_word_length: number
}

/**
 * 详细情感分析
 */
export interface DetailedSentiment {
  label: string
  score: number
  intensity: string
  keywords: Keyword[]
  summary: string
  positive_words: string[]
  negative_words: string[]
}

/**
 * 文本分析响应
 */
export interface TextAnalysisResponse {
  text: string
  keywords: Keyword[]
  summary?: string
  stats: TextStats
  sentiment?: DetailedSentiment
}

/**
 * 提取关键词
 *
 * @param text 文本内容
 * @param maxKeywords 最大关键词数量
 * @returns 关键词列表
 */
export function extractKeywords(
  text: string,
  maxKeywords: number = 10
) {
  return request.post<Keyword[]>('/api/v1/text-analysis/keywords', {
    text,
    max_keywords: maxKeywords,
  })
}

/**
 * 生成文本摘要
 *
 * @param text 文本内容
 * @param maxLength 摘要最大长度
 * @returns 文本摘要
 */
export function summarizeText(
  text: string,
  maxLength: number = 200
) {
  return request.post<{ summary: string; original_length: number; summary_length: number }>(
    '/api/v1/text-analysis/summarize',
    { text, max_length: maxLength }
  )
}

/**
 * 获取文本统计信息
 *
 * @param text 文本内容
 * @returns 文本统计
 */
export function getTextStats(text: string) {
  return request.post<TextStats>('/api/v1/text-analysis/stats', { text })
}

/**
 * 详细情感分析
 *
 * @param text 文本内容
 * @param modelKey 模型key
 * @returns 详细情感分析
 */
export function analyzeSentimentDetail(
  text: string,
  modelKey: string = 'bert'
) {
  return request.post<DetailedSentiment>('/api/v1/text-analysis/detailed-sentiment', {
    text,
    model_key: modelKey,
  })
}

/**
 * 完整文本分析
 *
 * @param text 文本内容
 * @param modelKey 模型key
 * @returns 完整分析结果
 */
export function analyzeText(text: string, modelKey: string = 'bert') {
  return request.post<TextAnalysisResponse>('/api/v1/text-analysis/analyze', {
    text,
    model_key: modelKey,
  })
}
