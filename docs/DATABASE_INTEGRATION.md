# 数据库集成 & 历史记录查询功能说明

> **版本**: v1.0  
> **最后更新**: 2026-06-19  
> **适用范围**: NLP 情感预测平台

---

## 1. 功能概述

本功能为 NLP 预测平台新增了 **PostgreSQL 持久化存储** 与 **预测历史记录查询** 能力。每次文本预测请求的结果（输入文本、预测标签、置信度分数、来源 IP 等）会自动写入数据库，并可通过 API 或前端界面进行多条件分页查询与统计分析。

### 关键特性

| 特性 | 描述 |
|------|------|
| 自动持久化 | 每次 `/predict` 调用自动保存记录，无需额外操作 |
| 多条件查询 | 支持按标签、置信度范围、关键词、时间范围等过滤 |
| 分页查询 | 支持自定义页码和每页条数（1~100） |
| 最近记录 | 快速获取最近 N 条记录 |
| 统计概览 | 总预测次数、标签分布、平均置信度 |
| 前端可视化 | Streamlit 三页面导航（预测 / 历史 / 统计） |

---

## 2. 架构设计

```
┌──────────────────────────────────────────────────────┐
│                    Streamlit 前端                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 文本预测  │  │ 历史记录查询  │  │  统计概览      │  │
│  └────┬─────┘  └──────┬───────┘  └───────┬───────┘  │
└───────┼───────────────┼──────────────────┼──────────┘
        │               │                  │
        ▼               ▼                  ▼
┌──────────────────────────────────────────────────────┐
│                  FastAPI 后端                          │
│                                                       │
│  POST /api/v1/predict          → 预测 + 写入DB       │
│  GET  /api/v1/history          → 分页查询历史          │
│  GET  /api/v1/history/recent   → 最近记录             │
│  GET  /api/v1/history/stats    → 统计概览             │
│                                                       │
│  ┌─────────────┐  ┌──────────────────────┐           │
│  │  Redis 缓存  │  │  SQLAlchemy 异步 ORM  │           │
│  └─────────────┘  └──────────┬───────────┘           │
└──────────────────────────────┼────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   PostgreSQL 16   │
                    │   (预测历史记录)   │
                    └──────────────────┘
```

### 技术栈

| 组件 | 技术选型 |
|------|----------|
| 数据库 | PostgreSQL 16 (Alpine) |
| ORM | SQLAlchemy 2.0 (异步模式) |
| 异步驱动 | asyncpg |
| 表迁移 | 启动时 `Base.metadata.create_all` 自动建表 |
| 缓存 | Redis 7 (已存在，本次未变更) |

---

## 3. 数据库表结构

### 3.1 `prediction_history` 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, 自增 | 主键 |
| `input_text` | `TEXT` | NOT NULL | 用户输入的原始文本 |
| `label` | `VARCHAR(50)` | NOT NULL | 预测标签（正面/负面） |
| `score` | `FLOAT` | NOT NULL | 置信度分数 (0~1) |
| `source_ip` | `VARCHAR(45)` | NULL | 请求来源 IP |
| `user_agent` | `VARCHAR(512)` | NULL | 客户端 UA |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | 记录创建时间 |

### 3.2 索引

| 索引名 | 字段 | 说明 |
|--------|------|------|
| `ix_prediction_history_created_at` | `created_at DESC` | 加速按时间倒序查询 |
| `ix_prediction_history_label` | `label` | 加速按标签过滤 |
| `ix_prediction_history_score` | `score` | 加速按置信度范围过滤 |

---

## 4. 新增/修改的文件

### 后端新增文件

| 文件路径 | 说明 |
|----------|------|
| `backend/app/db/__init__.py` | 数据库模块入口 |
| `backend/app/db/base.py` | SQLAlchemy 声明式基类 |
| `backend/app/db/session.py` | 异步数据库引擎与会话管理 |
| `backend/app/db/models.py` | ORM 模型定义（`PredictionHistory`） |
| `backend/app/services/history.py` | 历史记录 CRUD 服务层 |
| `backend/app/api/v1/history.py` | 历史查询 API 路由 |

### 后端修改文件

| 文件路径 | 变更内容 |
|----------|----------|
| `backend/app/main.py` | 注册 history 路由；启动时自动建表 |
| `backend/app/api/v1/predict.py` | 预测后自动保存记录到数据库 |
| `backend/app/core/config.py` | 新增 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME 和 DATABASE_URL 属性 |
| `backend/requirements.txt` | 新增 `sqlalchemy[asyncio]`, `asyncpg`, `psycopg2-binary` |

### 基础设施修改

