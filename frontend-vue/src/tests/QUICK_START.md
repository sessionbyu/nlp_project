# 文本功能测试快速启动指南

## 🚀 5分钟快速开始

本指南将帮助你在 5 分钟内完成文本功能的基本测试。

---

## 前置条件

✅ 后端服务运行中：`http://localhost:8000`
✅ 前端服务运行中：`http://localhost:5173`
✅ 已登录系统（账号：`admin` / 密码：`admin123`）

---

## 方法 1: 前端 UI 测试（推荐）

### 步骤 1: 打开预测页面

1. 在浏览器中打开：`http://localhost:5173/predict`
2. 或从侧边栏点击"📝 文本预测"

### 步骤 2: 测试文本预测

**快速测试（正面情感）：**
```
今天天气真好，心情特别愉快！
```
- 选择模型：BERT
- 点击"🚀 开始预测"
- 验证：3秒内看到情感标签"正面"和置信度

**快速测试（负面情感）：**
```
今天的天气糟透了，非常失望。
```
- 选择模型：BERT
- 点击"🚀 开始预测"
- 验证：3秒内看到情感标签"负面"和置信度

**快速测试（中性情感）：**
```
今天下午三点在会议室开会讨论项目。
```
- 选择模型：BERT
- 点击"🚀 开始预测"
- 验证：3秒内看到情感标签"中性"和置信度

### 步骤 3: 测试文本增强分析

1. 打开：`http://localhost:5173/text-analysis`
2. 或从侧边栏点击"📝 文本增强分析"
3. 输入文本（建议 100-300 字）
4. 点击"开始分析"
5. 验证：看到完整的分析结果（统计、情感、关键词等）

---

## 方法 2: API 自动化测试

### 步骤 1: 运行后端 API 健康检查

```bash
cd /path/to/nlp_project
./backend/scripts/check-api-health.sh
```

**预期输出：**
```
✅ 所有测试通过！
总计: 3 个测试
通过: 3 个 ✓
失败: 0 个 ✗
通过率: 100.0%
```

### 步骤 2: 运行前端 API 集成测试

```bash
cd frontend-vue
npx tsx src/tests/test-scripts/text-api.test.ts
```

**预期输出：**
```
🧪 测试: 文本情感预测 - 正面情感
✅ 通过: 文本情感预测 - 正面情感 (耗时: 1205ms)
预测结果: 正面, 置信度: 85.3%

📊 测试报告汇总
总计: 11 个测试
通过: 11 个 ✅
失败: 0 个 ❌
通过率: 100.0%
```

---

## 方法 3: curl 手动测试

### 步骤 1: 获取 Token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: ${TOKEN:0:20}..."
```

### 步骤 2: 测试文本预测

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"今天天气真好，心情特别愉快！","model_key":"bert"}' | \
  python3 -m json.tool
```

**预期响应：**
```json
{
  "label": "正面",
  "confidence": 0.856,
  "model_key": "bert",
  "text": "今天天气真好，心情特别愉快！"
}
```

### 步骤 3: 测试获取模型列表

```bash
curl -X GET http://localhost:8000/api/v1/models \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -m json.tool
```

**预期响应：**
```json
{
  "available_models": ["vader", "bert"],
  "default_model": "bert"
}
```

---

## 测试数据准备

### 📄 测试文本库

详细的测试文本数据集已准备在：
```
frontend-vue/src/tests/test-data/text-test-dataset.md
```

**包含内容：**
- ✅ 正面情感文本（短/中/长）
- ✅ 负面情感文本（短/中/长）
- ✅ 中性情感文本
- ✅ 混合情感文本
- ✅ 特殊格式文本（emoji、英文混合等）
- ✅ 边界测试文本（极短、超长、空文本）
- ✅ 多语言测试文本

**快速复制使用：**

**正面：**
```
今天天气真好，阳光明媚，心情特别愉快！
```

**负面：**
```
今天的天气糟透了，下雨降温，出门特别不方便。
```

