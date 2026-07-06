<template>
  <el-dropdown trigger="click" @command="handleCommand">
    <div class="locale-switcher">
      <el-icon><Van /></el-icon>
      <span class="locale-label">{{ currentLabel }}</span>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
          v-for="loc in locales"
          :key="loc.value"
          :command="loc.value"
          :disabled="currentLocale === loc.value"
        >
          <div class="locale-item">
            <span>{{ loc.label }}</span>
            <el-icon v-if="currentLocale === loc.value"><Check /></el-icon>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Van, Check } from '@element-plus/icons-vue'
import { useLocale } from '@/composables/useLocale'

const { currentLocale, locales, setLocale } = useLocale()

const currentLabel = computed(() => {
  return locales.value.find(l => l.value === currentLocale.value)?.label || '简体中文'
})

function handleCommand(locale: string) {
  setLocale(locale as 'zh-CN' | 'en-US')
}
</script>

<style scoped lang="scss">
.locale-switcher {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .locale-label {
    font-size: 14px;
  }
}

.locale-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 100px;
}
</style>
