<template>
  <div class="register-page">
    <div class="register-container">
      <h2>注册 法研智谱</h2>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" placeholder="请输入密码（至少6位）" required />
        </div>
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="form.email" type="email" placeholder="请输入邮箱（可选）" />
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        <button type="submit" class="submit-btn btn-glow" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        <div class="form-footer">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'

const router = useRouter()

const form = ref({
  username: '',
  password: '',
  email: ''
})
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const payload = {
      username: form.value.username.trim(),
      password: form.value.password,
      email: form.value.email.trim() || undefined
    }
    const res: any = await authApi.register(payload)
    if (res.code === 200) {
      success.value = '注册成功！正在跳转登录...'
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      error.value = res.message || '注册失败'
    }
  } catch (e: any) {
    error.value = e.response?.data?.message || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
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

.register-container {
  background: rgba(255, 255, 255, 0.04);
  padding: 2.5rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.16);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  width: 100%;
  max-width: 400px;
}

.register-container h2 {
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

.success-message {
  color: #b9ebd7;
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
