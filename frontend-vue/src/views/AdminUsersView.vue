<template>
  <div class="admin-users-view">
    <div class="page-header">
      <h1>👥 用户管理</h1>
      <p class="subtitle">管理系统用户和权限</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="User"
          label="总用户数"
          :value="stats.total_users"
          color-type="primary"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="CircleCheck"
          label="活跃用户"
          :value="stats.active_users"
          color-type="success"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="Key"
          label="API Keys"
          :value="stats.total_api_keys"
          color-type="warning"
          size="medium"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
        <StatCard
          :icon="UserFilled"
          label="新增用户(7天)"
          :value="stats.recent_registrations"
          color-type="info"
          size="medium"
        />
      </el-col>
    </el-row>

    <!-- 过滤器 -->
    <el-card class="filter-card fade-in">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名/邮箱..."
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-select
            v-model="roleFilter"
            placeholder="角色"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-select
            v-model="statusFilter"
            placeholder="状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="激活" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="24" :md="6">
          <div class="filter-actions">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button
              type="primary"
              plain
              @click="handleRefresh"
              :loading="refreshing"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 用户列表 -->
    <div class="user-list">
      <transition name="slide-up">
        <div v-if="loading" class="loading-state">
          <Loading :visible="true" text="加载用户列表..." />
        </div>

        <div v-else-if="filteredUsers.length === 0" class="empty-state">
          <el-empty description="暂无用户">
            <el-button type="primary" @click="handleRefresh">刷新</el-button>
          </el-empty>
        </div>

        <div v-else class="user-items">
          <div
            v-for="user in paginatedUsers"
            :key="user.id"
            class="user-item fade-in"
          >
            <el-card>
              <div class="user-header">
                <div class="user-avatar">
                  <el-avatar :size="50" :icon="UserFilled" />
                </div>
                <div class="user-info">
                  <div class="user-name">
                    <el-text strong>{{ user.nickname || user.username }}</el-text>
                    <el-tag
                      v-if="user.role === 'admin'"
                      type="danger"
                      effect="dark"
                      size="small"
                    >
                      管理员
                    </el-tag>
                  </div>
                  <div class="user-meta">
                    <el-text type="info" size="small">@{{ user.username }}</el-text>
                    <el-divider direction="vertical" />
                    <el-text type="info" size="small">{{ user.email }}</el-text>
                  </div>
                  <div class="user-stats">
                    <el-text type="info" size="small">
                      <el-icon><Clock /></el-icon>
                      注册于 {{ formatDate(user.created_at) }}
                    </el-text>
                    <el-text v-if="user.last_login" type="info" size="small">
                      <el-divider direction="vertical" />
                      <el-icon><Select /></el-icon>
                      最后登录 {{ formatDate(user.last_login) }}
                    </el-text>
                  </div>
                </div>
                <div class="user-status">
                  <el-tag
                    :type="user.is_active ? 'success' : 'danger'"
                    effect="dark"
                  >
                    {{ user.is_active ? '激活' : '禁用' }}
                  </el-tag>
                  <el-tag
                    v-if="user.is_verified"
                    type="info"
                    effect="plain"
                    size="small"
                  >
                    已验证
                  </el-tag>
                </div>
              </div>

              <div class="user-actions">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleViewAPIKeys(user)"
                >
                  <el-icon><Key /></el-icon>
                  API Keys
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click="handleToggleActive(user)"
                  :loading="togglingUser === user.id"
                >
                  <el-icon>
                    <SwitchButton v-if="user.is_active" />
                    <Close v-else />
                  </el-icon>
                  {{ user.is_active ? '禁用' : '激活' }}
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click="handleDelete(user)"
                  :loading="deletingUser === user.id"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </transition>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalUsers"
          layout="total, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- API Keys 对话框 -->
    <el-dialog
      v-model="apiKeysDialogVisible"
      :title="`${selectedUser?.nickname || selectedUser?.username} - API Keys`"
      width="700px"
    >
      <div class="api-keys-header">
        <el-button
          type="primary"
          @click="handleCreateAPIKey"
          :loading="creatingAPIKey"
        >
          <el-icon><Plus /></el-icon>
          创建 API Key
        </el-button>
      </div>

      <el-table
        :data="userAPIKeys"
        v-loading="loadingAPIKeys"
        style="width: 100%"
      >
        <el-table-column
          prop="name"
          label="名称"
          width="150"
        />
        <el-table-column
          prop="key_prefix"
          label="Key 前缀"
          width="150"
        >
          <template #default="{ row }">
            <el-text code>{{ row.key_prefix }}...</el-text>
          </template>
        </el-table-column>
        <el-table-column
          prop="permissions"
          label="权限"
          width="120"
        />
        <el-table-column
          prop="is_active"
          label="状态"
          width="100"
        >
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="expires_at"
          label="过期时间"
          width="150"
        >
          <template #default="{ row }">
            {{ row.expires_at ? formatDate(row.expires_at) : '永不过期' }}
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="120"
        >
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="handleRevokeAPIKey(row.id)"
              :loading="revokingKey === row.id"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="userAPIKeys.length === 0 && !loadingAPIKeys" class="empty-keys">
        <el-empty description="暂无 API Keys" />
      </div>
    </el-dialog>

    <!-- 创建 API Key 对话框 -->
    <el-dialog
      v-model="createKeyDialogVisible"
      title="创建 API Key"
      width="500px"
    >
      <el-form
        ref="createKeyFormRef"
        :model="createKeyForm"
        :rules="createKeyRules"
        label-position="top"
      >
        <el-form-item label="名称" prop="name">
          <el-input
            v-model="createKeyForm.name"
            placeholder="例如: 生产环境"
          />
        </el-form-item>
        <el-form-item label="权限" prop="permissions">
          <el-input
            v-model="createKeyForm.permissions"
            placeholder="predict,history（逗号分隔）"
          />
        </el-form-item>
        <el-form-item label="有效期（天）">
          <el-input-number
            v-model="createKeyForm.expires_in_days"
            :min="1"
            :max="365"
            :step="30"
          />
          <div class="form-tip">留空表示永不过期</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createKeyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreateKey" :loading="creatingAPIKey">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- API Key 显示对话框 -->
    <el-dialog
      v-model="showKeyDialogVisible"
      title="API Key 创建成功"
      width="500px"
    >
      <div class="api-key-success">
        <el-alert
          title="请妥善保存此 API Key，它只会显示一次！"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="api-key-display">
          <el-text code class="api-key-value">{{ createdAPIKey }}</el-text>
          <el-button
            type="primary"
            @click="handleCopyAPIKey"
            :icon="useDocumentCopy()"
          >
            复制
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  User,
  UserFilled,
  CircleCheck,
  Key,
  Search,
  RefreshLeft,
  Refresh,
  Clock,
  Select,
  Delete,
  SwitchButton,
  Plus,
  DocumentCopy,
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getUsers, updateUser, deleteUser, getUserAPIKeys, createAPIKeyForUser, revokeAPIKey, getAdminStats, type AdminUserResponse, type APIKeyResponse } from '@/api/admin'
import StatCard from '@/components/common/StatCard.vue'
import Loading from '@/components/common/Loading.vue'

