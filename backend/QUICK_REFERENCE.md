# 新增功能快速参考指南

## 快速导航

### 📁 新增文件清单

#### 服务层 (Services)
1. `backend/app/services/file_upload.py` - 文件上传服务
2. `backend/app/services/celery_tasks.py` - Celery异步任务
3. `backend/app/services/text_analysis.py` - 文本分析服务
4. `backend/app/services/websocket.py` - WebSocket连接管理
5. `backend/app/utils/i18n.py` - 国际化支持
6. `backend/app/utils/metrics.py` - Prometheus指标

#### API路由层
7. `backend/app/api/v1/admin.py` - 管理员API
8. `backend/app/api/v1/upload.py` - 文件上传API
9. `backend/app/api/v1/tasks.py` - 任务状态API
10. `backend/app/api/v1/stats.py` - 统计分析API
11. `backend/app/api/v1/monitoring.py` - 监控API
12. `backend/app/api/v1/websocket.py` - WebSocket端点

#### 其他
13. `backend/app/services/websocket_auth.py` - WebSocket认证依赖

---

## 新功能使用指南

### 1. 文件上传批量分析

#### 上传文件
```bash
curl -X POST http://localhost:8000/api/v1/upload/file \
  -H "Authorization: Bearer {token}" \
  -F "file=@data.csv"
```

#### 批量分析
```bash
curl -X POST http://localhost:8000/api/v1/upload/batch-analyze \
  -H "Authorization: Bearer {token}" \
  -F "file=@data.csv" \
  -F "text_column=review" \
  -F "model_key=bert"
```

#### 异步分析
```bash
curl -X POST http://localhost:8000/api/v1/upload/async-analyze \
  -H "Authorization: Bearer {token}" \
  -F "file=@large_data.csv"
```

**返回示例**:
```json
{
  "task_id": "abc-123-def",
  "status": "queued",
  "message": "Task queued successfully"
}
```

---

### 2. 任务状态查询

#### 查询任务
```bash
curl http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer {token}"
```

**返回示例**:
```json
{
  "task_id": "abc-123",
  "status": "SUCCESS",
  "result": {
    "total": 100,
    "success": 95,
    "failed": 5,
    "results": [...]
  }
}
```

#### 取消任务
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/{task_id}/cancel?terminate=true" \
  -H "Authorization: Bearer {token}"
```

---

### 3. WebSocket实时推送

#### 连接WebSocket
```javascript
const ws = new WebSocket(
  "ws://localhost:8000/api/v1/ws/{task_id}?token={access_token}"
);

ws.onopen = () => {
  console.log("Connected");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Progress:", data);

  // 示例响应
  if (data.type === "progress") {
    console.log(`Progress: ${data.progress_percent}%`);
    console.log(`Status: ${data.status}`);
  }
};
```

**消息类型**:
- `connected` - 连接成功
- `progress` - 任务进度
- `notification` - 通知消息
- `pong` - 心跳响应
- `error` - 错误消息

---

### 4. 统计分析接口

#### 概览统计
```bash
curl http://localhost:8000/api/v1/stats/overview \
  -H "Authorization: Bearer {token}"
```

**返回示例**:
```json
{
  "total_predictions": 1520,
  "recent_7d": 85,
  "recent_30d": 320,
  "label_distribution": {
    "positive": 850,
    "negative": 420,
    "neutral": 250
  },
  "average_score": 0.6823
}
```

#### 每日统计
```bash
curl "http://localhost:8000/api/v1/stats/daily?days=7" \
  -H "Authorization: Bearer {token}"
```

#### 趋势分析
```bash
curl "http://localhost:8000/api/v1/stats/trends?period=daily&limit=30" \
  -H "Authorization: Bearer {token}"
```

**period选项**: `daily`, `weekly`, `monthly`

#### 标签分布
```bash
curl http://localhost:8000/api/v1/stats/label-distribution \
  -H "Authorization: Bearer {token}"
```

---

### 5. 管理员接口

**要求**: `role=admin`

#### 用户管理

##### 获取用户列表
```bash
curl "http://localhost:8000/api/v1/admin/users?skip=0&limit=20" \
  -H "Authorization: Bearer {admin_token}"
