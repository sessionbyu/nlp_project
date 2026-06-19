# 多模型动态切换 & 模型热加载

## 概述

本项目新增了两个核心功能：

1. **多模型动态切换**：前端可通过参数选择不同模型（VADER、BERT）进行情感分析，无需修改代码
2. **模型热加载**：更新模型文件后无需重启服务，支持手动 API 触发和自动文件监控两种方式

---

## 架构设计

```
┌─────────────────────────────────────────────────┐
│                   Frontend (Streamlit)           │
│   ┌─────────────┐                               │
│   │ 模型选择器   │  GET /api/v1/models           │
│   │ (vader/bert)│  POST /api/v1/predict          │
│   └─────────────┘  { model_key: "vader" }        │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│                Backend (FastAPI)                  │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │          SentimentService (单例)             │ │
│  │                                              │ │
│  │  _models = {                                 │ │
│  │    "bert":  BertModel(),                     │ │
│  │    "vader": VaderModel(),                    │ │
│  │  }                                           │ │
│  │                                              │ │
│  │  + get_model(key) → model                   │ │
│  │  + reload_models()   # 热加载               │ │
│  │  + available_models  # 可用列表             │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  API 端点:                                        │
│  • POST /api/v1/predict   (model_key 参数)       │
│  • GET  /api/v1/models    (查询可用模型)         │
│  • POST /admin/reload-model (手动热加载)         │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │    ModelWatcher (watchdog)                   │ │
│  │    监控 /data/models/ 目录                   │ │
│  │    检测 .bin/.json 文件变更 → 自动热加载     │ │
│  └─────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

---

## 功能一：多模型动态切换

### 1.1 配置（`config.py`）

```python
# 可用模型列表（环境变量 AVAILABLE_MODELS，逗号分隔）
AVAILABLE_MODELS: list = os.getenv("AVAILABLE_MODELS", "vader,bert").split(",")

# 默认模型（请求未指定 model_key 时使用）
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "bert")
```

通过环境变量控制启用哪些模型：

```bash
# 只启用 BERT
export AVAILABLE_MODELS="bert"

# 启用全部模型
export AVAILABLE_MODELS="vader,bert"

# 设置默认模型为 VADER
export DEFAULT_MODEL="vader"
```

### 1.2 模型注册（`inference.py`）

`SentimentService` 单例在启动时加载所有配置的模型：

```python
class SentimentService:
    def __init__(self):
        self._models: Dict[str, Any] = {}
        self._load_all_models()

    def _load_all_models(self):
        for model_key in settings.AVAILABLE_MODELS:
            if model_key == "bert":
                self._models["bert"] = BertModel()
            elif model_key == "vader":
                self._models["vader"] = VaderModel()
```

### 1.3 预测接口（`predict.py`）

请求体新增可选字段 `model_key`，响应中返回实际使用的模型：

**请求：**
```json
POST /api/v1/predict
{
    "text": "这个产品非常好用",
    "model_key": "vader"
}
```

**响应：**
```json
{
    "label": "positive",
    "score": 0.8472,
    "model_key": "vader"
}
```

若未指定 `model_key`，则使用 `DEFAULT_MODEL`（默认为 `bert`）。

### 1.4 模型列表查询

```json
GET /api/v1/models

{
    "available_models": ["vader", "bert"],
    "default_model": "bert"
}
```

前端通过此接口动态获取可用模型列表并渲染模型选择器。

### 1.5 VADER 模型（`vader_model.py`）

基于 NLTK 的 VADER（Valence Aware Dictionary and sEntiment Reasoner）情感分析器：

- **特点**：轻量、快速、无需 GPU，适合英文文本
- **输出**：与 BERT 统一的 `{"label": "positive/negative/neutral", "score": 0.0~1.0}` 格式
- **标签映射**：compound ≥ 0.05 → positive，≤ -0.05 → negative，其余 → neutral
- **分数归一化**：`(compound + 1) / 2` 映射到 [0, 1] 区间

### 1.6 模型对比

| 特性 | BERT | VADER |
|------|------|-------|
| 准确度 | 高（中文优化） | 中等（英文优化） |
| 速度 | 慢（需 GPU/CPU 推理） | 极快（基于词典） |
| 内存占用 | 大（~400MB+） | 小（~10MB） |
| 适用场景 | 中文文本、高精度需求 | 英文文本、快速原型 |
| 依赖 | transformers + torch | nltk |

### 1.7 缓存隔离

不同模型的预测结果使用独立的缓存键，避免模型切换后返回错误缓存：

```python
def get_cache_key(text: str, model_key: str = "") -> str:
    raw = f"{model_key}:{text}"
    return f"nlp:cache:{hashlib.md5(raw.encode()).hexdigest()}"