const router = useRouter()

// 状态
const loading = ref(false)
const refreshing = ref(false)
const users = ref<AdminUserResponse[]>([])
const stats = ref({
  total_users: 0,
  active_users: 0,
  total_api_keys: 0,
  recent_registrations: 0,
})

// 过滤
const searchKeyword = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalUsers = ref(0)

// API Keys
const apiKeysDialogVisible = ref(false)
const selectedUser = ref<AdminUserResponse | null>(null)
const userAPIKeys = ref<APIKeyResponse[]>([])
const loadingAPIKeys = ref(false)
const togglingUser = ref<number | null>(null)
const deletingUser = ref<number | null>(null)
const revokingKey = ref<number | null>(null)

// 创建 API Key
const createKeyDialogVisible = ref(false)
const creatingAPIKey = ref(false)
const createKeyFormRef = ref<FormInstance>()
const createKeyForm = ref({
  name: '',
  permissions: 'predict,history',
  expires_in_days: 90,
})
const createKeyRules: FormRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}
const showKeyDialogVisible = ref(false)
const createdAPIKey = ref('')

// 计算属性
const filteredUsers = computed(() => {
  let result = users.value

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(
      (u) =>
        u.username.toLowerCase().includes(keyword) ||
        u.email.toLowerCase().includes(keyword)
    )
  }

  // 角色过滤
  if (roleFilter.value) {
    result = result.filter((u) => u.role === roleFilter.value)
  }

  // 状态过滤
  if (statusFilter.value) {
    result = result.filter((u) =>
      statusFilter.value === 'true' ? u.is_active : !u.is_active
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / pageSize.value))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
})

// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await getUsers(currentPage.value, pageSize.value)
    users.value = response.users
    totalUsers.value = response.total
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const data = await getAdminStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 重置
const handleReset = () => {
  searchKeyword.value = ''
  roleFilter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
}

// 刷新
const handleRefresh = async () => {
  refreshing.value = true
  try {
    await Promise.all([fetchUsers(), fetchStats()])
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 分页
const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 查看 API Keys
const handleViewAPIKeys = async (user: AdminUserResponse) => {
  selectedUser.value = user
  apiKeysDialogVisible.value = true

  try {
    loadingAPIKeys.value = true
    const keys = await getUserAPIKeys(user.id)
    userAPIKeys.value = keys
  } catch (error) {
    ElMessage.error('获取 API Keys 失败')
  } finally {
    loadingAPIKeys.value = false
  }
}

// 创建 API Key
const handleCreateAPIKey = () => {
  selectedUser.value && (createKeyForm.value = {
    name: '',
    permissions: 'predict,history',
    expires_in_days: 90,
  })
  createKeyDialogVisible.value = true
}

// 确认创建 API Key
const handleConfirmCreateKey = async () => {
  if (!selectedUser.value) return

  try {
    await createKeyFormRef.value?.validate()
    creatingAPIKey.value = true

    const response = await createAPIKeyForUser(selectedUser.value.id, {
      name: createKeyForm.value.name,
      permissions: createKeyForm.value.permissions,
      expires_in_days: createKeyForm.value.expires_in_days,
    })

    createdAPIKey.value = response.api_key
    createKeyDialogVisible.value = false
    showKeyDialogVisible.value = true

    // 刷新 API Keys 列表
    const keys = await getUserAPIKeys(selectedUser.value.id)
    userAPIKeys.value = keys
    await fetchStats()
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    creatingAPIKey.value = false
  }
}

// 复制 API Key
const handleCopyAPIKey = () => {
  navigator.clipboard.writeText(createdAPIKey.value)
  ElMessage.success('已复制到剪贴板')
}

// 撤销 API Key
const handleRevokeAPIKey = async (keyId: number) => {
  try {
    await ElMessageBox.confirm('确定要撤销这个 API Key 吗？', '确认撤销', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    revokingKey.value = keyId
    await revokeAPIKey(keyId)
    ElMessage.success('API Key 已撤销')

    // 刷新列表
    if (selectedUser.value) {
      const keys = await getUserAPIKeys(selectedUser.value.id)
      userAPIKeys.value = keys
      await fetchStats()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤销失败')
    }
  } finally {
    revokingKey.value = null
  }
}

// 切换用户状态
const handleToggleActive = async (user: AdminUserResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要${user.is_active ? '禁用' : '激活'}用户 ${user.username} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    togglingUser.value = user.id
    await updateUser(user.id, { is_active: !user.is_active })
    ElMessage.success(`${user.is_active ? '禁用' : '激活'}成功`)

    // 刷新列表
    await fetchUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    togglingUser.value = null
  }
}

// 删除用户
const handleDelete = async (user: AdminUserResponse) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    deletingUser.value = user.id
    await deleteUser(user.id)
    ElMessage.success('删除成功')

    // 刷新列表和统计
    await Promise.all([fetchUsers(), fetchStats()])
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    deletingUser.value = null
  }
}

// 格式化日期
const formatDate = (date: string) => {
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`

  return d.toLocaleDateString('zh-CN')
}

// 生命周期
onMounted(() => {
  fetchUsers()
  fetchStats()
})
</script>

<style scoped lang="scss">
.admin-users-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.stats-row {
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-actions {
    display: flex;
    gap: 8px;
  }
}

.loading-state,
.empty-state {
  padding: 60px 0;
}

.user-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-item {
  .user-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 16px;

    .user-avatar {
      flex-shrink: 0;
    }

    .user-info {
      flex: 1;

      .user-name {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 16px;
      }

      .user-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
      }

      .user-stats {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
      }
    }

    .user-status {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: flex-end;
    }
  }

  .user-actions {
    display: flex;
    gap: 8px;
    padding-top: 16px;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.api-keys-header {
  margin-bottom: 16px;
}

.empty-keys {
  padding: 40px 0;
}

.api-key-success {
  .api-key-display {
    margin-top: 16px;
    padding: 16px;
    background: var(--el-bg-color-page);
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 12px;

    .api-key-value {
      flex: 1;
      word-break: break-all;
      font-family: monospace;
      font-size: 14px;
      color: var(--el-color-primary);
    }
  }
}

.form-tip {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
