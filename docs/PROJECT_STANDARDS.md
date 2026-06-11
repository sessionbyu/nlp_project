# 项目规范文档

## 1. 目录结构规范
- `backend/`：FastAPI 后端服务
  - `app/api/`：路由层（API 端点）
  - `app/core/`：配置、异常处理、依赖注入
  - `app/models/`：Pydantic 数据模型
  - `app/services/`：业务逻辑 + NLP 模型推理
  - `app/utils/`：辅助函数
- `frontend/`：Streamlit 前端应用
- `docs/`：所有文档（包括本规范、Git 说明、Docker 指南等）
- `scripts/`：辅助脚本（测试、数据准备等）

## 2. 代码规范（强制执行）
- **格式化**：统一使用 `black`，行宽 88
- **排序**：使用 `isort` 自动管理 import 顺序
- **检查**：使用 `ruff` 替代 flake8 + pylint
- **类型注解**：所有函数参数和返回值必须有类型注解

## 3. 环境变量规范
- 禁止硬编码配置（端口、密钥、模型路径等）
- 使用 `pydantic-settings` 管理配置
- 本地开发使用 `.env` 文件（不提交到 Git）
- 生产环境使用环境变量注入

## 4. API 设计规范
- 路径前缀：`/api/v1/`
- 响应格式统一：
  ```json
  {
    "code": 200,
    "data": {},
 # 项目规范文档

## 1. 目录结构规范
- `backend/`：FastAPI 后端服务
  - `app/api/`：路由层（API 端点）
  - `app/core/`：配置、异常处理、依赖注入
  - `app/models/`：Pydantic 数据模型
  - `app/services/`：业务逻辑 + NLP 模型推理
  - `app/utils/`：辅助函数
- `frontend/`：Streamlit 前端应用
- `docs/`：所有文档（包括本规范、Git 说明、Docker 指南等）
- `scripts/`：辅助脚本（测试、数据准备等）

## 2. 代码规范（强制执行）
- **格式化**：统一使用 `black`，行宽 88
- **排序**：使用 `isort` 自动管理 import 顺序
- **检查**：使用 `ruff` 替代 flake8 + pylint
- **类型注解**：所有函数参数和返回值必须有类型注解

## 3. 环境变量规范
- 禁止硬编码配置（端口、密钥、模型路径等）
- 使用 `pydantic-settings` 管理配置
- 本地开发使用 `.env` 文件（不提交到 Git）
- 生产环境使用环境变量注入

## 4. API 设计规范
- 路径前缀：`/api/v1/`
- 响应格式统一：
  ```json
  {
    "code": 200,
    "data": {},
    "msg": "success"
  }
  - HTTP 方法：GET（查询）、POST（创建/推理）、PUT（全量更新）、DELETE（删除）

## 5. 命名规范
- Python 文件：小写下划线（`text_classifier.py`）
- 类名：大驼峰（`TextClassifierService`）
- 函数/变量：小写下划线（`predict_sentiment`）
- 常量：全大写下划线（`MAX_SEQUENCE_LEN`）

## 6. Git 提交规范
- 必须使用语义化提交类型：`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- 示例：`feat: 添加文本分类API`、`fix: 修复模型加载时的内存泄漏`