```

---

## 功能二：模型热加载

### 2.1 方式一：管理接口（手动触发）

```bash
curl -X POST http://localhost:8000/admin/reload-model
```

**响应：**
```json
{
    "status": "ok",
    "message": "All models reloaded successfully",
    "available_models": ["vader", "bert"]
}
```

`SentimentService.reload_models()` 方法：
1. 清空现有模型字典
2. 重新读取 `AVAILABLE_MODELS` 配置
3. 重新实例化所有模型类

### 2.2 方式二：文件监控（自动触发）

服务启动时，watchdog 自动监控模型目录（`MODEL_PATH` 的父目录，默认为 `/data/models/`）：

```
启动日志：
[INFO] Starting model file watcher on: /data/models
[INFO] Model file watcher started

检测到文件变更时：
[INFO] Model file changed: /data/models/bert-base-chinese/pytorch_model.bin
[INFO] Reloading all models...
[INFO] Unloaded model: bert
[INFO] BERT model loaded into registry
[INFO] VADER model loaded into registry
[INFO] Model reload complete
```

**监控的文件类型：** `.bin`, `.safetensors`, `.json`, `.model`, `.pth`

**防抖机制：** 5 秒内的多次变更只触发一次重载，等待文件完全写入后再执行。

**关闭安全：** 服务关闭时自动停止文件监控线程。

### 2.3 完整工作流

```
1. 开发者替换模型文件（如 pytorch_model.bin）
       ↓
2. watchdog 检测到文件变更
       ↓
3. 5 秒防抖等待
       ↓
4. sentiment_service.reload_models()
       ↓
5. 新模型实例替换旧实例
       ↓
6. 后续请求自动使用新模型
```

或手动触发：
```
curl -X POST /admin/reload-model → 立即执行步骤 4-6
```

---

## 前端集成

前端 Streamlit 应用新增模型选择器：

```python
# 动态获取可用模型
models_info = call_api(f"{BACKEND_BASE_URL}/api/v1/models")
available_models = models_info.get("available_models", ["bert"])

# 模型选择下拉框
model_key = st.selectbox(
    "🤖 选择模型",
    options=available_models,
    index=default_index,
    help="选择用于情感分析的模型（VADER 速度快，BERT 准确度高）",
)

# 预测时传递 model_key
result = call_api(
    PREDICT_URL,
    method="POST",
    json_data={"text": text.strip(), "model_key": model_key},
)
```

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/app/core/config.py` | 修改 | 新增 `AVAILABLE_MODELS`、`DEFAULT_MODEL` 配置 |
| `backend/app/models/vader_model.py` | **新增** | VADER 情感分析模型封装 |
| `backend/app/services/inference.py` | 重写 | `SentimentService` 单例 + `model_key` 参数 |
| `backend/app/api/v1/predict.py` | 修改 | 请求体增加 `model_key`，响应增加 `model_key`，新增 `GET /api/v1/models` |
| `backend/app/main.py` | 修改 | `POST /admin/reload-model` + startup/shutdown 文件监控 |
| `backend/app/utils/model_watcher.py` | **新增** | watchdog 文件监控 + 防抖 |
| `backend/requirements.txt` | 修改 | 新增 `nltk>=3.8`、`watchdog>=4.0` |
| `frontend/app.py` | 修改 | 模型选择器 + `model_key` 传递 |

---

## 扩展指南

### 添加新模型

1. 创建模型封装类（参考 `vader_model.py`），实现 `predict(text) → Dict` 接口
2. 在 `SentimentService._load_all_models()` 中注册新模型 key
3. 将模型 key 加入 `AVAILABLE_MODELS` 配置

示例：添加自定义模型

```python
# backend/app/models/custom_model.py
class CustomModel:
    def __init__(self):
        # 加载自定义模型
        pass

    def predict(self, text: str) -> Dict[str, Any]:
        # 返回 {"label": "...", "score": 0.0~1.0}
        pass

# config.py 中启用
export AVAILABLE_MODELS="vader,bert,custom"

# inference.py 中注册
if model_key == "custom":
    from app.models.custom_model import CustomModel
    self._models["custom"] = CustomModel()
```

### 环境变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AVAILABLE_MODELS` | `vader,bert` | 启用的模型列表，逗号分隔 |
| `DEFAULT_MODEL` | `bert` | 默认推理模型 |
| `MODEL_PATH` | `/data/models/bert-base-chinese` | BERT 模型文件路径 |
| `USE_CACHE` | `true` | 是否启用 Redis 缓存 |