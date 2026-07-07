<template>
  <div class="loading-overlay" :class="{ 'full-screen': fullScreen }" v-if="visible">
    <div class="loading-content">
      <div class="loading-spinner">
        <el-icon class="loading-icon"><Loading /></el-icon>
      </div>
      <p class="loading-text">{{ text }}</p>
      <div class="loading-progress" v-if="showProgress">
        <el-progress
          :percentage="progress"
          :stroke-width="6"
          :show-text="false"
          :color="progressColor"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  visible?: boolean
  text?: string
  progress?: number
  showProgress?: boolean
  fullScreen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  text: '加载中...',
  progress: 0,
  showProgress: false,
  fullScreen: true,
})

const progressColor = computed(() => {
  if (props.progress < 30) return '#f56c6c'
  if (props.progress < 70) return '#e6a23c'
  return '#67c23a'
})
</script>

<style scoped lang="scss">
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: all 0.3s ease;

  &.full-screen {
    position: fixed;
  }

  &:not(.full-screen) {
    position: absolute;
  }

  // 暗色模式支持
  html.dark & {
    background: rgba(0, 0, 0, 0.8);
  }
}

.loading-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  min-width: 200px;

  html.dark & {
    background: #1a1a2e;
  }
}

.loading-spinner {
  margin-bottom: 20px;

  .loading-icon {
    font-size: 48px;
    color: #5B9A8B;
    animation: rotate 2s linear infinite;

    html.dark & {
      color: #818cf8;
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 16px;
  color: #5A6878;
  margin: 0 0 20px 0;
  font-weight: 500;

  html.dark & {
    color: #a1a1aa;
  }
}

.loading-progress {
  width: 200px;
  margin: 0 auto;
}
</style>
