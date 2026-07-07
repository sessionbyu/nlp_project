<template>
  <el-dropdown trigger="click" @command="handleCommand">
    <el-button circle class="theme-btn">
      <el-icon><component :is="themeIcon" /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="t in themes"
          :key="t.value"
          :command="t.value"
          :disabled="themeStore.theme === t.value"
        >
          <div class="theme-item">
            <el-icon>
              <component :is="t.icon" />
            </el-icon>
            <span>{{ t.label }}</span>
            <el-icon v-if="themeStore.theme === t.value">
              <Check />
            </el-icon>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sunny, Moon, Monitor, Check } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const themeIcon = computed(() => {
  return themeStore.theme
})

const themes = [
  { value: 'light', label: 'light', icon: 'Sunny' },
  { value: 'dark', label: 'dark', icon: 'Moon' },
  { value: 'auto', label: 'auto', icon: 'Monitor' },
]

function handleCommand(theme: string) {
  themeStore.setTheme(theme as 'light' | 'dark' | 'auto')
}
</script>

<style scoped lang="scss">
.theme-btn {
  border: none;
  background: transparent;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: rotate(30deg);
  }
}

.theme-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;

  .el-icon:last-child {
    margin-left: auto;
  }
}
</style>
