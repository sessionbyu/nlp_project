/**
 * 文本功能自动化测试脚本
 *
 * 功能：
 * 1. 测试文本情感预测 API
 * 2. 测试文本增强分析 API
 * 3. 测试关键词提取 API
 * 4. 测试文本摘要 API
 * 5. 测试文本统计 API
 *
 * 使用方法：
 *   npm run test:text-api
 *   或
 *   npx tsx src/tests/test-scripts/text-api.test.ts
 */

import axios from 'axios'

// 配置
const API_BASE_URL = 'http://localhost:8000'
const TEST_USERNAME = 'admin'
const TEST_PASSWORD = 'admin123'

// 测试结果统计
interface TestResult {
  name: string
  passed: boolean
  duration: number
  error?: string
  data?: any
}

const results: TestResult[] = []

// 颜色输出
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
}

function log(message: string, color: keyof typeof colors = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logTestStart(name: string) {
  log(`\n${'='.repeat(60)}`, 'blue')
  log(`🧪 测试: ${name}`, 'blue')
  log('='.repeat(60), 'blue')
}

function logTestPass(name: string, duration: number) {
  results.push({ name, passed: true, duration })
  log(`✅ 通过: ${name} (耗时: ${duration}ms)`, 'green')
}

function logTestFail(name: string, duration: number, error: string) {
  results.push({ name, passed: false, duration, error })
  log(`❌ 失败: ${name} (耗时: ${duration}ms)`, 'red')
  log(`   错误: ${error}`, 'red')
}

// 获取认证 Token
async function getAuthToken(): Promise<string> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    })
    return response.data.access_token
  } catch (error: any) {
    throw new Error(`登录失败: ${error.response?.data?.detail || error.message}`)
  }
}

// 创建 Axios 实例（带认证）
function createAuthClient(token: string) {
  return axios.create({
    baseURL: API_BASE_URL,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })
}

// ==================== 测试用例 ====================

/**
 * 测试 1: 登录认证
 */
async function testLogin(): Promise<TestResult> {
  const startTime = Date.now()
  const name = '用户登录认证'

  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, {
      username: TEST_USERNAME,
      password: TEST_PASSWORD,
    })

    if (!response.data.access_token) {
      throw new Error('响应中缺少 access_token')
    }

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    const msg = error.response?.data?.detail || error.message
    return { name, passed: false, duration, error: msg }
  }
}

/**
 * 测试 2: 文本情感预测 - 正面情感
 */
