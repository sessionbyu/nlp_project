<template>
  <div class="profile-view">
    <div class="page-header">
      <h1>⚙️ 个人设置</h1>
      <p class="subtitle">管理您的账户信息和偏好设置</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：用户信息 -->
      <el-col :xs="24" :lg="10">
        <!-- 用户卡片 -->
        <el-card class="user-card fade-in">
          <div class="user-info">
            <el-avatar :size="80" :icon="UserFilled" />
            <div class="user-details">
              <h2>{{ authStore.user?.nickname || authStore.user?.username }}</h2>
              <el-text type="info">@{{ authStore.user?.username }}</el-text>
              <div class="user-meta">
                <el-tag :type="authStore.user?.role === 'admin' ? 'danger' : 'primary'" effect="dark">
                  {{ authStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
                </el-tag>
                <el-tag v-if="authStore.user?.is_verified" type="success" effect="plain">
                  已验证
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="password-card fade-in" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Lock /></el-icon>
                修改密码
              </span>
            </div>
          </template>

          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-position="top"
          >
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input
                v-model="passwordForm.currentPassword"
                type="password"
                show-password
                placeholder="请输入当前密码"
              />
            </el-form-item>

            <el-form-item label="新密码" prop="newPassword">
              <el-input
                v-model="passwordForm.newPassword"
                type="password"
                show-password
                placeholder="请输入新密码（至少6位）"
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input
                v-model="passwordForm.confirmPassword"
                type="password"
                show-password
                placeholder="请再次输入新密码"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleChangePassword"
                :loading="changingPassword"
              >
                <el-icon><Lock /></el-icon>
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：偏好设置 -->
      <el-col :xs="24" :lg="14">
        <!-- 个人信息 -->
        <el-card class="profile-card fade-in">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><User /></el-icon>
                个人信息
              </span>
            </div>
          </template>

          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-position="top"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input
                    v-model="profileForm.username"
                    placeholder="用户名"
                    :disabled="true"
                  >
                    <template #prepend>用户名</template>
                  </el-input>
                  <div class="form-tip">用户名不可修改</div>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="昵称" prop="nickname">
                  <el-input
                    v-model="profileForm.nickname"
                    placeholder="请输入昵称"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="profileForm.email"
                    placeholder="请输入邮箱"
                    clearable
                  >
                    <template #prepend>邮箱</template>
                  </el-input>
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input
                    v-model="profileForm.phone"
                    placeholder="请输入手机号"
                    clearable
                  >
                    <template #prepend>手机</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleUpdateProfile"
                :loading="updatingProfile"
              >
                <el-icon><Check /></el-icon>
                保存信息
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 偏好设置 -->
        <el-card class="preferences-card fade-in" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Setting /></el-icon>
                偏好设置
              </span>
            </div>
          </template>

          <el-form label-position="top">
            <!-- 语言设置 -->
            <el-form-item label="语言">
              <el-select
                v-model="preferences.language"
                @change="handleLanguageChange"
                style="width: 100%"
              >
                <el-option label="🇨🇳 简体中文" value="zh-CN" />
                <el-option label="🇺🇸 English" value="en-US" />
              </el-select>
            </el-form-item>

            <!-- 主题设置 -->
            <el-form-item label="主题">
              <el-radio-group v-model="preferences.theme" @change="handleThemeChange">
                <el-radio-button value="light">
                  <el-icon><Sunny /></el-icon>
                  亮色
                </el-radio-button>
                <el-radio-button value="dark">
                  <el-icon><Moon /></el-icon>
                  暗色
                </el-radio-button>
                <el-radio-button value="auto">
                  <el-icon><Operation /></el-icon>
                  自动
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 通知设置 -->
            <el-form-item label="通知">
              <el-checkbox-group v-model="preferences.notifications">
                <el-checkbox label="email">邮件通知</el-checkbox>
                <el-checkbox label="browser">浏览器通知</el-checkbox>
                <el-checkbox label="task">任务完成通知</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- API Keys -->
        <el-card class="api-keys-card fade-in" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon class="header-icon"><Key /></el-icon>
                API Keys
              </span>
              <el-button type="primary" size="small" @click="handleCreateAPIKey">
                <el-icon><Plus /></el-icon>
                创建新 Key
              </el-button>
            </div>
          </template>

          <el-table :data="apiKeys" v-loading="loadingKeys" style="width: 100%">
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
                  @click="handleRevokeKey(row.id)"
                  :loading="revokingKey === row.id"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="apiKeys.length === 0 && !loadingKeys" description="暂无 API Keys" />

          <!-- 创建 Key 对话框 -->
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
                  placeholder="例如: 个人使用"
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
              <el-button type="primary" @click="handleConfirmCreateKey" :loading="creatingKey">
                创建
              </el-button>
            </template>
          </el-dialog>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  User,
  UserFilled,
  Lock,
  Setting,
  Key,
  Plus,
  Delete,
  Check,
  Sunny,
  Moon,
  Operation,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  updateProfile,
  changePassword,
  getUserAPIKeys,
  createAPIKey,
  revokeAPIKey,
  type APIKeyResponse,
} from '@/api/auth'

const authStore = useAuthStore()

// 个人信息
const profileFormRef = ref<FormInstance>()
const profileForm = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
})
const updatingProfile = ref(false)
const profileRules = {
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
}

