<template>
  <div class="case-search-page">
    <TopNavBar />

    <main class="search-container">
      <div class="search-bar">
        <div class="search-input-group">
          <input
            v-model="keyword"
            type="text"
            placeholder="输入关键词搜索案例..."
            @keyup.enter="handleSearch(1)"
          />
          <select v-model="caseType">
            <option value="">全部类型</option>
            <option value="劳动争议">劳动争议</option>
            <option value="合同纠纷">合同纠纷</option>
            <option value="侵权责任">侵权责任</option>
            <option value="婚姻家庭">婚姻家庭</option>
            <option value="刑事案件">刑事案件</option>
          </select>
          <button @click="handleSearch(1)" class="btn-glow">搜索</button>
          <button @click="showAddModal = true" class="btn-outline">添加案例</button>
        </div>
      </div>

      <div class="results-container">
        <div v-if="loading" class="loading">加载中...</div>
        <div v-else-if="results.length === 0" class="empty">
          <p>暂无相关案例</p>
          <p class="hint">尝试更换关键词或筛选条件</p>
        </div>
        <div v-else class="case-list">
          <div v-for="item in results" :key="item.id" class="case-card">
            <div class="case-header">
              <h3>{{ item.caseTitle }}</h3>
              <span class="case-type">{{ item.caseType }}</span>
            </div>
            <div class="case-meta">
              <span v-if="item.caseDate">时间：{{ item.caseDate }}</span>
              <span v-if="item.caseRegion">地域：{{ item.caseRegion }}</span>
              <span v-if="item.court">法院：{{ item.court }}</span>
            </div>
             <div class="case-laws" v-if="item.citedLaws && item.citedLaws.length">
              <strong>引用法条：</strong>
              <span v-for="(law, idx) in item.citedLaws" :key="idx" class="law-tag">{{ law }}</span>
            </div>
            <div class="case-summary">{{ item.caseSummary }}</div>
            <div class="case-footer">
              <span class="judgment-result" :class="getResultClass(item.judgmentResult)">
                {{ item.judgmentResult }}
              </span>
            </div>
             <div class="case-key-points" v-if="item.judgmentReason">
              <strong>判决理由：</strong>{{ item.judgmentReason }}
            </div>
            <div class="case-key-points">
              <strong>关键要点：</strong>{{ item.keyPoints }}
            </div>
            <div class="case-text-preview" v-if="item.caseText">
              <details>
                <summary>查看案例全文</summary>
                <p>{{ item.caseText }}</p>
              </details>
            </div>
          </div>
        </div>

        <div v-if="totalPages > 1" class="pagination">
          <button class="page-btn" :disabled="currentPage === 1" @click="handleSearch(currentPage - 1)">
            上一页
          </button>

          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn page-number"
            :class="{ active: page === currentPage }"
            @click="handleSearch(page)"
          >
            {{ page }}
          </button>

          <button class="page-btn" :disabled="currentPage === totalPages" @click="handleSearch(currentPage + 1)">
            下一页
          </button>

          <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页，共 {{ total }} 条</span>
        </div>
      </div>
    </main>

    <!-- 自定义提示弹窗 -->
    <div v-if="toast.show" class="toast-message" :class="toast.type">
      {{ toast.message }}
    </div>

    <!-- 添加案例弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content scrollable">
        <h2>添加案例</h2>
        <div class="form-group">
          <label>案件名称</label>
          <input v-model="addForm.caseTitle" type="text" placeholder="填入案件名称" />
        </div>
        <div class="form-group-row">
          <div class="form-group half-width">
            <label>案例类型</label>
            <select v-model="addForm.caseType">
              <option value="劳动争议">劳动争议</option>
              <option value="合同纠纷">合同纠纷</option>
              <option value="侵权责任">侵权责任</option>
              <option value="婚姻家庭">婚姻家庭</option>
              <option value="刑事案件">刑事案件</option>
            </select>
          </div>
          <div class="form-group half-width">
            <label>案件发生时间</label>
            <input v-model="addForm.caseDate" type="date" />
          </div>
        </div>
        <div class="form-group-row">
          <div class="form-group half-width">
            <label>案件发生地域</label>
            <input v-model="addForm.caseRegion" type="text" placeholder="例如：北京市海淀区" />
          </div>
          <div class="form-group half-width">
            <label>审理法院</label>
            <input v-model="addForm.court" type="text" placeholder="例如：北京市海淀区人民法院" />
          </div>
        </div>
        <div class="form-group">
          <label>引用法条 (用逗号分隔)</label>
          <input v-model="addForm.citedLawsInput" type="text" placeholder="例如：民法典第一百二十三条, ..." />
        </div>
        <div class="form-group">
          <label>案例摘要</label>
          <textarea v-model="addForm.caseSummary" placeholder="填入案例摘要"></textarea>
        </div>
        <div class="form-group">
          <label>关键要点</label>
          <textarea v-model="addForm.keyPoints" placeholder="填入案件关键要点"></textarea>
        </div>
        <div class="form-group">
          <label>判决结果</label>
          <input v-model="addForm.judgmentResult" type="text" placeholder="填入判决结果" />
        </div>
        <div class="form-group">
          <label>判决理由</label>
          <textarea v-model="addForm.judgmentReason" placeholder="填入判决理由"></textarea>
        </div>
        <div class="form-group">
          <label>案例全文</label>
          <textarea v-model="addForm.caseText" placeholder="填入案例全文" rows="5"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn-oval btn-cancel" @click="showAddModal = false">取消</button>
          <button class="btn-oval btn-confirm" @click="handleAdd" :disabled="submitting">
            {{ submitting ? '提交中...' : '确定添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { caseApi } from '../api'
import TopNavBar from '../components/TopNavBar.vue'

const keyword = ref('')
const caseType = ref('')
const results = ref<any[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = 8
const total = ref(0)

const showAddModal = ref(false)
const submitting = ref(false)
const toast = ref({ show: false, message: '', type: 'info' })

const showToast = (message: string, type = 'info') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const addForm = ref({
  caseTitle: '',
  caseType: '劳动争议',
  caseDate: '',
  caseRegion: '',
  court: '',
  citedLawsInput: '',
  keyPoints: '',
  caseSummary: '',
  judgmentResult: '',
  judgmentReason: '',
  caseText: ''
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + maxVisible - 1)
  const adjustedStart = Math.max(1, end - maxVisible + 1)

  for (let page = adjustedStart; page <= end; page += 1) {
    pages.push(page)
  }

  return pages
})

const handleAdd = async () => {
  if (!addForm.value.caseTitle || !addForm.value.caseType || !addForm.value.keyPoints || !addForm.value.caseSummary || !addForm.value.judgmentResult) {
    showToast('请填写必填字段(案件名称,类型,要点,摘要,判决结果)！', 'warning')
    return
  }

  if (addForm.value.judgmentResult.length > 100) {
    showToast('添加失败：判决结果不能超过100个字', 'error')
    return
  }
  
  if (addForm.value.caseTitle.length > 200) {
    showToast('添加失败：案件名称不能超过200个字', 'error')
    return
  }

  let citedLawsArray: string[] = []
  if (addForm.value.citedLawsInput) {
    citedLawsArray = addForm.value.citedLawsInput.split(/[,，]/).map((item: string) => item.trim()).filter((i: string) => i)
  }

  const submitData = {
    ...addForm.value,
    citedLaws: citedLawsArray,
    caseDate: addForm.value.caseDate || null
  }

  submitting.value = true
  try {
    const res: any = await caseApi.add(submitData)
    if (res.code === 200) {
      showToast('添加成功！', 'success')
      showAddModal.value = false
      addForm.value = {
        caseTitle: '',
        caseType: '劳动争议',
        caseDate: '',
        caseRegion: '',
        court: '',
        citedLawsInput: '',
        keyPoints: '',
        caseSummary: '',
        judgmentResult: '',
        judgmentReason: '',
        caseText: ''
      }
      handleSearch(1)
    } else {
      showToast('添加失败: ' + res.message, 'error')
    }
  } catch (e: any) {
    showToast('添加失败: ' + (e.response?.data?.message || e.message), 'error')
    console.error('Add case failed', e)
  } finally {
    submitting.value = false
  }
}

const handleSearch = async (page = currentPage.value) => {
  currentPage.value = page
  loading.value = true
  try {
    const res: any = await caseApi.search({
      keyword: keyword.value,
      caseType: caseType.value,
      page: currentPage.value,
      size: pageSize
    })
    if (res.code === 200) {
      results.value = res.data?.items || []
      total.value = res.data?.total || 0
      currentPage.value = res.data?.page || currentPage.value
    }
  } catch (e) {
    console.error('Search failed', e)
  } finally {
    loading.value = false
  }
}

const getResultClass = (result: string) => {
  if (result?.includes('胜诉')) return 'success'
  if (result?.includes('败诉')) return 'error'
  return 'info'
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.case-search-page {
  min-height: 100vh;
  color: #eef4fc;
  background:
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
}

.search-container {
  max-width: 900px;
  margin: 2.2rem auto;
  padding: 0 1rem;
}

.search-bar {
  background: rgba(255, 255, 255, 0.03);
  padding: 1.5rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
}

.search-input-group {
  display: flex;
  gap: 1rem;
}

.search-input-group input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  font-size: 1rem;
  color: #eef4fc;
  background: rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
}
.search-input-group input:focus {
  border-color: #b58d45;
  outline: none;
  box-shadow: 0 0 0 2px rgba(181, 141, 69, 0.2);
}

.search-input-group select {
  padding: 0.8rem 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  font-size: 1rem;
  min-width: 150px;
  color: #eef4fc;
  background: rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  cursor: pointer;
}
.search-input-group select:focus {
  border-color: #b58d45;
  outline: none;
}

.search-input-group button {
  padding: 0.8rem 2rem;
  border-radius: 999px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-glow {
  background: linear-gradient(135deg, #b58d45, #d9b876);
  color: #061526;
  border: none;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(181, 141, 69, 0.3);
  transition: all 0.3s;
}
.btn-glow:hover {
  box-shadow: 0 4px 25px rgba(181, 141, 69, 0.6);
  transform: translateY(-2px);
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: rgba(238, 244, 252, 0.74);
}

.hint {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.case-card {
  background: rgba(255, 255, 255, 0.03);
  padding: 2rem;
  border-radius: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.case-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  border-color: rgba(181, 141, 69, 0.3);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.case-header h3 {
  font-size: 1.25rem;
  color: #f5e3bb;
  flex: 1;
  line-height: 1.4;
  margin: 0;
}

.case-type {
  background: linear-gradient(135deg, rgba(181, 141, 69, 0.2), rgba(217, 184, 118, 0.1));
  border: 1px solid rgba(181, 141, 69, 0.3);
  color: #f5e3bb;
  padding: 0.3rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.case-summary {
  color: rgba(238, 244, 252, 0.85);
  line-height: 1.7;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.case-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.85rem;
  color: rgba(238, 244, 252, 0.5);
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
}

.case-laws {
  font-size: 0.85rem;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.law-tag {
  background: rgba(181, 141, 69, 0.08);
  border: 1px solid rgba(181, 141, 69, 0.25);
  color: #d9b876;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  transition: all 0.3s;
}

.law-tag:hover {
  background: rgba(181, 141, 69, 0.15);
}

.case-text-preview {
  margin-top: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  padding: 1.2rem;
  border-radius: 0.75rem;
  color: rgba(238, 244, 252, 0.85);
  font-size: 0.9rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.case-text-preview summary {
  cursor: pointer;
  color: #d9b876;
  font-weight: 600;
  outline: none;
  user-select: none;
  transition: color 0.3s;
}

.case-text-preview summary:hover {
  color: #f5e3bb;
}

.case-text-preview p {
  margin-top: 1rem;
  line-height: 1.8;
  white-space: pre-wrap;
}

.case-footer {
  margin-bottom: 1.5rem;
}

.judgment-result {
  display: inline-block;
  padding: 0.4rem 1.2rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.judgment-result.success {
  background: rgba(88, 176, 126, 0.15);
  color: #b9ebd7;
  border-color: rgba(88, 176, 126, 0.3);
}

.judgment-result.error {
  background: rgba(200, 80, 80, 0.15);
  color: #f2b6b6;
  border-color: rgba(200, 80, 80, 0.3);
}

.judgment-result.info {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(238, 244, 252, 0.85);
  border-color: rgba(255, 255, 255, 0.15);
}

.case-key-points {
  background: rgba(255, 255, 255, 0.03);
  border-left: 3px solid #b58d45;
  padding: 1rem 1.2rem;
  border-radius: 0 0.75rem 0.75rem 0;
  font-size: 0.95rem;
  color: rgba(238, 244, 252, 0.9);
  line-height: 1.6;
  margin-bottom: 1rem;
}

@media (max-width: 860px) {
  .search-input-group {
    flex-direction: column;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: linear-gradient(145deg, #0a1f33 0%, #15314f 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 1rem;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  color: #fff;
}

.modal-content.scrollable {
  max-height: 85vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 1.5rem;
  color: #f5e3bb;
}

.form-group-row {
  display: flex;
  gap: 1rem;
}
.half-width {
  flex: 1;
}

.form-group {
  margin-bottom: 0.8rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.9rem;
  color: rgba(238, 244, 252, 0.8);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 8px;
  font-size: 1rem;
  color: #eef4fc;
  background: rgba(5, 21, 38, 0.45);
  outline: none;
  font-family: inherit;
}

.form-group textarea {
  min-height: 60px;
  resize: vertical;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #b58d45;
  box-shadow: 0 0 0 2px rgba(181, 141, 69, 0.2);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-outline {
  padding: 0.8rem 2rem;
  border-radius: 999px;
  font-size: 1rem;
  background: transparent;
  color: #f5e3bb;
  border: 1px solid rgba(181, 141, 69, 0.6);
  cursor: pointer;
  transition: all 0.3s;
}
.btn-outline:hover {
  background: rgba(181, 141, 69, 0.1);
  border-color: #f5e3bb;
}

.btn-oval {
  padding: 0.8rem 2rem;
  border-radius: 999px; /* 使按钮成为椭圆形 */
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  outline: none;
}

.btn-oval.btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(238, 244, 252, 0.8);
}
.btn-oval.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.4);
}

.btn-oval.btn-confirm {
  background: linear-gradient(135deg, #b58d45, #d9b876);
  border: none;
  color: #061526;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(181, 141, 69, 0.3);
}
.btn-oval.btn-confirm:hover {
  box-shadow: 0 4px 20px rgba(181, 141, 69, 0.6);
  transform: translateY(-1px);
}
.btn-oval.btn-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.toast-message {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  color: #fff;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: slideDown 0.3s ease-out;
}

.toast-message.success {
  background: rgba(88, 176, 126, 0.9);
  border: 1px solid rgba(88, 176, 126, 1);
}

.toast-message.error {
  background: rgba(200, 80, 80, 0.9);
  border: 1px solid rgba(200, 80, 80, 1);
}

.toast-message.warning {
  background: rgba(200, 150, 40, 0.9);
  border: 1px solid rgba(200, 150, 40, 1);
}

.toast-message.info {
  background: rgba(30, 80, 150, 0.9);
  border: 1px solid rgba(30, 80, 150, 1);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.page-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(238, 244, 252, 0.7);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: rgba(181, 141, 69, 0.15);
  border-color: rgba(181, 141, 69, 0.4);
  color: #f5e3bb;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-number.active {
  background: #b58d45;
  color: #061526;
  border-color: #b58d45;
  font-weight: 600;
  box-shadow: 0 2px 10px rgba(181, 141, 69, 0.3);
}

.page-info {
  font-size: 0.9rem;
  color: rgba(238, 244, 252, 0.6);
  margin-left: 1rem;
}

@keyframes slideDown {
  from {
    top: 40px;
    opacity: 0;
  }
  to {
    top: 80px;
    opacity: 1;
  }
}
</style>
