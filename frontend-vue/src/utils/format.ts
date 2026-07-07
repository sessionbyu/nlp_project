import dayjs from 'dayjs'

export function formatScore(score: number, decimals: number = 4): string {
  return score.toFixed(decimals)
}

export function formatScorePercent(score: number, decimals: number = 1): string {
  return `${(score * 100).toFixed(decimals)}%`
}

export function formatDateTime(
  dateTime: string,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  return dayjs(dateTime).format(format)
}

export function formatLabel(label: string): { text: string; type: 'success' | 'danger' | 'info' } {
  const lower = label.toLowerCase()
  if (lower.includes('正面') || lower.includes('positive')) {
    return { text: '🟢 正面', type: 'success' }
  }
  if (lower.includes('负面') || lower.includes('negative')) {
    return { text: '🔴 负面', type: 'danger' }
  }
  return { text: `⚪ ${label}`, type: 'info' }
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (!text || text.length <= maxLength) {
    return text
  }
  return text.slice(0, maxLength) + '...'
}

export function formatNumber(num: number): string {
  return num.toLocaleString()
}

export function downloadCSV(data: Record<string, unknown>[], filename: string): void {
  if (!data.length) {
    return
  }

  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map((row) =>
      headers.map((header) => {
        const value = row[header]
        const stringValue = String(value ?? '')
        // 如果包含逗号或引号，需要包裹引号
        if (stringValue.includes(',') || stringValue.includes('"')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      }).join(',')
    ),
  ].join('\n')

  const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
