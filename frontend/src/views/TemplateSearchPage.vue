<template>
  <div class="template-search-page">
    <TopNavBar />

    <main class="search-container">
      <section class="search-panel">
        <div class="search-row">
          <input
            v-model="keyword"
            type="text"
            placeholder="输入关键词，例如：租赁、股权、劳动、转让"
            @keyup.enter="handleSearch"
          />
          <button class="btn-glow" :disabled="loading" @click="handleSearch">
            {{ loading ? '搜索中...' : '搜索模板' }}
          </button>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-head">
          <h3>搜索结果</h3>
          <span v-if="totalPages > 1">{{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, results.length) }} / {{ results.length }} 条</span>
          <span v-else>{{ results.length }} 条</span>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>
        <p v-else-if="!loading && results.length === 0" class="empty-text">暂无结果，请更换关键词再试。</p>

        <div v-else class="result-list">
          <article v-for="item in paginatedResults" :key="item.id" class="result-item">
            <div class="item-main">
              <p class="file-name">{{ item.fileName }}</p>
              <p class="file-path">{{ item.relativePath }}</p>
            </div>
            <div class="item-side">
              <span class="file-ext">{{ item.ext || 'unknown' }}</span>
              <span class="file-size">{{ formatSize(item.size) }}</span>
              <div class="item-actions">
                <button class="mini-btn" @click="openPreview(item)">查看</button>
                <button class="mini-btn" @click="downloadTemplate(item)">下载</button>
              </div>
            </div>
          </article>
        </div>

        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">上一页</button>
          <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">下一页</button>
        </div>
      </section>

      <section v-if="previewVisible" class="preview-mask" @click.self="closePreview">
        <div class="preview-panel" role="dialog" aria-modal="true" aria-label="模板预览">
          <div class="preview-head">
            <h3>模板预览：{{ previewTitle }}</h3>
            <button class="action-btn" @click="closePreview">关闭</button>
          </div>

          <p v-if="previewHint" class="empty-text">{{ previewHint }}</p>

          <p v-if="previewError" class="error-text">{{ previewError }}</p>
          <p v-else-if="previewLoading" class="empty-text">预览加载中，请稍候...</p>

          <iframe
            v-if="previewMode === 'pdf' && !previewError"
            :src="previewPdfUrl"
            class="preview-iframe"
            frameborder="0"
            title="模板PDF预览"
            @load="handlePdfLoaded"
            @error="handlePdfError"
          ></iframe>
          <pre v-else-if="!previewError" class="preview-content">{{ previewContent }}</pre>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import TopNavBar from '@/components/TopNavBar.vue'
import { templateApi } from '@/api'

type TemplateItem = {
  id: string
  fileName: string
  relativePath: string
  ext: string
  size: number
  previewable: boolean
}

const keyword = ref('合同')
const loading = ref(false)
const error = ref('')
const results = ref<TemplateItem[]>([])
const currentPage = ref(1)
const pageSize = 10
const previewVisible = ref(false)
const previewTitle = ref('')
const previewContent = ref('')
const previewPdfUrl = ref('')
const previewMode = ref<'text' | 'pdf'>('text')
const previewLoading = ref(false)
const previewError = ref('')
const previewHint = ref('')

const totalPages = computed(() => Math.ceil(results.value.length / pageSize))
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return results.value.slice(start, start + pageSize)
})

watch(results, () => {
  currentPage.value = 1
})

const shouldUsePdfPreview = (ext: string) => {
  const normalized = (ext || '').toLowerCase()
  return normalized === 'pdf' || normalized === 'doc' || normalized === 'docx' || normalized === 'wps'
}

const isOfficeExt = (ext: string) => {
  const normalized = (ext || '').toLowerCase()
  return normalized === 'doc' || normalized === 'docx' || normalized === 'wps'
}

const prewarmOfficePreviews = async (items: TemplateItem[]) => {
  const ids = items
    .filter((item) => isOfficeExt(item.ext))
    .slice(0, 12)
    .map((item) => item.id)

  if (ids.length === 0) {
    return
  }

  try {
    await templateApi.prewarm({
      ids,
      limit: ids.length
    })
  } catch (_e) {
    // 预热失败不影响页面主流程
  }
}

const handleSearch = async () => {
  const key = keyword.value.trim()
  if (!key) {
    error.value = '请输入关键词后再搜索'
    return
  }

  error.value = ''
  loading.value = true
  try {
    const res: any = await templateApi.search({
      keyword: key
    })

    if (res.code === 200) {
      results.value = Array.isArray(res.data) ? res.data : []
      void prewarmOfficePreviews(results.value)
    } else {
      error.value = res.message || '搜索失败'
      results.value = []
    }
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || '搜索失败，请稍后重试'
    results.value = []
  } finally {
    loading.value = false
  }
}

const openPreview = async (item: TemplateItem) => {
  previewVisible.value = true
  previewTitle.value = item.fileName
  error.value = ''
  previewError.value = ''
  previewHint.value = ''
  previewLoading.value = true

  if (shouldUsePdfPreview(item.ext)) {
    const pdfUrl = templateApi.pdfPreviewUrl(item.id)

    if (isOfficeExt(item.ext)) {
      try {
        const probeUrl = `${pdfUrl}?probe=1&t=${Date.now()}`
        const response = await fetch(probeUrl, { method: 'GET' })
        const contentType = response.headers.get('content-type') || ''
        if (!response.ok || !contentType.includes('application/pdf')) {
          throw new Error('office-pdf-unavailable')
        }

        previewMode.value = 'pdf'
        previewContent.value = ''
        previewPdfUrl.value = `${pdfUrl}?t=${Date.now()}`
        return
      } catch (_e) {
        previewHint.value = '当前环境未启用Office保真预览，已自动切换为文本预览。'
      }
    } else {
      previewMode.value = 'pdf'
      previewContent.value = ''
      previewPdfUrl.value = `${pdfUrl}?t=${Date.now()}`
      return
    }
  }

  await loadTextPreview(item)
}

