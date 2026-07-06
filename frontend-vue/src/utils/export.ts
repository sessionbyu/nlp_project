/**
 * 高级导出工具
 *
 * 功能：
 * 1. CSV 导出
 * 2. JSON 导出
 * 3. Excel 导出
 */

/**
 * 导出为 CSV
 *
 * @param data 数据
 * @param headers 表头
 * @param filename 文件名
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  headers: { key: keyof T; label: string }[],
  filename: string = 'export.csv'
) {
  if (data.length === 0) {
    throw new Error('数据为空')
  }

  // 构建 CSV 内容
  const headerRow = headers.map((h) => `"${h.label}"`).join(',')
  const dataRows = data.map((item) =>
    headers
      .map((h) => {
        const value = item[h.key]
        // 处理特殊字符
        const strValue = String(value ?? '')
        // 如果包含逗号、引号或换行符，需要用引号包围
        if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
          return `"${strValue.replace(/"/g, '""')}"`
        }
        return `"${strValue}"`
      })
      .join(',')
  )

  const csvContent = [headerRow, ...dataRows].join('\n')

  // 添加 BOM 以支持中文
  const blob = new Blob(['﻿' + csvContent], { type: 'text/csv;charset=utf-8;' })
  downloadFile(blob, filename)

  return true
}

/**
 * 导出为 JSON
 *
 * @param data 数据
 * @param filename 文件名
 */
export function exportToJSON<T>(data: T[], filename: string = 'export.json') {
  if (data.length === 0) {
    throw new Error('数据为空')
  }

  const jsonContent = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
  downloadFile(blob, filename)

  return true
}

/**
 * 导出为 Excel (简化版 - 使用 CSV 格式但保存为 .xlsx)
 *
 * @param data 数据
 * @param headers 表头
 * @param filename 文件名
 */
export function exportToExcel<T extends Record<string, any>>(
  data: T[],
  headers: { key: keyof T; label: string }[],
  filename: string = 'export.xlsx'
) {
  if (data.length === 0) {
    throw new Error('数据为空')
  }

  // 构建 TSV (Tab-Separated Values) 格式，Excel 可以直接打开
  const headerRow = headers.map((h) => h.label).join('\t')
  const dataRows = data.map((item) =>
    headers
      .map((h) => {
        const value = item[h.key]
        return String(value ?? '').replace(/\t/g, ' ').replace(/\n/g, ' ')
      })
      .join('\t')
  )

  const tsvContent = [headerRow, ...dataRows].join('\n')
  const blob = new Blob(['﻿' + tsvContent], { type: 'application/vnd.ms-excel;charset=utf-8;' })
  downloadFile(blob, filename)

  return true
}

/**
 * 下载文件
 *
 * @param blob 文件内容
 * @param filename 文件名
 */
function downloadFile(blob: Blob, filename: string) {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(link.href)
}

/**
 * 格式化文件名
 *
 * @param prefix 前缀
 * @param extension 扩展名
 * @returns 格式化后的文件名
 */
export function formatFilename(prefix: string, extension: string): string {
  const date = new Date().toISOString().split('T')[0]
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0]
  return `${prefix}_${timestamp}.${extension}`
}
