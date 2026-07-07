<template>
  <el-card class="stat-card-component" :class="size" shadow="hover">
    <div class="stat-content">
      <div v-if="$slots.icon || icon" class="stat-icon" :class="colorType">
        <slot name="icon">
          <el-icon :size="iconSize"><component :is="icon" /></el-icon>
        </slot>
      </div>
      <div class="stat-info">
        <div v-if="label" class="stat-label">{{ label }}</div>
        <div class="stat-value" :class="{ 'has-label': label }">
          <slot name="value">{{ value }}</slot>
        </div>
        <div v-if="$slots.extra" class="stat-extra">
          <slot name="extra"></slot>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

const props = defineProps<{
  icon?: Component
  label?: string
  value?: string | number
  colorType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'small' | 'medium' | 'large'
}>()

const iconSize = computed(() => {
  switch (props.size) {
    case 'small':
      return 20
    case 'large':
      return 36
    default:
      return 28
  }
})
</script>

<style scoped lang="scss">
.stat-card-component {
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
  }

  &.small {
    .stat-content {
      padding: 12px;

      .stat-icon {
        width: 40px;
        height: 40px;

        .el-icon {
          font-size: 20px;
        }
      }

      .stat-info {
        .stat-value {
          font-size: 20px;
        }
      }
    }
  }

  &.medium {
    .stat-content {
      padding: 20px;

      .stat-icon {
        width: 56px;
        height: 56px;

        .el-icon {
          font-size: 28px;
        }
      }

      .stat-info {
        .stat-value {
          font-size: 24px;
        }
      }
    }
  }

  &.large {
    .stat-content {
      padding: 24px;

      .stat-icon {
        width: 72px;
        height: 72px;

        .el-icon {
          font-size: 36px;
        }
      }

      .stat-info {
        .stat-value {
          font-size: 32px;
        }
      }
    }
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;

    .stat-icon {
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: all 0.3s ease;

      &.primary {
        background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
      }

      &.success {
        background: linear-gradient(135deg, #7BA3C4 0%, #6B93B4 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
      }

      &.warning {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(250, 112, 154, 0.3);
      }

      &.danger {
        background: linear-gradient(135deg, #E8A87C 0%, #D4906A 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(240, 147, 251, 0.3);
      }

      &.info {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(67, 233, 123, 0.3);
      }
    }

    .stat-info {
      flex: 1;

      .stat-label {
        font-size: 14px;
        color: #8A98A8;
        margin-bottom: 8px;
      }

      .stat-value {
        font-weight: 700;
        color: #2C3E50;
        line-height: 1;

        &.has-label {
          font-size: 28px;
        }
      }

      .stat-extra {
        margin-top: 8px;
        font-size: 12px;
        color: #8A98A8;
      }
    }
  }
}
</style>