// 密码修改
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})
const changingPassword = ref(false)
const passwordRules: FormRules = {
  currentPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 偏好设置
const preferences = reactive({
  language: localStorage.getItem('language') || 'zh-CN',
  theme: localStorage.getItem('theme') || 'auto',
  notifications: [] as string[],
})

// API Keys
const apiKeys = ref<APIKeyResponse[]>([])
const loadingKeys = ref(false)
const revokingKey = ref<number | null>(null)

// 创建 Key
const createKeyDialogVisible = ref(false)
const creatingKey = ref(false)
const createKeyFormRef = ref<FormInstance>()
const createKeyForm = reactive({
  name: '',
  permissions: 'predict,history',
  expires_in_days: 90,
})
const createKeyRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 更新个人信息
async function handleUpdateProfile() {
  if (!profileFormRef.value) return

  try {
    await profileFormRef.value.validate()
    updatingProfile.value = true

    await updateProfile({
      nickname: profileForm.nickname,
      email: profileForm.email,
      phone: profileForm.phone,
    })

    ElMessage.success('个人信息更新成功')
    authStore.fetchUser()
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updatingProfile.value = false
  }
}

// 修改密码
async function handleChangePassword() {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true

    await changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword,
    })

    ElMessage.success('密码修改成功')
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    ElMessage.error(error.message || '修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 语言切换
function handleLanguageChange(lang: string) {
  localStorage.setItem('language', lang)
  window.location.reload()
}

// 主题切换
function handleThemeChange(theme: string) {
  localStorage.setItem('theme', theme)
  window.location.reload()
}

// 获取 API Keys
async function fetchAPIKeys() {
  try {
    loadingKeys.value = true
    const userId = authStore.user?.id
    if (userId) {
      const keys = await getUserAPIKeys(userId)
      apiKeys.value = keys
    }
  } catch (error) {
    console.error('获取 API Keys 失败:', error)
  } finally {
    loadingKeys.value = false
  }
}

// 创建 API Key
function handleCreateAPIKey() {
  createKeyForm.name = ''
  createKeyForm.permissions = 'predict,history'
  createKeyForm.expires_in_days = 90
  createKeyDialogVisible.value = true
}

// 确认创建 API Key
async function handleConfirmCreateKey() {
  if (!createKeyFormRef.value) return

  try {
    await createKeyFormRef.value.validate()
    creatingKey.value = true

    const response = await createAPIKey({
      name: createKeyForm.name,
      permissions: createKeyForm.permissions,
      expires_in_days: createKeyForm.expires_in_days,
    })

    ElMessage.success(`API Key 创建成功：${response.api_key}`)
    createKeyDialogVisible.value = false

    // 刷新列表
    await fetchAPIKeys()
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    creatingKey.value = false
  }
}

// 撤销 Key
async function handleRevokeKey(keyId: number) {
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
    await fetchAPIKeys()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('撤销失败')
    }
  } finally {
    revokingKey.value = null
  }
}

// 初始化
onMounted(() => {
  // 填充用户信息
  const user = authStore.user
  if (user) {
    profileForm.username = user.username
    profileForm.nickname = user.nickname || ''
    profileForm.email = user.email || ''
    profileForm.phone = user.phone || ''
  }

  // 获取 API Keys
  fetchAPIKeys()
})
</script>

<style scoped lang="scss">
.profile-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.subtitle {
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.user-card {
  .user-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    text-align: center;

    .user-details {
      h2 {
        margin: 0 0 8px;
        font-size: 20px;
      }

      .user-meta {
        margin-top: 12px;
        display: flex;
        gap: 8px;
        justify-content: center;
      }
    }
  }
}

.password-card,
.profile-card,
.preferences-card,
.api-keys-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }

    .header-icon {
      font-size: 18px;
    }
  }
}

.profile-card,
.preferences-card {
  .form-tip {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.preferences-card {
  .el-form-item {
    margin-bottom: 24px;
  }
}

.api-keys-card {
  .form-tip {
    margin-top: 4px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
</style>
