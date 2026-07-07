# 🎨 护眼配色快速参考指南

## 📋 目录
1. [颜色速查表](#颜色速查表)
2. [使用场景](#使用场景)
3. [代码示例](#代码示例)
4. [配色原则](#配色原则)

---

## 颜色速查表

### 🎨 主色调

```scss
// 主色 - 护眼青绿色
$primary-gradient: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
$primary-light: #6DB3A8;
$primary-color: #5B9A8B;

// 辅助色 - 温暖珊瑚色
$secondary-gradient: linear-gradient(135deg, #E8A87C 0%, #D4906A 100%);
$secondary-light: #E8B89A;
```

### 🎯 状态色

```scss
// 成功色 - 柔和绿色
$success-gradient: linear-gradient(135deg, #68C3A0 0%, #5AB38D 100%);
$success-color: #68C3A0;

// 警告色 - 温暖琥珀色
$warning-gradient: linear-gradient(135deg, #E8B87C 0%, #D4A56A 100%);
$warning-color: #E8B87C;

// 错误色 - 珊瑚红
$danger-gradient: linear-gradient(135deg, #E87C7C 0%, #D46A6A 100%);
$danger-color: #E87C7C;

// 信息色 - 蓝灰色
$info-gradient: linear-gradient(135deg, #7BA3C4 0%, #6B93B4 100%);
$info-color: #7BA3C4;
```

### 🖼️ 背景色

```scss
// 浅色背景
$bg-primary: #F8F9FA;      // 主背景（温暖米白）
$bg-secondary: #FFFFFF;    // 卡片背景（纯白）
$bg-tertiary: #F0F2F5;     // 次背景
$bg-hover: #E8ECF0;        // 悬停背景
$bg-active: #DDE1E6;       // 激活背景

// 深色背景（深绿灰，非纯黑）
$bg-dark-primary: #3A4A46;
$bg-dark-secondary: #4A5A56;
$bg-dark-tertiary: #4A5D59;
```

### 📝 文字色

```scss
// 文字颜色
$text-primary: #2C3E50;    // 主标题
$text-secondary: #5A6878;  // 正文
$text-tertiary: #8A98A8;   // 辅助文字
$text-muted: #9AA8B8;      // 禁用/弱化
$text-white: #FFFFFF;      // 白色文字
```

### 🎨 边框与阴影

```scss
// 边框颜色
$border-color-light: #DCE1E6;
$border-color-lighter: #E4E8EC;

// 阴影
$shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
$shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
$shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.1);
```

---

## 使用场景

### 1️⃣ 按钮

#### Element Plus 按钮

```vue
<!-- 主要按钮 -->
<el-button type="primary">主要操作</el-button>

<!-- 成功按钮 -->
<el-button type="success">成功操作</el-button>

<!-- 警告按钮 -->
<el-button type="warning">警告操作</el-button>

<!-- 危险按钮 -->
<el-button type="danger">危险操作</el-button>

<!-- 信息按钮 -->
<el-button type="info">信息操作</el-button>
```

#### 自定义样式按钮

```vue
<!-- 主色渐变按钮 -->
<el-button class="custom-primary-btn">
  自定义按钮
</el-button>

<style scoped>
.custom-primary-btn {
  background: $primary-gradient;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 6px 16px rgba(91, 154, 139, 0.4);
    transform: translateY(-2px);
  }
}
</style>
```

### 2️⃣ 链接

```vue
<!-- 普通链接 -->
<el-link type="primary">默认链接</el-link>

<!-- 无下划线链接 -->
<el-link type="primary" underline="never">无下划线</el-link>

<!-- 悬停下划线 -->
<el-link type="primary" underline="hover">悬停显示</el-link>
```

### 3️⃣ 标签/徽章

```vue
<!-- 成功标签 -->
<el-tag type="success">正面情感</el-tag>

<!-- 警告标签 -->
<el-tag type="warning">中性情感</el-tag>

<!-- 危险标签 -->
<el-tag type="danger">负面情感</el-tag>

<!-- 信息标签 -->
<el-tag type="info">待处理</el-tag>
```

### 4️⃣ 进度条

```vue
<!-- 主要进度条 -->
<el-progress :percentage="75" />

<!-- 彩色进度条 -->
<el-progress :percentage="60" color="#5B9A8B" />

<!-- 状态进度条 -->
<el-progress
  :percentage="score * 100"
  :color="getScoreColor(score)"
/>
```

### 5️⃣ 背景色

```vue
<!-- 主背景 -->
<template>
  <div class="main-background">
    内容
  </div>
</template>

<style scoped>
.main-background {
  background: $bg-primary;  // #F8F9FA
}

// 卡片背景
.card {
  background: $bg-secondary;  // #FFFFFF
}

// 悬停效果
.hover-card:hover {
  background: $bg-hover;  // #E8ECF0
}
</style>
```

### 6️⃣ 文字颜色

```vue
<template>
  <div>
    <h1 class="title">主标题</h1>
    <p class="content">正文内容</p>
    <span class="hint">辅助提示</span>
  </div>
</template>

<style scoped>
.title {
  color: $text-primary;  // #2C3E50
}

.content {
  color: $text-secondary;  // #5A6878
}

.hint {
  color: $text-tertiary;  // #8A98A8
}
</style>
```

### 7️⃣ 渐变效果

```vue
<template>
  <!-- 主色渐变 -->
  <div class="gradient-primary"></div>

  <!-- 辅助渐变 -->
  <div class="gradient-secondary"></div>

  <!-- 成功渐变 -->
  <div class="gradient-success"></div>
</template>

<style scoped>
.gradient-primary {
  background: $primary-gradient;
  /* linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%) */
}

.gradient-secondary {
  background: $secondary-gradient;
  /* linear-gradient(135deg, #E8A87C 0%, #D4906A 100%) */
}

.gradient-success {
  background: $success-gradient;
  /* linear-gradient(135deg, #68C3A0 0%, #5AB38D 100%) */
}
</style>
```

---

## 代码示例

### Vue + SCSS 完整示例

```vue
<template>
  <div class="sentiment-card">
    <div class="card-header">
      <h2>情感分析结果</h2>
      <el-tag :type="sentimentType">{{ sentimentLabel }}</el-tag>
    </div>

    <div class="card-body">
      <p class="text">{{ text }}</p>

      <div class="confidence">
        <span class="label">置信度</span>
        <el-progress
          :percentage="confidence * 100"
          :color="getConfidenceColor(confidence)"
        />
      </div>

      <el-button type="primary" class="action-btn">
        查看详情
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  text: string
  sentiment: 'positive' | 'neutral' | 'negative'
  confidence: number
}>()

const sentimentLabel = computed(() => {
  const labels = {
    positive: '正面情感',
    neutral: '中性情感',
    negative: '负面情感'
  }
  return labels[props.sentiment]
})

const sentimentType = computed(() => {
  const types = {
    positive: 'success',
    neutral: 'warning',
    negative: 'danger'
  }
  return types[props.sentiment]
})

function getConfidenceColor(score: number): string {
  if (score >= 0.7) return '#68C3A0'  // 成功色
  if (score >= 0.5) return '#E8B87C'  // 警告色
  return '#E87C7C'                     // 错误色
}
</script>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.sentiment-card {
  background: $bg-secondary;
  border-radius: $border-radius;
  padding: 24px;
  box-shadow: $shadow-sm;
  transition: $transition;

  &:hover {
    box-shadow: $shadow-md;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: $text-primary;
    }
  }

  .card-body {
    .text {
      color: $text-secondary;
      line-height: 1.6;
      margin-bottom: 24px;
    }

    .confidence {
      margin-bottom: 20px;

      .label {
        display: block;
        font-size: 14px;
        color: $text-tertiary;
        margin-bottom: 8px;
      }
    }

    .action-btn {
      width: 100%;
      background: $primary-gradient;
      border: none;

      &:hover {
        box-shadow: 0 4px 12px rgba(91, 154, 139, 0.3);
      }
    }
  }
}
</style>
```

---

## 配色原则

### ✅ 推荐做法

```scss
// ✅ 使用变量
.button {
  background: $primary-gradient;
  color: $text-white;
}

// ✅ 使用护眼背景
.container {
  background: $bg-primary;  // #F8F9FA
}

// ✅ 使用状态色
.tag {
  &.success {
    color: $success-color;
    background: rgba($success-color, 0.1);
  }
}
```

### ❌ 避免做法

```scss
// ❌ 硬编码颜色
.button {
  background: #667eea;  // 旧主色
}

// ❌ 高饱和度颜色
.highlight {
  color: #FF0000;  // 刺眼的纯红
  background: #0000FF;  // 刺眼的纯蓝
}

// ❌ 纯黑纯白
.text {
  color: #000000;  // 纯黑
  background: #FFFFFF;  // 纯白
}
```

---

## 快速参考卡片

### 颜色用途速查

| 颜色 | 色值 | 用途 |
|------|------|------|
| 🟢 **主色** | `#5B9A8B` | 主要按钮、链接、高亮 |
| 🟠 **辅助色** | `#E8A87C` | 次要按钮、标签 |
| 💚 **成功色** | `#68C3A0` | 正面情感、成功状态 |
| 🟡 **警告色** | `#E8B87C` | 中性情感、警告状态 |
| ❤️ **错误色** | `#E87C7C` | 负面情感、错误状态 |
| 💙 **信息色** | `#7BA3C4` | 信息提示 |
| ⬜ **主背景** | `#F8F9FA` | 页面背景 |
| ⬛ **侧边栏** | `#3A4A46` | 深色导航背景 |

### 渐变组合

| 渐变名称 | 颜色组合 | 用途 |
|---------|---------|------|
| **主色渐变** | `#5B9A8B → #4A8B7A` | 主按钮、进度条 |
| **辅助渐变** | `#E8A87C → #D4906A` | 次要按钮、徽章 |
| **成功渐变** | `#68C3A0 → #5AB38D` | 成功状态、正面情感 |
| **警告渐变** | `#E8B87C → #D4A56A` | 警告状态、中性情感 |
| **错误渐变** | `#E87C7C → #D46A6A` | 错误状态、负面情感 |

---

## 情感分析配色

### 中文情感标签

```typescript
// 正面情感 - 绿色
{
  label: '正面情感',
  type: 'success',
  color: '#68C3A0',
  gradient: 'linear-gradient(135deg, #68C3A0 0%, #5AB38D 100%)'
}

// 中性情感 - 橙色
{
  label: '中性情感',
  type: 'warning',
  color: '#E8B87C',
  gradient: 'linear-gradient(135deg, #E8B87C 0%, #D4A56A 100%)'
}

// 负面情感 - 红色
{
  label: '负面情感',
  type: 'danger',
  color: '#E87C7C',
  gradient: 'linear-gradient(135deg, #E87C7C 0%, #D46A6A 100%)'
}
```

### 英文情感标签

```typescript
// Positive - Green
{
  label: 'Positive',
  type: 'success',
  color: '#68C3A0'
}

// Neutral - Orange
{
  label: 'Neutral',
  type: 'warning',
  color: '#E8B87C'
}

// Negative - Red
{
  label: 'Negative',
  type: 'danger',
  color: '#E87C7C'
}
```

---

## 🔧 常用工具函数

### 获取状态颜色

```typescript
// 根据置信度返回颜色
function getScoreColor(score: number): string {
  if (score >= 0.7) return '#68C3A0'  // 高置信度 - 绿色
  if (score >= 0.5) return '#E8B87C'  // 中置信度 - 橙色
  return '#E87C7C'                     // 低置信度 - 红色
}

// 根据情感类型返回标签类型
function getSentimentType(sentiment: string): string {
  const types = {
    positive: 'success',
    neutral: 'warning',
    negative: 'danger'
  }
  return types[sentiment] || 'info'
}
```

### 动态样式绑定

```vue
<template>
  <!-- 动态背景色 -->
  <div :style="{ background: scoreColor }"></div>

  <!-- 动态文字色 -->
  <span :style="{ color: statusColor }">状态文本</span>

  <!-- 动态渐变 -->
  <div :style="{ background: gradient }"></div>
</template>

<script setup>
const scoreColor = computed(() => getScoreColor(score))
const statusColor = computed(() => statusColor)
const gradient = computed(() => `linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%)`)
</script>
```

---

## 📱 Element Plus 主题配置

### 自定义主题变量

```typescript
// main.ts 或主题配置文件
import { ElConfigProvider } from 'element-plus'

app.use(ElConfigProvider, {
  props: {
    // 主色调
    color: '#5B9A8B',

    // 组件颜色
    'el-button-primary-background-color': '#5B9A8B',
    'el-button-primary-border-color': '#4A8B7A',

    // 链接颜色
    'el-link-text-color': '#5B9A8B',

    // 标签颜色
    'el-tag-success-color': '#68C3A0',
    'el-tag-warning-color': '#E8B87C',
    'el-tag-danger-color': '#E87C7C',
  }
})
```

---

## 🎯 设计检查清单

### 开发阶段
- [ ] 使用 `variables.scss` 中的颜色变量
- [ ] 避免硬编码颜色值
- [ ] 确保文字对比度符合 WCAG AA 标准
- [ ] 使用渐变而非纯色填充大面积区域

### 设计审核
- [ ] 颜色使用符合护眼原则
- [ ] 主次颜色层次分明
- [ ] 状态色清晰可辨
- [ ] 整体配色和谐统一

### 用户测试
- [ ] 长时间使用无视觉疲劳
- [ ] 颜色可识别性好
- [ ] 深色模式舒适
- [ ] 不同设备上显示正常

---

## 📚 相关文档

- 📄 [配色方案详细说明](./COLOR_SCHEME.md)
- 📊 [配色对比分析](./COLOR_COMPARISON.md)
- 🎨 [Element Plus 官方主题](https://element-plus.org/en-US/component/theme.html)

---

**版本**: v1.0.0  
**最后更新**: 2026-06-29  
**维护**: Claude Code

---

## 🎯 侧边栏（菜单栏）配色

### 完整样式代码

```scss
// 侧边栏容器
.app-sidebar {
  background: linear-gradient(180deg, #3A4A46 0%, #4A5A56 100%);
  border-right: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  // Header
  .sidebar-header {
    height: 70px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.15);
  }

  // 菜单
  .sidebar-menu {
    padding: 16px 0;

    .el-menu-item {
      margin: 4px 12px;
      border-radius: 8px;
      color: rgba(255, 255, 255, 0.65);  // 柔和白色

      &:hover {
        background: rgba(255, 255, 255, 0.08);  // 淡雅悬停
        color: white;
      }

      &.is-active {
        background: linear-gradient(90deg, rgba(91, 154, 139, 0.3) 0%, rgba(74, 139, 122, 0.3) 100%);
        color: white;
        border-right: 3px solid #5B9A8B;
        box-shadow: 0 4px 12px rgba(91, 154, 139, 0.3);
      }

      .menu-icon {
        font-size: 18px;
      }
    }
  }

  // Footer
  .sidebar-footer {
    .version {
      color: rgba(255, 255, 255, 0.4);
    }
  }
}
```

### 响应式样式

```scss
// 移动端侧边栏
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);

    &.is-open {
      transform: translateX(0);
    }
  }
}
```

### 颜色变量

```scss
// 建议添加到 variables.scss
$sidebar-gradient: linear-gradient(180deg, #3A4A46 0%, #4A5A56 100%);
$sidebar-text: rgba(255, 255, 255, 0.65);
$sidebar-hover: rgba(255, 255, 255, 0.08);
$sidebar-header-bg: rgba(0, 0, 0, 0.15);
$sidebar-active-bg: linear-gradient(90deg, rgba(91, 154, 139, 0.3) 0%, rgba(74, 139, 122, 0.3) 100%);
$sidebar-border-color: rgba(255, 255, 255, 0.08);
```

### 颜色对比

| 用途 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| **背景顶部** | `#2C3E3A` | `#3A4A46` | +8% 亮度 |
| **背景底部** | `#3A4D49` | `#4A5A56` | +8% 亮度 |
| **菜单文字** | `rgba(255,255,255,0.70)` | `rgba(255,255,255,0.65)` | -7% 不透明度 |
| **悬停背景** | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.08)` | -20% 不透明度 |
| **Header 背景** | `rgba(0,0,0,0.20)` | `rgba(0,0,0,0.15)` | -25% 不透明度 |

---

**版本**: v1.1.0  
**最后更新**: 2026-06-29  
**维护**: Claude Code
