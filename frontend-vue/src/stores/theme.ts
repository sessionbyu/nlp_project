import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'

type Theme = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  // State
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'auto')

  // Computed
  const isDark = computed(() => {
    if (theme.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return theme.value === 'dark'
  })

  const themeIcon = computed(() => {
    if (theme.value === 'light') return 'Sunny'
    if (theme.value === 'dark') return 'Moon'
    return 'Monitor'
  })

  const themeText = computed(() => {
    if (theme.value === 'light') return 'light'
    if (theme.value === 'dark') return 'dark'
    return 'auto'
  })

  // Actions
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme()
  }

  function toggleTheme() {
    if (theme.value === 'light') {
      setTheme('dark')
    } else if (theme.value === 'dark') {
      setTheme('auto')
    } else {
      setTheme('light')
    }
  }

  function applyTheme() {
    const html = document.documentElement
    if (isDark.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }

  // 监听系统主题变化
  function watchSystemTheme() {
    if (theme.value === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', applyTheme)
      return () => mediaQuery.removeEventListener('change', applyTheme)
    }
    return () => {}
  }

  // 初始化
  watch(theme, () => {
    applyTheme()
  }, { immediate: true })

  return {
    theme,
    isDark,
    themeIcon,
    themeText,
    setTheme,
    toggleTheme,
    applyTheme,
    watchSystemTheme,
  }
})