```

##### 更新用户
```bash
curl -X PUT http://localhost:8000/api/v1/admin/users/{user_id} \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_active": true}'
```

##### 删除用户
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/users/{user_id} \
  -H "Authorization: Bearer {admin_token}"
```

#### API Key管理

##### 创建API Key
```bash
curl -X POST http://localhost:8000/api/v1/admin/users/{user_id}/api-keys \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key",
    "permissions": "predict,history",
    "rate_limit": 100,
    "expires_in_days": 30
  }'
```

**响应** (包含明文key, 只显示一次):
```json
{
  "id": 1,
  "key": "abc123xyz...",
  "key_prefix": "abc123",
  "warning": "Save this key securely, it won't be shown again"
}
```

##### 撤销API Key
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/api-keys/{key_id} \
  -H "Authorization: Bearer {admin_token}"
```

#### 系统统计
```bash
curl http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer {admin_token}"
```

---

### 6. 监控接口

#### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

#### 系统状态
```bash
curl http://localhost:8000/api/v1/status
```

**返回示例**:
```json
{
  "system": {
    "cpu_percent": 25.5,
    "memory": {
      "total": 17179869184,
      "available": 8589934592,
      "percent": 50.0
    },
    "disk": {
      "total": 53687091200,
      "free": 26843545600,
      "percent": 50.0
    }
  },
  "database": {
    "status": "connected",
    "prediction_count": 1520
  },
  "config": {
    "default_model": "bert",
    "redis_host": "localhost",
    "rate_limit_enabled": true
  }
}
```

#### Prometheus指标
```bash
curl http://localhost:8000/api/v1/metrics
```

---

### 7. 文本分析

#### 使用文本分析服务

```python
from app.services.text_analysis import text_analysis_service

# 提取关键词
keywords = text_analysis_service.extract_keywords(
    "这部电影非常精彩，剧情紧凑，演员表现出色！",
    max_keywords=5
)
# 返回: [{"keyword": "电影", "weight": 3, "frequency": 0.15}, ...]

# 生成摘要
summary = text_analysis_service.summarize_text(long_text, max_length=200)

# 文本统计
stats = text_analysis_service.get_text_stats(text)
# 返回: {"char_count": 100, "word_count": 50, "sentence_count": 5, ...}

# 详细情感分析
detailed = text_analysis_service.analyze_sentiment_detail(text, sentiment_result)
# 返回: {"label": "positive", "score": 0.95, "intensity": "强", "keywords": [...], "summary": "..."}
```

---

## 配置文件更新

### requirements.txt新增依赖

已添加:
- `prometheus-client==0.19.0`
- `sentry-sdk==1.39.1`
- `celery==5.3.4`
- `celery[redis]==5.3.4`
- `python-socketio==5.10.0`

### 新增环境变量

```bash
# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 文件上传配置
UPLOAD_DIR=/tmp/uploads

# Sentry (可选)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

---

## API路由总览