| 文件路径 | 变更内容 |
|----------|----------|
| `docker-compose.yml` | 新增 `postgres` 服务；backend 新增 `depends_on postgres` 和数据库环境变量；新增 `postgres_data` 卷 |
| `.env` | 新增 `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |

### 前端修改

| 文件路径 | 变更内容 |
|----------|----------|
| `frontend/app.py` | 重构为三页面导航：文本预测 / 历史记录查询 / 统计概览 |

---

## 5. API 接口说明

### 5.1 预测（已增强）

**POST** `/api/v1/predict`

请求体：
```json
{
  "text": "今天天气真好，心情不错！"
}
```

响应体（不变）：
```json
{
  "label": "正面",
  "score": 0.9234
}
```

> 💡 该接口在返回结果的同时，自动将记录写入 `prediction_history` 表。

---

### 5.2 历史记录查询

**GET** `/api/v1/history`

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | `int` | 否 | 1 | 页码 (≥1) |
| `page_size` | `int` | 否 | 20 | 每页条数 (1~100) |
| `label` | `str` | 否 | - | 按标签过滤 |
| `min_score` | `float` | 否 | - | 最低置信度 (0~1) |
| `max_score` | `float` | 否 | - | 最高置信度 (0~1) |
| `keyword` | `str` | 否 | - | 文本关键词模糊搜索 |
| `start_date` | `datetime` | 否 | - | 开始时间 (ISO 8601) |
| `end_date` | `datetime` | 否 | - | 结束时间 (ISO 8601) |

响应示例：
```json
{
  "total": 156,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "records": [
    {
      "id": 156,
      "input_text": "今天天气真好，心情不错！",
      "label": "正面",
      "score": 0.9234,
      "source_ip": "172.18.0.1",
      "created_at": "2026-06-19T01:30:00+00:00"
    }
  ]
}
```

---

### 5.3 最近记录

**GET** `/api/v1/history/recent?limit=10`

返回最近 N 条记录（按时间倒序）。

---

### 5.4 统计概览

**GET** `/api/v1/history/stats`

响应示例：
```json
{
  "total_predictions": 156,
  "label_distribution": {
    "正面": 98,
    "负面": 58
  },
  "average_score": 0.8123
}
```

---

## 6. 前端界面

前端重构为 **三页面侧边栏导航**：

| 页面 | 功能 |
|------|------|
| 📝 文本预测 | 输入文本 → 点击预测 → 显示标签+置信度+进度条 |
| 📊 历史记录 | 多条件过滤（页码/每页条数/标签/关键词/置信度范围/时间范围）→ 分页表格展示 + 最近10条快速查看 |
| 📈 统计概览 | 总预测次数 / 平均置信度 / 正面负面比 / 标签分布柱状图 |

历史记录表格中的预测标签会自动着色：
- 🟢 **正面** → 绿色背景
- 🔴 **负面** → 红色背景

---

## 7. 环境变量

新增和修改的环境变量：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `POSTGRES_USER` | `nlp_user` | PostgreSQL 用户名 |
| `POSTGRES_PASSWORD` | `nlp_pass` | PostgreSQL 密码 |
| `POSTGRES_DB` | `nlp_db` | PostgreSQL 数据库名 |
| `DB_HOST` | `localhost` (容器内为 `postgres`) | 数据库主机 |
| `DB_PORT` | `5432` | 数据库端口 |
| `DB_USER` | `nlp_user` | 应用连接数据库用户名 |
| `DB_PASSWORD` | `nlp_pass` | 应用连接数据库密码 |
| `DB_NAME` | `nlp_db` | 应用连接数据库名 |

---

## 8. 部署与启动

### 8.1 Docker Compose 启动（推荐）

```bash
# 克隆项目后
cd nlp_project

# 启动所有服务（backend + frontend + redis + postgres）
docker compose up -d --build

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f backend
```

### 8.2 本地开发

```bash
# 1. 确保 PostgreSQL 和 Redis 已运行
# 2. 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=nlp_user
export DB_PASSWORD=nlp_pass
export DB_NAME=nlp_db

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. 启动前端（另一个终端）
cd frontend
streamlit run app.py
```

### 8.3 验证数据库

```bash
# 进入 PostgreSQL 容器
docker exec -it nlp_postgres psql -U nlp_user -d nlp_db

# 查看表结构
\d prediction_history

# 查询记录数
SELECT COUNT(*) FROM prediction_history;

# 查看最近的预测
SELECT input_text, label, score, created_at
FROM prediction_history
ORDER BY created_at DESC
LIMIT 10;
```

---

## 9. 数据库自动建表机制

应用在 FastAPI `startup` 事件中会调用 `Base.metadata.create_all` 自动创建缺失的表。这意味着：

- ✅ 首次启动无需手动执行 SQL
- ✅ 新增模型后重启即可自动建表
- ⚠️ 不会修改已有表结构（如需变更请使用 Alembic 等迁移工具）
- ⚠️ 生产环境建议使用 Alembic 进行版本化迁移

---

## 10. 后续扩展建议

| 方向 | 说明 |
|------|------|
| 数据导出 | 新增 CSV/JSON 导出接口 |
| 批量删除 | 支持按条件批量清理历史记录 |
| 高级统计 | 时间趋势图、置信度分布直方图 |
| Alembic 迁移 | 替代 `create_all` 实现版本化数据库迁移 |
| 数据保留策略 | 定期自动清理 N 天前的记录 |
| 用户系统 | 关联用户 ID，实现个人历史查询 |

---

## 11. 常见问题

**Q: 数据库连接失败怎么办？**  
A: 确认 `docker-compose.yml` 中 `postgres` 服务已健康运行（`docker compose ps` 检查）。检查 `.env` 中的数据库密码是否匹配。

**Q: 表没有自动创建？**  
A: 查看 backend 日志 `docker compose logs backend`，确认启动日志中是否有 `Database tables created/verified.`。如果报权限错误，请检查数据库用户是否有建表权限。

**Q: 历史记录查询很慢？**  
A: 系统已为 `created_at`、`label`、`score` 建立了索引。如数据量超过百万，建议考虑分区表或数据归档。

**Q: 如何清空历史数据？**  
A: 进入 PostgreSQL 容器执行 `TRUNCATE TABLE prediction_history;`