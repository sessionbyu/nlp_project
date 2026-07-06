<template>
  <div class="error-message" :class="type" v-if="visible">
    <div class="error-icon">
      <el-icon v-if="type === 'error'"><CircleClose /></el-icon>
      <el-icon v-else-if="type === 'warning'"><Warning /></el-icon>
      <el-icon v-else-if="type === 'info'"><InfoFilled /></el-icon>
      <el-icon v-else><SuccessFilled /></el-icon>
    </div>
    <div class="error-content">
      <div class="error-title" v-if="title">{{ title }}</div>
      <div class="error-text">{{ message }}</div>
      <div class="error-detail" v-if="detail">
        <el-text type="info" size="small">{{ detail }}</el-text>
      </div>
    </div>
    <div class="error-actions" v-if="$slots.actions">
      <slot name="actions"></slot>
    </div>
    <el-button
      v-else-if="closable"
      class="error-close"
      :icon="Close"
      circle
      size="small"
      @click="handleClose"
    />
  </div>
</template>

<script setup lang="ts">
import { Close, CircleClose, Warning, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'

interface Props {
  visible?: boolean
  message?: string
  title?: string
  detail?: string
  type?: 'error' | 'warning' | 'info' | 'success'
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  visible: true,
  message: '出错了',
  type: 'error',
  closable: true,
})

const emit = defineEmits<{
  close: []
}>()

function handleClose() {
  emit('close')
}
</script>

<style scoped lang="scss">
.error-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  animation: slideDown 0.3s ease;

  &.error {
    background: #fef0f0;
    border: 1px solid #fde2e2;
    color: #f56c6c;

    .error-icon {
      color: #f56c6c;
    }
  }

  &.warning {
    background: #fdf6ec;
    border: 1px solid #faecd8;
    color: #e6a23c;

    .error-icon {
      color: #e6a23c;
    }
  }

  &.info {
    background: #f4f4f5;
    border: 1px solid #e9e9eb;
    color: #8A98A8;

    .error-icon {
      color: #8A98A8;
    }
  }

  &.success {
    background: #f0f9ff;
    border: 1px solid #d1fae5;
    color: #67c23a;

    .error-icon {
      color: #67c23a;
    }
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  flex-shrink: 0;
  font-size: 20px;
  margin-top: 2px;
}

.error-content {
  flex: 1;
  min-width: 0;

  .error-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .error-text {
    font-size: 14px;
    line-height: 1.6;
    word-break: break-word;
  }

  .error-detail {
    margin-top: 8px;
    padding: 8px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    font-family: 'Courier New', monospace;
  }
}

.error-actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

.error-close {
  flex-shrink: 0;
  border: none;
  background: transparent;

  &:hover {
    background: rgba(0, 0, 0, 0.1);
  }
}
</style>
