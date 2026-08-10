<template>
  <div class="profile-page">
    <TopNavBar />
    <PageHeader title="个人中心" show-back>
      <button @click="handleLogout" class="logout-btn btn-glow">退出登录</button>
    </PageHeader>

    <main class="profile-container">
      <div class="profile-card">
        <div class="avatar">{{ username?.charAt(0).toUpperCase() }}</div>
        <div class="user-info">
          <h2>{{ username }}</h2>
          <p>欢迎使用法研智谱法律智能体平台</p>
        </div>
      </div>

      <div class="menu-section">
        <h3>我的操作</h3>
        <div class="menu-list">
          <router-link to="/consultation" class="menu-item">
            <span class="menu-icon">💬</span>
            <span>法律咨询记录</span>
            <span class="arrow">→</span>
          </router-link>
          <router-link to="/contract-review" class="menu-item">
            <span class="menu-icon">📝</span>
            <span>合同审查记录</span>
            <span class="arrow">→</span>
          </router-link>
          <router-link to="/document-generate" class="menu-item">
            <span class="menu-icon">📄</span>
            <span>法律文书记录</span>
            <span class="arrow">→</span>
          </router-link>
        </div>
      </div>

      <div class="about-section">
        <h3>关于法研智谱</h3>
        <p>LawIntelEmpower 法研智谱法律智能体平台是一款基于人工智能的法律服务工具，为用户提供专业的法律咨询、案件分析、合同审查和法律文书生成服务。</p>
        <p class="version">版本 1.0.0</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import TopNavBar from '@/components/TopNavBar.vue'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = computed(() => authStore.username)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  color: #eef4fc;
  background:
    linear-gradient(120deg, rgba(181, 141, 69, 0.14), rgba(181, 141, 69, 0) 38%),
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
}

:deep(.logout-btn) {
  padding: 0.5rem 1rem;
}

:deep(.logout-btn:hover) {
}

.profile-container {
  max-width: 600px;
  margin: 2.2rem auto;
  padding: 0 1rem;
}

.profile-card {
  background: rgba(255, 255, 255, 0.05);
  padding: 2.5rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.avatar {
  width: 80px;
  height: 80px;
  background: rgba(181, 141, 69, 0.22);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
  color: #f5e3bb;
}

.user-info h2 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-family: 'Cormorant Garamond', Georgia, serif;
  color: #f5e3bb;
}

.user-info p {
  opacity: 0.85;
}

.menu-section, .about-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
  margin-bottom: 1.5rem;
}

.menu-section h3, .about-section h3 {
  font-size: 1.05rem;
  color: #f5e3bb;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}

.menu-list {
  display: flex;
  flex-direction: column;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(238, 244, 252, 0.92);
  text-decoration: none;
}

.menu-item:hover {
  color: #f5e3bb;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  font-size: 1.5rem;
  margin-right: 1rem;
}

.menu-item span:nth-child(2) {
  flex: 1;
}

.arrow {
  color: rgba(238, 244, 252, 0.66);
}

.about-section p {
  color: rgba(238, 244, 252, 0.8);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.version {
  color: rgba(238, 244, 252, 0.58);
  font-size: 0.85rem;
}

@media (max-width: 640px) {
  .profile-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
