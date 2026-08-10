<template>
  <div class="login-page">
    <div class="login-container">
      <h2>登录 法研智谱</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" required />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="submit-btn btn-glow" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <div class="form-footer">
          <router-link to="/register">还没有账号？立即注册</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const res: any = await authApi.login(form.value)
    if (res.code === 200) {
      authStore.setAuth(res.data.token, res.data.username)
      router.push('/')
    } else {
      error.value = res.message || '登录失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  color: #eef4fc;
  background:
    linear-gradient(120deg, rgba(181, 141, 69, 0.14), rgba(181, 141, 69, 0) 38%),
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
}

.login-container {
  background: rgba(255, 255, 255, 0.04);
  padding: 2.5rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.16);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  width: 100%;
  max-width: 400px;
}

.login-container h2 {
  text-align: center;
  color: #f5e3bb;
  font-family: 'Cormorant Garamond', Georgia, serif;
  letter-spacing: 0.04rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: rgba(238, 244, 252, 0.88);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.7rem;
  font-size: 1rem;
  color: #eef4fc;
  background: rgba(5, 21, 38, 0.45);
  transition: border-color 0.2s, background 0.2s;
}

.form-group input::placeholder {
  color: rgba(238, 244, 252, 0.5);
}

.form-group input:focus {
  outline: none;
  border-color: rgba(222, 193, 136, 0.82);
  background: rgba(5, 21, 38, 0.65);
}

.error-message {
  color: #f2b6b6;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  border-radius: 999px;
  font-size: 1.1rem;
  letter-spacing: 2px;
  margin-top: 1rem;
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.form-footer a {
  color: #dec188;
}

.form-footer a:hover {
  color: #f5e3bb;
}
</style>
