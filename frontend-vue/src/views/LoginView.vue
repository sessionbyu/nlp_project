<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🤖</div>
        <h1>NLP 预测平台</h1>
        <p class="subtitle">用户登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.rememberMe">记住我</el-checkbox>
          <el-link type="primary" underline="never" class="forgot-link">
            忘记密码？
          </el-link>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p class="tips">
          <el-icon><InfoFilled /></el-icon>
          演示账号：admin / admin123
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, InfoFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()

console.log('[LoginView] 组件挂载')
console.log('[LoginView] 当前路径:', router.currentRoute.value.path)
console.log('[LoginView] isAuthenticated:', authStore.isAuthenticated)

const form = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

const loading = ref(false)

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await authStore.login({
        username: form.username,
        password: form.password,
        rememberMe: form.rememberMe,
      })

      ElMessage.success('登录成功')

      // 等待状态更新
      await new Promise(resolve => setTimeout(resolve, 100))

      console.log('[Login] 登录后 store 状态:', {
        isAuthenticated: authStore.isAuthenticated,
        token: authStore.token ? 'exists' : 'null',
        userInfo: authStore.userInfo?.username || 'null'
      })

      // 跳转到预测页或之前的页面
      let redirect = router.currentRoute.value.query.redirect as string

      // 如果 redirect 是根路径 "/"，直接跳转到 /predict（避免循环重定向）
      if (redirect === '/') {
        redirect = '/predict'
      }

      const targetPath = redirect || '/predict'

      console.log('[Login] 即将跳转到:', targetPath)

      // 使用 router.push 进行 SPA 路由跳转
      await router.push(targetPath)
    } catch (error: any) {
      console.error('[Login] 登录失败:', error)
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #5B9A8B 0%, #4A8B7A 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;

  .login-header {
    text-align: center;
    margin-bottom: 32px;

    .logo {
      font-size: 64px;
      margin-bottom: 16px;
    }

    h1 {
      font-size: 24px;
      font-weight: 700;
      color: #2C3E50;
      margin: 0 0 8px 0;
    }

    .subtitle {
      font-size: 14px;
      color: #8A98A8;
      margin: 0;
    }
  }

  .forgot-link {
    float: right;
    font-size: 14px;
  }

  .login-footer {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #DCE1E6;

    .tips {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 13px;
      color: #8A98A8;
      margin: 0;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }

  .login-card {
    padding: 24px;
  }
}
</style>
