# Vue 3 + TypeScript + Vite + Element Plus

基于 Vue 3 + TypeScript + Vite + Element Plus 的现代前端项目，是 NLP 预测平台的官方前端实现。

## 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **语言**: TypeScript 5.0+
- **构建工具**: Vite 5.0+
- **UI 组件库**: Element Plus 2.4+
- **路由**: Vue Router 4.0+
- **状态管理**: Pinia 2.0+
- **HTTP 客户端**: Axios
- **图表库**: ECharts
- **CSS 方案**: SCSS

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 环境配置

复制 `.env.example` 到 `.env.development` 和 `.env.production`，并根据实际情况修改 API 地址：

```env
# .env.development (开发环境)
VITE_API_BASE_URL=http://localhost:8000

# .env.production (生产环境)
VITE_API_BASE_URL=http://your-server:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 4. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 项目结构

```
frontend-vue/
├── src/
│   ├── api/                  # API 封装
│   ├── views/                # 页面组件
│   ├── components/           # 公共组件
│   ├── stores/               # Pinia 状态管理
│   ├── utils/                # 工具函数
│   ├── types/                # TypeScript 类型
│   ├── router/               # 路由配置
│   ├── styles/               # 样式文件
│   ├── App.vue               # 根组件
│   └── main.ts               # 入口文件
├── public/                    # 静态资源
├── .env.development          # 开发环境变量
├── .env.production           # 生产环境变量
├── vite.config.ts            # Vite 配置
├── nginx.conf                # Nginx 配置
├── Dockerfile                # Docker 构建文件
└── package.json              # 依赖管理
```

## 功能清单

### ✅ 已完成

- [x] 项目初始化
- [x] Element Plus 集成
- [x] 路由配置
- [x] 状态管理 (Pinia)
- [x] API 封装 (Axios)
- [x] 文本预测页面
- [x] 批量处理页面
- [x] 历史记录页面
- [x] 统计概览页面
- [x] 布局组件
- [x] 工具函数
- [x] TypeScript 类型定义
- [x] SCSS 样式
- [x] Docker 配置
- [x] Nginx 配置
- [x] Loading 组件
- [x] ErrorMessage 组件
- [x] StatCard 组件
- [x] ResultCard 组件
- [x] 用户认证
- [x] 模型管理页面
- [x] 国际化 (i18n)
- [x] 暗色主题
- [x] PWA 支持

## 部署指南

### Nginx 部署

```bash
npm run build
cp -r dist/* /var/www/nlp-frontend/
```

### Docker 部署

```bash
# 开发环境
docker build -t nlp-frontend:dev -f Dockerfile.dev .
docker run -p 3000:3000 nlp-frontend:dev

# 生产环境
docker build -t nlp-frontend:prod -f Dockerfile.prod .
docker run -p 80:80 nlp-frontend:prod
```

## 开发规范

### 命名规范

- **组件**: PascalCase (如 `PredictView.vue`)
- **文件**: kebab-case (如 `format.ts`)
- **变量/函数**: camelCase (如 `predictText`)
- **常量**: UPPER_SNAKE_CASE (如 `API_BASE_URL`)

### TypeScript 规范

- ✅ 所有函数必须有返回类型
- ✅ 所有变量尽量有类型标注
- ✅ 使用 `interface` 定义对象类型
- ✅ 使用 `type` 定义联合类型

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | API 基础 URL | `http://localhost:8000` |
| `VITE_API_TIMEOUT` | 请求超时时间（毫秒） | `10000` |

## 常见问题

### 跨域问题

开发环境已在 `vite.config.ts` 中配置代理。如遇到跨域，检查后端是否允许跨域。

### API 请求失败

检查 `.env` 文件中的 `VITE_API_BASE_URL` 是否正确配置。

### TypeScript 报错

运行 `npm run build` 或 `npx vue-tsc --noEmit` 查看详细错误。

## 许可证

MIT License

---

**版本**: 1.0.0
**更新时间**: 2026-06-28
**状态**: ✅ 开发就绪
