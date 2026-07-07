<template>
  <el-card class="result-card-component" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="header-title">
          <slot name="icon">
            <el-icon class="header-icon"><component :is="icon" /></el-icon>
          </slot>
          <slot name="title">{{ title }}</slot>
        </span>
        <div v-if="$slots.extra" class="header-extra">
          <slot name="extra"></slot>
        </div>
      </div>
    </template>

    <div class="result-content">
      <slot></slot>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon?: Component
  title?: string
}>()
</script>

<style scoped lang="scss">
.result-card-component {
  border-radius: 12px;
  background: linear-gradient(135deg, #F8F9FA 0%, #ffffff 100%);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 16px;

      .header-icon {
        color: #5B9A8B;
        font-size: 18px;
      }
    }

    .header-extra {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .result-content {
    padding: 8px 0;
  }
}
</style>
