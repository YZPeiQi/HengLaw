<template>
  <header class="topbar">
    <div class="brand-wrap">
      <router-link to="/" class="brand-link">
        <span class="brand-icon-wrap">
          <img class="brand-icon" src="/brand/logo-transparent.png" alt="法研智谱天平标志" />
        </span>
        <div class="brand-text">
          <p class="brand-cn">法研智谱</p>
          <h1 class="brand-en">LawIntelEmpower</h1>
        </div>
      </router-link>
    </div>
    <nav class="top-nav">
      <router-link to="/" exact>首页</router-link>
      <router-link to="/consultation">咨询</router-link>
      <router-link to="/case-search">案例</router-link>
      <router-link to="/template-search">合同模板</router-link>
      <router-link to="/contract-review">合同审查</router-link>
      <router-link to="/document-generate">文书生成</router-link>
    </nav>
    <div class="session-actions">
      <router-link v-if="isLoggedIn" to="/profile" class="profile-link">{{ username }}</router-link>
      <button v-if="isLoggedIn" @click="handleLogout" class="session-btn ghost">退出</button>
      <router-link v-else to="/login" class="session-btn">登录 / 注册</router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isAuthenticated())
const username = computed(() => authStore.username)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem clamp(1rem, 3vw, 3rem);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  background: rgba(10, 15, 26, 0.45);
}

.brand-wrap {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: stretch;
  gap: 0.6rem;
  text-decoration: none;
}

.brand-icon-wrap {
  display: flex;
  align-items: center;
  align-self: stretch;
}

.brand-icon {
  width: auto;
  height: 100%;
  display: block;
  flex: 0 0 auto;
  object-fit: contain;
  max-height: 3.9rem;
}

.brand-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.12rem;
}

.brand-cn {
  margin: 0;
  color: rgba(238, 244, 252, 0.72);
  font-size: 0.8rem;
  letter-spacing: 0.32rem;
}

.brand-en {
  margin: 0;
  font-family: 'Cormorant Garamond', Georgia, serif;
  letter-spacing: 0.08rem;
  font-size: clamp(1.05rem, 1.3vw, 1.3rem);
  color: #eef4fc;
}

.top-nav {
  display: flex;
  justify-content: center;
  gap: clamp(0.8rem, 2vw, 1.5rem);
  flex-wrap: wrap;
}

.top-nav a {
  color: rgba(238, 244, 252, 0.88);
  font-size: 0.95rem;
  letter-spacing: 0.05rem;
  text-transform: uppercase;
  text-decoration: none;
}

.top-nav a:hover,
.top-nav a.router-link-active {
  color: #dec188;
}

.top-nav a.router-link-active {
  border-bottom: 1px solid #dec188;
  padding-bottom: 2px;
}

.session-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.75rem;
}

.profile-link {
  color: #dec188;
  font-weight: 600;
  text-decoration: none;
}

.session-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.2rem;
  border-radius: 999px;
  padding: 0 0.95rem;
  border: 1px solid rgba(222, 193, 136, 0.45);
  color: #f5e8ca;
  background: rgba(181, 141, 69, 0.15);
  transition: all 0.25s ease;
  text-decoration: none;
  font-size: 0.9rem;
  cursor: pointer;
}

.session-btn:hover {
  border-color: rgba(222, 193, 136, 0.9);
  background: rgba(181, 141, 69, 0.28);
}

.session-btn.ghost {
  background: transparent;
}

@media (max-width: 1080px) {
  .topbar {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
    gap: 0.8rem;
  }

  .session-actions {
    justify-content: center;
  }

  .brand-icon {
    max-height: 3.3rem;
  }
}
</style>