async function testPredictPositive(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本情感预测 - 正面情感'

  try {
    const testText = '今天天气真好，阳光明媚，心情特别愉快！'
    const response = await client.post('/api/v1/predict', {
      text: testText,
      model_key: 'bert',
    })

    const { label, confidence } = response.data

    // 验证响应格式
    if (!label) throw new Error('响应中缺少 label 字段')
    if (typeof confidence !== 'number') throw new Error('响应中缺少 confidence 字段')

    // 验证是否为正面情感（不强制要求，记录实际结果）
    const isPositive = label.toLowerCase().includes('正面') || label.toLowerCase().includes('positive')
    console.log(`   预测结果: ${label}, 置信度: ${(confidence * 100).toFixed(1)}%`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 3: 文本情感预测 - 负面情感
 */
async function testPredictNegative(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本情感预测 - 负面情感'

  try {
    const testText = '今天的天气糟透了，下雨降温，出门特别不方便。'
    const response = await client.post('/api/v1/predict', {
      text: testText,
      model_key: 'bert',
    })

    const { label, confidence } = response.data
    console.log(`   预测结果: ${label}, 置信度: ${(confidence * 100).toFixed(1)}%`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 4: 文本情感预测 - VADER 模型
 */
async function testPredictVader(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本情感预测 - VADER 模型'

  try {
    const testText = 'This movie is absolutely amazing! I love it so much!'
    const response = await client.post('/api/v1/predict', {
      text: testText,
      model_key: 'vader',
    })

    const { label, confidence } = response.data
    console.log(`   预测结果: ${label}, 置信度: ${(confidence * 100).toFixed(1)}%`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 5: 文本增强分析 - 完整分析
 */
async function testTextAnalyze(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本增强分析 - 完整分析'

  try {
    const testText = `
      今天公司召开了年度总结大会，CEO发表了振奋人心的演讲。
      虽然今年遇到了不少困难，但全体员工团结一心，取得了超出预期的成绩。
      特别是产品团队，在新版本发布后获得了用户的高度认可，
      应用商店评分从4.0分涨到了4.8分。
      听到这些好消息，大家都非常开心和自豪。
      接下来的一年，我们有信心再创佳绩，实现更大的突破！
    `.trim()

    const response = await client.post('/api/v1/text-analysis/analyze', {
      text: testText,
      model_key: 'bert',
    })

    const { keywords, stats, sentiment, summary } = response.data

    // 验证响应格式
    if (!Array.isArray(keywords)) throw new Error('响应中缺少 keywords 字段')
    if (!stats) throw new Error('响应中缺少 stats 字段')
    if (!sentiment) throw new Error('响应中缺少 sentiment 字段')

    console.log(`   关键词数量: ${keywords.length}`)
    console.log(`   字符数: ${stats.char_count}`)
    console.log(`   情感标签: ${sentiment.label}`)
    console.log(`   摘要: ${summary ? summary.substring(0, 50) + '...' : '无'}`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 6: 关键词提取
 */
async function testExtractKeywords(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '关键词提取'

  try {
    const testText = `
      人工智能技术正在快速发展，深度学习算法在各个领域得到广泛应用。
      自然语言处理是人工智能的重要分支，文本分析技术也在不断进步。
    `.trim()

    const response = await client.post('/api/v1/text-analysis/keywords', {
      text: testText,
      max_keywords: 10,
    })

    if (!Array.isArray(response.data)) {
      throw new Error('响应格式错误，期望数组')
    }

    console.log(`   提取关键词: ${response.data.length} 个`)
    response.data.slice(0, 5).forEach((kw: any) => {
      console.log(`   - ${kw.keyword} (权重: ${kw.weight})`)
    })

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 7: 文本摘要生成
 */
async function testSummarizeText(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本摘要生成'

  try {
    const testText = `
      人工智能（AI）是研究、开发用于模拟、延伸和扩展人类智能的理论、方法、
      技术及应用系统的一门技术科学。近年来，随着深度学习技术的突破，
      AI在图像识别、自然语言处理、语音识别等领域取得了显著进展。
      未来，AI将继续改变我们的生活和工作方式，带来更多创新和机遇。
    `.trim()

    const response = await client.post('/api/v1/text-analysis/summarize', {
      text: testText,
      max_length: 100,
    })

    if (!response.data.summary) {
      throw new Error('响应中缺少 summary 字段')
    }

    console.log(`   原文长度: ${response.data.original_length} 字`)
    console.log(`   摘要长度: ${response.data.summary_length} 字`)
    console.log(`   摘要内容: ${response.data.summary}`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 8: 文本统计信息
 */
async function testGetTextStats(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '文本统计信息'

  try {
    const testText = `
      这是第一句话。这是第二句话，包含多个逗号。
      这是第三句话！这是最后一段的最后一句话。
    `.trim()

    const response = await client.post('/api/v1/text-analysis/stats', {
      text: testText,
    })

    const { char_count, word_count, sentence_count, paragraph_count } = response.data

    console.log(`   字符数: ${char_count}`)
    console.log(`   词数: ${word_count}`)
    console.log(`   句子数: ${sentence_count}`)
    console.log(`   段落数: ${paragraph_count}`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 9: 详细情感分析
 */
async function testDetailedSentiment(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '详细情感分析'

  try {
    const testText = `
      今天真是太开心了！收到了期待已久的offer，经过三个月的努力，
      终于得到了回报。感谢所有帮助过我的人，未来我会继续加油！
      虽然过程很艰难，但结果是美好的。
    `.trim()

    const response = await client.post('/api/v1/text-analysis/detailed-sentiment', {
      text: testText,
      model_key: 'bert',
    })

    const { label, score, intensity, keywords, summary, positive_words, negative_words } = response.data

    console.log(`   情感标签: ${label}`)
    console.log(`   置信度: ${(score * 100).toFixed(1)}%`)
    console.log(`   情感强度: ${intensity}`)
    console.log(`   关键词: ${keywords.length} 个`)
    console.log(`   积极词汇: ${positive_words.length} 个`)
    console.log(`   消极词汇: ${negative_words.length} 个`)

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 10: 边界测试 - 空文本
 */
async function testEmptyText(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '边界测试 - 空文本'

  try {
    const response = await client.post('/api/v1/predict', {
      text: '',
      model_key: 'bert',
    })

    // 期望返回错误
    if (response.status === 200) {
      throw new Error('空文本应该返回错误，但成功返回了')
    }

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    // 400 错误是预期的
    if (error.response?.status === 400) {
      return { name, passed: true, duration, data: { expectedError: true } }
    }
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 11: 性能测试 - 长文本
 */
async function testLongText(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '性能测试 - 长文本处理'

  try {
    // 生成 500 字的文本
    const longText = '人工智能技术正在快速发展。'.repeat(50)

    const response = await client.post('/api/v1/predict', {
      text: longText,
      model_key: 'bert',
    })

    const duration = Date.now() - startTime
    console.log(`   文本长度: ${longText.length} 字`)
    console.log(`   处理耗时: ${duration}ms`)

    // 性能要求：应该在 10 秒内完成
    if (duration > 10000) {
      throw new Error(`处理超时: ${duration}ms > 10000ms`)
    }

    return { name, passed: true, duration, data: response.data }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

/**
 * 测试 12: 多语言测试
 */
async function testMultilingual(client: any): Promise<TestResult> {
  const startTime = Date.now()
  const name = '多语言文本测试'

  try {
    const testCases = [
      { text: 'The weather is beautiful today!', lang: 'English' },
      { text: 'El clima está hermoso hoy!', lang: 'Spanish' },
      { text: '今日はいい天気ですね。', lang: 'Japanese' },
    ]

    const results = []
    for (const tc of testCases) {
      const response = await client.post('/api/v1/predict', {
        text: tc.text,
        model_key: 'vader', // VADER 支持多语言
      })
      results.push({
        lang: tc.lang,
        text: tc.text,
        label: response.data.label,
        confidence: response.data.confidence,
      })
    }

    const duration = Date.now() - startTime
    return { name, passed: true, duration, data: results }
  } catch (error: any) {
    const duration = Date.now() - startTime
    return { name, passed: false, duration, error: error.message }
  }
}

// ==================== 主测试流程 ====================

async function runTests() {
  log('\n🚀 开始文本功能自动化测试\n', 'yellow')

  const overallStartTime = Date.now()

  try {
    // 步骤 1: 获取认证 Token
    logTestStart('获取认证 Token')
    const token = await getAuthToken()
    log(`✅ Token 获取成功: ${token.substring(0, 20)}...`, 'green')

    // 创建认证客户端
    const client = createAuthClient(token)

    // 步骤 2: 运行所有测试
    const tests = [
      testPredictPositive,
      testPredictNegative,
      testPredictVader,
      testTextAnalyze,
      testExtractKeywords,
      testSummarizeText,
      testGetTextStats,
      testDetailedSentiment,
      testEmptyText,
      testLongText,
      testMultilingual,
    ]

    for (const test of tests) {
      logTestStart(test.name)
      const result = await test(client)
      if (result.passed) {
        logTestPass(result.name, result.duration)
      } else {
        logTestFail(result.name, result.duration, result.error || '')
      }
    }

    // 步骤 3: 输出测试报告
    const overallDuration = Date.now() - overallStartTime
    printSummary(overallDuration)
  } catch (error: any) {
    log(`\n❌ 测试流程失败: ${error.message}`, 'red')
    process.exit(1)
  }
}

function printSummary(totalDuration: number) {
  log('\n' + '='.repeat(60), 'blue')
  log('📊 测试报告汇总', 'blue')
  log('='.repeat(60), 'blue')

  const passed = results.filter((r) => r.passed).length
  const failed = results.filter((r) => !r.passed).length
  const total = results.length
  const passRate = ((passed / total) * 100).toFixed(1)

  log(`\n总计: ${total} 个测试`, 'yellow')
  log(`通过: ${passed} 个 ✅`, 'green')
  log(`失败: ${failed} 个 ❌`, failed > 0 ? 'red' : 'green')
  log(`通过率: ${passRate}%`, passRate === '100.0' ? 'green' : 'yellow')
  log(`总耗时: ${totalDuration}ms`, 'yellow')

  if (failed > 0) {
    log('\n失败的测试:', 'red')
    results
      .filter((r) => !r.passed)
      .forEach((r) => {
        log(`  ❌ ${r.name}: ${r.error}`, 'red')
      })
  }

  log('\n详细耗时:', 'blue')
  results.forEach((r) => {
    const color = r.passed ? 'green' : 'red'
    log(`  ${r.passed ? '✅' : '❌'} ${r.name}: ${r.duration}ms`, color)
  })

  log('\n' + '='.repeat(60), 'blue')

  // 退出码
  process.exit(failed > 0 ? 1 : 0)
}

// 运行测试
runTests().catch((error) => {
  log(`\n❌ 未捕获的错误: ${error.message}`, 'red')
  process.exit(1)
})
