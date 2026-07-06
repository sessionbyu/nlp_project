<template>
  <div class="admin-layout">
    <div class="admin-sidebar">
      <div class="admin-nav">
        <div class="nav-section">
          <div class="nav-title">管理面板</div>
          <router-link to="/admin/users" class="nav-item" active-class="active">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </router-link>
          <router-link to="/admin/monitoring" class="nav-item" active-class="active">
            <el-icon><Monitor /></el-icon>
            <span>系统监控</span>
          </router-link>
        </div>
      </div>
    </div>

    <div class="admin-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Monitor } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-sidebar {
  width: 240px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  overflow-y: auto;

  .admin-nav {
    padding: 20px 0;

    .nav-section {
      margin-bottom: 20px;

      .nav-title {
        padding: 0 20px 12px;
        font-size: 12px;
        font-weight: 600;
        color: var(--el-text-color-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 20px;
        color: var(--el-text-color-regular);
        text-decoration: none;
        transition: all 0.3s;
        border-left: 3px solid transparent;

        &:hover {
          background: var(--el-bg-color-page);
          color: var(--el-color-primary);
        }

        &.active {
          background: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
          border-left-color: var(--el-color-primary);
        }

        .el-icon {
          font-size: 18px;
        }
      }
    }
  }
}

.admin-content {
  flex: 1;
  margin-left: 240px;
  padding: 24px;
  background: var(--el-bg-color-page);
  min-height: 100vh;
}
</style>