const loadTextPreview = async (item: TemplateItem) => {
  previewMode.value = 'text'
  previewPdfUrl.value = ''
  previewContent.value = '加载预览中...'

  try {
    const res: any = await templateApi.preview(item.id)
    if (res.code === 200) {
      previewContent.value = res.data?.content || '暂无预览内容'
    } else {
      previewError.value = res.message || '预览失败'
    }
  } catch (e: any) {
    previewError.value = e?.response?.data?.message || e?.message || '预览失败'
  } finally {
    previewLoading.value = false
  }
}

const handlePdfLoaded = () => {
  previewLoading.value = false
}

const handlePdfError = () => {
  previewLoading.value = false
  previewError.value = 'PDF预览加载失败，请尝试下载查看。'
}

const closePreview = () => {
  previewVisible.value = false
  previewPdfUrl.value = ''
  previewLoading.value = false
  previewError.value = ''
  previewHint.value = ''
}

const onEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && previewVisible.value) {
    closePreview()
  }
}

const downloadTemplate = (item: TemplateItem) => {
  window.open(templateApi.downloadUrl(item.id), '_blank')
}

const formatSize = (size: number) => {
  if (!size || size <= 0) return '0 B'
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

onMounted(async () => {
  window.addEventListener('keydown', onEscKey)
  await handleSearch()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onEscKey)
})
</script>

<style scoped>
.template-search-page {
  min-height: 100vh;
  color: #eef4fc;
  background:
    linear-gradient(120deg, rgba(181, 141, 69, 0.14), rgba(181, 141, 69, 0) 38%),
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
}

.search-container {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1rem 2rem;
}

.search-panel,
.result-panel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 1rem;
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
}

/* 已往中间缩进 2 个中文字 */
.search-panel {
  padding: 1.2rem 2.4rem;
  margin-bottom: 1rem;
}
.result-panel {
  padding: 1.2rem 2.4rem;
}

.search-row {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.search-row input {
  flex: 1;
  padding: 0.8rem 1.2rem 0.8rem 2.4rem;
  border-radius: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(5, 21, 38, 0.45);
  color: #eef4fc;
}

.search-row input:focus {
  outline: none;
  border-color: rgba(222, 193, 136, 0.82);
}

.btn-glow {
  background: linear-gradient(135deg, #b58d45, #d9b876);
  color: #061526;
  border: none;
  border-radius: 0.8rem;
  font-weight: 600;
  padding: 0.8rem 2.25rem;
  box-shadow: 0 4px 15px rgba(181, 141, 69, 0.3);
  transition: all 0.3s;
  cursor: pointer;
  white-space: nowrap;
}

.btn-glow:hover {
  box-shadow: 0 4px 25px rgba(181, 141, 69, 0.6);
  transform: translateY(-2px);
}

.btn-glow:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-btn {
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #eef4fc;
  padding: 0.45rem 0.9rem;
  cursor: pointer;
}

.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.result-head h3 {
  margin: 0;
  color: #f5e3bb;
}

.result-list {
  display: grid;
  gap: 0.65rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 2.4rem;
  border-radius: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.03);
}

.item-main {
  min-width: 0;
}

.file-name {
  margin: 0 0 0.3rem;
  font-weight: 600;
  font-size: 1.4rem;
  color: #eef4fc;
}

.file-path {
  margin: 0;
  font-size: 0.88rem;
  color: rgba(238, 244, 252, 0.7);
  word-break: break-all;
}

.item-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 86px;
  gap: 0.3rem;
}

.item-actions {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.35rem;
}

.mini-btn {
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #eef4fc;
  padding: 0.2rem 0.65rem;
  cursor: pointer;
}

.file-ext,
.file-size {
  font-size: 0.8rem;
  color: rgba(238, 244, 252, 0.72);
}

.preview-mask {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(5, 16, 30, 0.58);
  backdrop-filter: blur(2px);
}

.preview-panel {
  width: min(1100px, 100%);
  max-height: 90vh;
  overflow: auto;
  padding: 1.2rem;
  background: rgba(19, 42, 66, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 1rem;
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.42);
}

.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.preview-head h3 {
  margin: 0;
  color: #f5e3bb;
}

.preview-content {
  margin-top: 0.9rem;
  padding: 1rem;
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(238, 244, 252, 0.9);
  max-height: 65vh;
  overflow: auto;
}

.preview-iframe {
  width: 100%;
  height: 72vh;
  margin-top: 0.9rem;
  border-radius: 0.8rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.empty-text {
  color: rgba(238, 244, 252, 0.74);
}

.error-text {
  color: #f2b6b6;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.page-btn {
  border: 1px solid rgba(255, 255, 255, 0.26);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #eef4fc;
  padding: 0.4rem 1rem;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: rgba(255, 255, 255, 0.12);
}

.page-info {
  color: rgba(238, 244, 252, 0.8);
  font-size: 0.9rem;
}

@media (max-width: 720px) {
  .search-row {
    grid-template-columns: 1fr;
  }

  .result-item {
    flex-direction: column;
  }

  .item-side {
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
  }
}
</style>