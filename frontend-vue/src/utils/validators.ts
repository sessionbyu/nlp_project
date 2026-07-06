export function validateText(text: string, minLength: number = 1, maxLength: number = 5000): { valid: boolean; message: string } {
  if (!text || !text.trim()) {
    return { valid: false, message: '文本不能为空' }
  }

  const trimmed = text.trim()

  if (trimmed.length < minLength) {
    return { valid: false, message: `文本长度不能少于 ${minLength} 个字符` }
  }

  if (trimmed.length > maxLength) {
    return { valid: false, message: `文本长度不能超过 ${maxLength} 个字符` }
  }

  return { valid: true, message: '' }
}

export function validateScore(score: number): { valid: boolean; message: string } {
  if (typeof score !== 'number' || isNaN(score)) {
    return { valid: false, message: '分数必须是数字' }
  }

  if (score < 0 || score > 1) {
    return { valid: false, message: '分数必须在 0 到 1 之间' }
  }

  return { valid: true, message: '' }
}

export function validatePage(page: number, totalPages: number): { valid: boolean; message: string } {
  if (!Number.isInteger(page) || page < 1) {
    return { valid: false, message: '页码必须大于等于 1' }
  }

  if (totalPages > 0 && page > totalPages) {
    return { valid: false, message: `页码不能超过 ${totalPages}` }
  }

  return { valid: true, message: '' }
}
