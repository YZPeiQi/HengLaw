<template>
  <header class="page-header">
    <button v-if="showBack" @click="$router.push('/')" class="back-btn">← 返回首页</button>
    <h1>{{ title }}</h1>
    <div class="header-actions">
      <slot />
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  showBack?: boolean
}>()
</script>

<style scoped>
.page-header {
  padding: 1rem clamp(1rem, 3vw, 2.5rem);
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  margin-bottom: 1.5rem;
}

.page-header h1 {
  flex: 1;
  font-size: clamp(1.3rem, 2.3vw, 1.8rem);
  color: #f5e3bb;
  font-family: 'Cormorant Garamond', Georgia, serif;
}

.back-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.26);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  color: #eef4fc;
  transition: all 0.22s ease;
  font-size: 0.9rem;
}

.back-btn:hover {
  border-color: rgba(222, 193, 136, 0.85);
  color: #f5e3bb;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

@media (max-width: 640px) {
  .page-header {
    flex-wrap: wrap;
  }
}
</style>
