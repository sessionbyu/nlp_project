import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SupportedLocale } from '@/types/i18n'
import { SUPPORTED_LOCALES, LOCALE_NAMES } from '@/types/i18n'

/**
 * 语言切换 Composable
 */
export function useLocale() {
  const { locale } = useI18n()

  const currentLocale = computed<SupportedLocale>(() => {
    return (locale.value as SupportedLocale) || 'zh-CN'
  })

  const locales = computed(() => {
    return SUPPORTED_LOCALES.map(loc => ({
      value: loc,
      label: LOCALE_NAMES[loc],
    }))
  })

  function setLocale(loc: SupportedLocale) {
    locale.value = loc
    localStorage.setItem('locale', loc)
  }

  function toggleLocale() {
    const newLocale = currentLocale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
    setLocale(newLocale)
  }

  return {
    currentLocale,
    locales,
    setLocale,
    toggleLocale,
  }
}