**中性：**
```
今天下午三点在会议室开会，讨论下个季度的计划。
```

---

## 常见问题排查

### ❌ 后端服务未启动

**症状：** API 请求超时或连接被拒绝

**解决：**
```bash
cd /path/to/nlp_project
docker-compose up -d
# 或
cd backend && uvicorn app.main:app --reload
```

### ❌ 前端服务未启动

**症状：** 浏览器打不开 `http://localhost:5173`

**解决：**
```bash
cd frontend-vue
npm run dev
```

### ❌ 登录失败

**症状：** 登录时提示"用户名或密码错误"

**解决：**
1. 确认账号：`admin`
2. 确认密码：`admin123`
3. 清除浏览器缓存后重试
4. 检查后端日志

### ❌ 预测无响应

**症状：** 点击"开始预测"后一直加载

**排查：**
1. 打开浏览器控制台 (F12)
2. 查看 Network 标签，找到 `/api/v1/predict` 请求
3. 检查响应状态码和内容
4. 查看后端日志是否有错误

### ❌ 预测结果不准确

**说明：** 这不是 bug，是正常的 AI 模型行为

**改进：**
- 使用 BERT 模型（准确度更高）
- 输入更明确的文本
- 避免歧义和复杂句式

---

## 📊 测试结果记录

### 测试日期：__________

**测试人员：** __________

#### 基本功能测试

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 文本输入 | ⬜ 通过 / ❌ 失败 | |
| 模型选择 | ⬜ 通过 / ❌ 失败 | |
| 文本预测（正面） | ⬜ 通过 / ❌ 失败 | |
| 文本预测（负面） | ⬜ 通过 / ❌ 失败 | |
| 文本预测（中性） | ⬜ 通过 / ❌ 失败 | |
| 文本增强分析 | ⬜ 通过 / ❌ 失败 | |
| 结果复制 | ⬜ 通过 / ❌ 失败 | |
| 再次预测 | ⬜ 通过 / ❌ 失败 | |

#### API 测试

| 测试项 | 状态 | 响应时间 | 备注 |
|--------|------|----------|------|
| 登录 API | ⬜ 通过 / ❌ 失败 | ___ms | |
| 预测 API | ⬜ 通过 / ❌ 失败 | ___ms | |
| 模型列表 API | ⬜ 通过 / ❌ 失败 | ___ms | |

#### 发现的问题

1. ___________________________________
2. ___________________________________
3. ___________________________________

---

## 📚 更多资源

### 测试文档

- 📄 **测试数据集**：`frontend-vue/src/tests/test-data/text-test-dataset.md`
- 📋 **完整测试清单**：`frontend-vue/src/tests/test-docs/comprehensive-test-checklist.md`
- 🧪 **自动化测试脚本**：`frontend-vue/src/tests/test-scripts/text-api.test.ts`
- 🔍 **API 健康检查**：`backend/scripts/check-api-health.sh`

### 相关文档

- 📖 **API 文档**：`http://localhost:8000/docs`
- 📊 **API 规范**：`http://localhost:8000/openapi.json`
- 🏥 **健康检查**：`http://localhost:8000/api/v1/health`
- 📈 **监控指标**：`http://localhost:8000/api/v1/metrics`

---

## 💡 测试技巧

### 1. 使用开发者工具

打开浏览器控制台 (F12)：
- **Console 标签**：查看日志和错误
- **Network 标签**：查看 API 请求和响应
- **Application 标签**：查看 LocalStorage 中的 Token

### 2. 快速清空测试数据

```javascript
// 在控制台执行
localStorage.clear()
sessionStorage.clear()
location.reload()
```

### 3. 查看实时日志

```bash
# 后端日志
cd backend && docker-compose logs -f app

# 前端日志
# 查看浏览器控制台
```

### 4. 使用测试账号

```
账号：admin
密码：admin123
权限：管理员（可访问所有功能）
```

---

**祝你测试顺利！** 🎉

如有问题，请查看完整文档或联系开发团队。
