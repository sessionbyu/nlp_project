import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import './styles/index.scss'
import { useAuthStore } from './stores/auth'

// 应用初始化
const initApp = async () => {
  const authStore = useAuthStore()

  // 如果有 token，尝获取用户信息以验证 token 有效性
  if (authStore.isAuthenticated && !authStore.userInfo) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to initialize user:', error)
      // fetchUser 内部已经处理了 401 错误并清除了 token
    }
  }
}

// 注册 Service Worker (仅生产环境)
if (import.meta.env.PROD) {
  // @ts-ignore - virtual module
  import('virtual:pwa-register').then(({ registerSW }: any) => {
    registerSW({
      immediate: true,
      onRegistered(registration: any) {
        console.log('Service Worker registered:', registration)

        // 检查更新
        registration?.addEventListener('updatefound', () => {
          const newWorker = registration?.installing
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // 发现新版本，提示用户刷新
                ElMessage({
                  message: '发现新版本，刷新页面以更新',
                  type: 'success',
                  duration: 0,
                  showClose: true,
                })
              }
            })
          }
        })
      },
      onRegisterError(error: any) {
        console.error('Service Worker registration failed:', error)
      },
    })
  }).catch((err: any) => {
    console.error('Failed to import virtual:pwa-register:', err)
  })
}

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.use(i18n)

// 挂载应用（先挂载，再异步初始化）
app.mount('#app')

// 初始化应用（验证 token、加载用户信息等）
initApp().catch((error) => {
  console.error('Failed to initialize app:', error)
})
