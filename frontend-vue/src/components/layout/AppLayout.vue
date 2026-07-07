<template>
  <el-container class="app-container">
    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobile && !appStore.sidebarCollapsed"
      class="sidebar-overlay"
      @click="appStore.sidebarCollapsed = true"
    />

    <el-aside :width="appStore.sidebarCollapsed ? '80px' : '260px'" class="app-sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span v-if="!appStore.sidebarCollapsed" class="logo-text">NLP 预测平台</span>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="appStore.sidebarCollapsed"
        :collapse-transition="true"
        :show-title="true"
        router
        class="sidebar-menu"
        :style="{ background: 'linear-gradient(180deg, #3A4A46 0%, #4A5A56 100%)' }"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
          :title="route.meta?.title"
        >
          <el-icon class="menu-icon">
            <component :is="route.meta?.icon || 'Document'" />
          </el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer" v-if="!appStore.sidebarCollapsed">
        <div class="version">v1.0.0</div>
      </div>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-button
            :icon="isMobile ? Menu : (appStore.sidebarCollapsed ? Expand : Fold)"
            circle
            @click="handleMenuToggle"
            class="toggle-btn"
          />
          <div class="header-title">
            <h1>{{ pageTitle }}</h1>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item>{{ pageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>

        <div class="header-right">
          <el-button circle class="notification-btn">
            <el-icon><Bell /></el-icon>
          </el-button>
          <ThemeSwitcher />
          <LocaleSwitcher />

          <el-dropdown>
            <div class="user-info">
              <el-avatar :size="36" :icon="User" />
              <span class="username">{{ authStore.userInfo?.nickname || '管理员' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleProfile">
                  <el-icon><User /></el-icon>
                  个人设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <el-footer class="app-footer">
        <div class="footer-content">
          <span>© 2026 NLP 预测平台. All rights reserved.</span>
          <div class="footer-links">
            <a href="#">文档</a>
            <span class="divider">|</span>
            <a href="#">关于</a>
          </div>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'
import {
  Fold,
  Expand,
  User,
  Bell,
  Document,
  Timer,
  DataAnalysis,
  List,
  SwitchButton,
  Monitor,
  Upload,
  Menu,
  Management,
  Cpu,
} from '@element-plus/icons-vue'
import ThemeSwitcher from '@/components/common/ThemeSwitcher.vue'
import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()
const themeStore = useThemeStore()

// 检测是否为移动端
const isMobile = ref(window.innerWidth < 768)

// 监听窗口大小变化
const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    // 桌面端：确保侧边栏状态正确
    appStore.sidebarCollapsed = false
  }
}

// 动态从路由配置中获取菜单项
const menuRoutes = computed(() => {
  try {
    // 获取所有路由
    const allRoutes = router.getRoutes()

    // 找到 AppLayout 组件对应的路由（有 children 数组的）
    const layoutRoute = allRoutes.find(route =>
      route.path === '/' && route.children && route.children.length > 0
    )

    if (!layoutRoute?.children) return []

    // 如果用户信息还未加载，先显示所有菜单（不进行权限过滤）
    // 避免权限检查未完成时菜单全部消失
    if (authStore.loading || !authStore.userInfo?.value) {
      return layoutRoute.children
        .filter(child => !child.meta?.hideInMenu)
        .map(child => ({
          path: `/${child.path}`,
          meta: {
            title: child.meta?.title as string,
            icon: child.meta?.icon as string,
          },
        }))
    }

    // 过滤掉不需要在菜单中显示的路由
    return layoutRoute.children
      .filter(child => {
        // 排除标记为隐藏的路由
        if (child.meta?.hideInMenu) {
          return false
        }

        // 如果路由定义了权限要求，检查用户是否有权限
        const requiredPermission = child.meta?.permission as string | undefined
        if (requiredPermission) {
          try {
            return authStore.hasPermission(requiredPermission)
          } catch (error) {
            console.error('Error checking permission:', error, requiredPermission)
            // 权限检查出错时，默认显示该菜单项
            return true
          }
        }

        // 如果没有定义权限要求，默认显示
        return true
      })
      .map(child => ({
        path: `/${child.path}`,
        meta: {
          title: child.meta?.title as string,
          icon: child.meta?.icon as string,
        },
      }))
  } catch (error) {
    console.error('Error computing menuRoutes:', error)
    // 出错时返回空数组，避免影响整个页面渲染
    return []
  }
})

const pageTitle = computed(() => route.meta.title || 'NLP 预测平台')

// 处理菜单切换
const handleMenuToggle = () => {
  if (isMobile.value) {
    // 移动端：切换侧边栏的显示/隐藏
    appStore.sidebarCollapsed = !appStore.sidebarCollapsed
  } else {
    // 桌面端：正常切换折叠状态
    appStore.toggleSidebar()
  }
}

// 点击外部关闭侧边栏（移动端）
const handleClickOutside = (event: MouseEvent) => {
  if (isMobile.value && !appStore.sidebarCollapsed) {
    const sidebar = document.querySelector('.app-sidebar')
    const toggleBtn = document.querySelector('.toggle-btn')
    if (sidebar && !sidebar.contains(event.target as Node) && !toggleBtn?.contains(event.target as Node)) {
      appStore.sidebarCollapsed = true
    }
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
})

function handleProfile() {
  router.push('/profile')
}

async function handleLogout() {
  console.log('[AppLayout] 开始退出登录')
  try {
    await authStore.logout()
    console.log('[AppLayout] 退出登录完成，等待状态更新')
    // 等待下一个 tick，确保响应式状态完全更新
    await nextTick()
    console.log('[AppLayout] 状态已更新:', {
      isAuthenticated: authStore.isAuthenticated,
      hasToken: !!authStore.token
    })
    ElMessage.success('已退出登录')
  } catch (error) {
    console.error('[AppLayout] 退出登录失败:', error)
    ElMessage.error('退出登录失败，请重试')
  }
  // 无论成功与否，都跳转到登录页
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-container {
  height: 100vh;
}

.app-sidebar {
  background: linear-gradient(180deg, #3A4A46 0%, #4A5A56 100%);
  border-right: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  .sidebar-header {
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.15);

    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 20px;

      .logo-icon {
        font-size: 28px;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
      }

      .logo-text {
        font-size: 18px;
        font-weight: 700;
        color: white;
        letter-spacing: 0.5px;
      }
    }
  }

  .sidebar-menu {
    border-right: none;
    padding: 16px 0;
    width: 100%;
    background: linear-gradient(180deg, #3A4A46 0%, #4A5A56 100%) !important;

    // 确保菜单项不换行
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    // 展开状态下的菜单项样式
    :deep(.el-menu-item) {
      margin: 4px 12px;
      border-radius: 8px;
      color: rgba(255, 255, 255, 0.65);
      transition: all 0.3s ease;
      min-height: 48px;
      line-height: 48px;

      &:hover {
        background: rgba(255, 255, 255, 0.08);
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
        min-width: 24px;
        text-align: center;
      }

      // 确保标题文本正确显示
      span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: block;
        max-width: 100%;
      }
    }

    // 折叠状态下的样式优化
    &.el-menu--collapse {
      :deep(.el-menu-item) {
        margin: 4px 8px;
        padding: 0 !important;
        justify-content: center;
        min-width: 64px;

        .menu-icon {
          margin: 0;
        }

        // 折叠时隐藏所有文本内容
        :deep(span:not(.menu-icon)) {
          display: none !important;
        }
      }
    }

    // 子菜单样式（如果未来需要）
    :deep(.el-sub-menu) {
      .el-sub-menu__title {
        margin: 4px 12px;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.65);
        transition: all 0.3s ease;

        &:hover {
          background: rgba(255, 255, 255, 0.08);
          color: white;
        }

        i {
          font-size: 18px;
        }

        span {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          display: block;
          max-width: 100%;
        }
      }

      &.el-menu--inline {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 0 0 8px 8px;

        .el-menu-item {
          margin-left: 20px;
        }
      }
    }
  }

  .sidebar-footer {
    position: absolute;
    bottom: 20px;
    left: 0;
    right: 0;
    text-align: center;

    .version {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.4);
    }
  }
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-bottom: 1px solid #DCE1E6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  padding: 0 24px;
  height: 70px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .toggle-btn {
      border: none;
      background: #F8F9FA;
      transition: all 0.3s ease;

      &:hover {
        background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
        color: white;
        transform: rotate(180deg);
      }
    }

    .header-title {
      h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }

      :deep(.el-breadcrumb) {
        margin-top: 4px;
        font-size: 12px;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .notification-btn {
      border: none;
      background: #F8F9FA;
      transition: all 0.3s ease;

      &:hover {
        background: linear-gradient(135deg, #E8A87C 0%, #D4906A 100%);
        color: white;
        transform: scale(1.1);
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 8px;
      transition: all 0.3s ease;

      &:hover {
        background: #F8F9FA;
      }

      .username {
        font-weight: 500;
        color: #2C3E50;
      }
    }
  }
}

.app-main {
  background: linear-gradient(135deg, #F8F9FA 0%, #E8ECF0 100%);
  padding: 24px;
  overflow-y: auto;
  min-height: calc(100vh - 70px - 60px);

  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
  }

  .fade-enter-from {
    opacity: 0;
    transform: translateY(10px);
  }

  .fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

.app-footer {
  text-align: center;
  background: white;
  border-top: 1px solid #DCE1E6;
  color: #8A98A8;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;

  .footer-content {
    display: flex;
    align-items: center;
    gap: 16px;

    .footer-links {
      display: flex;
      align-items: center;
      gap: 8px;

      a {
        color: #8A98A8;
        transition: all 0.3s ease;

        &:hover {
          color: #5B9A8B;
        }
      }

      .divider {
        color: #DCE1E6;
      }
    }
  }
}

@media (max-width: 768px) {
  // 移动端遮罩层
  .sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .app-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &.is-open {
      transform: translateX(0);
    }
  }

  .app-main {
    padding: 16px;
  }

  .header-left {
    .header-title {
      h1 {
        font-size: 18px;
      }

      :deep(.el-breadcrumb) {
        display: none;
      }
    }
  }

  .header-right {
    .username {
      display: none;
    }
  }
}

@media (prefers-color-scheme: dark) {
  .app-main {
    background: linear-gradient(135deg, #3A4A46 0%, #4A5A56 100%);
  }
}
</style>