### 新增端点汇总

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v1/upload/file` | 上传文件 | ✅ |
| POST | `/api/v1/upload/batch-analyze` | 批量分析 | ✅ |
| POST | `/api/v1/upload/async-analyze` | 异步分析 | ✅ |
| GET | `/api/v1/tasks/{task_id}` | 查询任务 | ✅ |
| POST | `/api/v1/tasks/{task_id}/cancel` | 取消任务 | ✅ |
| GET | `/api/v1/tasks/` | 活跃任务 | ✅ |
| WS | `/api/v1/ws/{task_id}` | WebSocket | ✅ |
| GET | `/api/v1/stats/overview` | 概览统计 | ✅ |
| GET | `/api/v1/stats/daily` | 每日统计 | ✅ |
| GET | `/api/v1/stats/trends` | 趋势分析 | ✅ |
| GET | `/api/v1/stats/label-distribution` | 标签分布 | ✅ |
| GET | `/api/v1/stats/score-distribution` | 分数分布 | ✅ |
| GET | `/api/v1/stats/model-usage` | 模型使用 | ✅ |
| GET | `/api/v1/admin/users` | 用户列表 | 👑 |
| GET | `/api/v1/admin/users/{id}` | 用户详情 | 👑 |
| PUT | `/api/v1/admin/users/{id}` | 更新用户 | 👑 |
| DELETE | `/api/v1/admin/users/{id}` | 删除用户 | 👑 |
| POST | `/api/v1/admin/users/{id}/api-keys` | 创建API Key | 👑 |
| GET | `/api/v1/admin/users/{id}/api-keys` | API Key列表 | 👑 |
| DELETE | `/api/v1/admin/api-keys/{id}` | 撤销Key | 👑 |
| GET | `/api/v1/admin/stats` | 系统统计 | 👑 |
| GET | `/api/v1/admin/predictions/all` | 所有预测 | 👑 |
| DELETE | `/api/v1/admin/predictions/{id}` | 删除预测 | 👑 |
| GET | `/api/v1/health` | 健康检查 | ❌ |
| GET | `/api/v1/health/ready` | 就绪检查 | ❌ |
| GET | `/api/v1/health/live` | 存活检查 | ❌ |
| GET | `/api/v1/status` | 系统状态 | ❌ |
| GET | `/api/v1/metrics` | Prometheus指标 | ❌ |

**图例**: ✅ 需要认证 | 👑 需要管理员权限 | ❌ 公开

---

## 数据库Schema变更

### 新增模型

#### User模型 (已存在)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

#### APIKey模型 (新增)
```sql
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(10) NOT NULL,
    permissions VARCHAR(500) DEFAULT 'predict,history',
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

#### PredictionHistory模型 (已存在)
```sql
CREATE TABLE prediction_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    input_text TEXT NOT NULL,
    label VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    model_key VARCHAR(50) DEFAULT 'bert',
    source_ip VARCHAR(45),
    user_agent VARCHAR(512),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 测试命令

### 1. 测试文件上传
```bash
# 创建测试文件
echo "这部电影太精彩了！" > test.txt
echo "review,sentiment" > test.csv
echo " terrible service,negative" >> test.csv
echo "great food,positive" >> test.csv

# 上传文件
curl -X POST http://localhost:8000/api/v1/upload/file \
  -H "Authorization: Bearer {token}" \
  -F "file=@test.csv"
```

### 2. 测试统计分析
```bash
# 概览
curl http://localhost:8000/api/v1/stats/overview \
  -H "Authorization: Bearer {token}"

# 趋势
curl "http://localhost:8000/api/v1/stats/trends?period=daily" \
  -H "Authorization: Bearer {token}"
```

### 3. 测试管理员接口
```bash
# 用户列表
curl "http://localhost:8000/api/v1/admin/users?skip=0&limit=10" \
  -H "Authorization: Bearer {admin_token}"

# 系统统计
curl http://localhost:8000/api/v1/admin/stats \
  -H "Authorization: Bearer {admin_token}"
```

### 4. 测试监控
```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 系统状态
curl http://localhost:8000/api/v1/status
```

---

## 常见问题

### Q1: Celery Worker未启动怎么办?
**A**: 确保Redis运行中，然后启动Worker:
```bash
celery -A app.services.celery_tasks.celery_app worker --loglevel=info
```

### Q2: WebSocket连接失败?
**A**: 检查:
1. Token是否有效
2. 网络是否正常
3. 防火墙是否允许WebSocket

### Q3: 文件上传失败?
**A**: 检查:
1. 文件大小是否超过50MB
2. 文件格式是否支持 (csv/xlsx/txt/json)
3. 是否有写入权限到 `/tmp/uploads`

### Q4: 统计接口返回空?
**A**: 确保有预测记录，且未软删除

---

## 下一步

1. **启动Celery Worker**: `celery -A app.services.celery_tasks.celery_app worker --loglevel=info`
2. **安装可选依赖**: `pip install prometheus-client sentry-sdk celery`
3. **运行数据库迁移**: `alembic upgrade head`
4. **测试WebSocket**: 使用前端页面或WebSocket客户端测试
5. **配置监控**: 集成Grafana展示Prometheus指标

---

**文档版本**: v1.0
**最后更新**: 2024-2025
