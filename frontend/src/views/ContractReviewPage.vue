<template>
  <div class="contract-review-page">
    <TopNavBar />

    <main class="review-container">
      <div class="input-section">
        <div class="left-inner-wrapper" ref="leftInnerRef">
          <h2 class="section-title">合同审查</h2>

          <div class="form-row">
            <div class="form-group">
              <label>合同类型</label>
              <select v-model="form.contractType">
                <option value="">请选择</option>
                <option value="劳动合同">劳动合同</option>
                <option value="租赁合同">租赁合同</option>
                <option value="买卖合同">买卖合同</option>
                <option value="借款合同">借款合同</option>
                <option value="服务合同">服务合同</option>
                <option value="技术合同">技术合同</option>
                <option value="投资合同">投资合同</option>
                <option value="其他">其他</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>审查模式</label>
            <div class="mode-selector">
              <button
                :class="['mode-btn', { active: reviewMode === 'basic' }]"
                @click="reviewMode = 'basic'"
              >
                ⏱ 快速
              </button>
              <button
                :class="['mode-btn', { active: reviewMode === 'advanced' }]"
                @click="reviewMode = 'advanced'"
              >
                🔍 深度思考
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>上传合同文件</label>
            <div
              class="upload-area"
              :class="{ 'has-file': uploadedFile, 'dragover': isDragover }"
              @click="triggerFileInput"
              @dragover.prevent="isDragover = true"
              @dragleave="isDragover = false"
              @drop.prevent="handleDrop"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".pdf,.docx,.doc"
                @change="handleFileChange"
                style="display: none"
              />
              <div v-if="!uploadedFile" class="upload-placeholder">
                <div class="upload-icon">📄</div>
                <p class="upload-text">点击或拖拽上传文件</p>
                <p class="upload-hint">支持 .pdf、.docx、.doc 格式</p>
              </div>
              <div v-else class="file-info">
                <div class="file-icon">📋</div>
                <div class="file-details">
                  <p class="file-name">{{ uploadedFile.name }}</p>
                  <p class="file-size">{{ formatFileSize(uploadedFile.size) }}</p>
                </div>
                <button class="remove-btn" @click.stop="removeFile">✕</button>
              </div>
            </div>
          </div>

          <button
            @click="handleReview"
            class="submit-btn btn-glow"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? '审查中...' : '开始审查' }}
          </button>

          <div v-if="result && !loading" class="result-grid">
            <div class="info-card">
              <h3>📄 合同信息</h3>
              <div class="info-row">
                <span class="label">合同名称</span>
                <span class="value">{{ uploadedFileName || '暂无' }}</span>
              </div>
              <div class="info-row">
                <span class="label">合同类型</span>
                <span class="value">{{ form.contractType || '暂无' }}</span>
              </div>
              <div class="info-row">
                <span class="label">审查模式</span>
                <span class="value">{{ reviewMode === 'basic' ? '快速' : '深度思考' }}</span>
              </div>
            </div>

            <div class="result-card">
              <h3>✏️ 修改建议</h3>
              <div class="suggestion-content">
                <p>{{ result.modificationSuggestions || '暂无' }}</p>
              </div>
            </div>

            <div class="result-card">
              <h3>
                ⚖️ 法律效力判断
                <span class="effect-badge" :class="getEffectBadgeClass(result.legalEffect)">
                  {{ result.legalEffect?.isValid !== undefined ? (result.legalEffect.isValid ? '有效' : '存在效力瑕疵') : '待评估' }}
                </span>
              </h3>
              <div class="effect-analysis">
                <p>{{ result.legalEffect?.analysis || '暂无' }}</p>
              </div>
              <div class="risk-level" v-if="result.legalEffect?.riskLevel">
                <span class="level-label">风险等级：</span>
                <span class="level-value" :class="'level-' + result.legalEffect.riskLevel.toLowerCase()">
                  {{ result.legalEffect.riskLevel }}
                </span>
              </div>
            </div>

            <div class="result-card">
              <h3>📝 综合评估与建议</h3>
              <div class="summary-content">
                <p>{{ result.summary || '暂无' }}</p>
              </div>
            </div>

            <div v-if="leftPaddingTips.length > 0" class="result-card padding-card span-full mt-gap">
              <h3>📋 审查提示</h3>
              <div class="tips-content">
                <p v-for="(tip, index) in leftPaddingTips" :key="index">{{ tip }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="result-section">
        <div v-if="!result && !loading" class="empty-state">
          <div class="empty-icon">📋</div>
          <p>请在左侧填写合同信息<br/>开始智能审查</p>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>AI正在审查合同...</p>
        </div>

        <template v-if="result && !loading">
          <div v-if="rightPaddingTips.length > 0" class="result-card padding-card">
            <h3>📋 审查提示</h3>
            <div class="tips-content">
              <p v-for="(tip, index) in rightPaddingTips" :key="index">{{ tip }}</p>
            </div>
          </div>

          <div class="result-card risk-full-height">
            <h3>⚠️ 风险点审查</h3>
            <div class="risk-list-wrapper">
              <div class="risk-list" ref="riskListRef" v-if="result.riskPoints && result.riskPoints.length > 0">
                <div
                  v-for="(risk, index) in result.riskPoints"
                  :key="index"
                  class="risk-item"
                  :class="getBorderClass(risk.level)"
                >
                  <div class="risk-header">
                    <span class="risk-index">{{ Number(index) + 1 }}</span>
                    <span class="risk-clause">{{ risk.clause || '未明确条款' }}</span>
                  </div>
                  <div class="risk-level-tag" :class="getRiskTagClass(risk.level)" v-if="risk.level">
                    {{ risk.level }}
                  </div>
                  <div class="risk-content">
                    <div class="risk-desc" v-if="risk.risk">
                      <strong>风险描述：</strong>{{ risk.risk }}
                    </div>
                    <div class="risk-suggestion" v-if="risk.suggestion">
                      <strong>修改建议：</strong>{{ risk.suggestion }}
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-result" ref="riskListRef">
                <p>暂无风险点</p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { contractApi } from '@/api'
import TopNavBar from '@/components/TopNavBar.vue'

const form = ref({
  contractType: '',
  content: ''
})

const reviewMode = ref<'basic' | 'advanced'>('basic')
const result = ref<any>(null)
const loading = ref(false)
const isDragover = ref(false)
const uploadedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const fileLoading = ref(false)
const uploadedFileName = ref('')

// 高度计算相关 Refs
const leftInnerRef = ref<HTMLElement | null>(null)
const riskListRef = ref<HTMLElement | null>(null)

// 左右两边的提示语数据互相独立
const rightPaddingTips = ref<string[]>([])
const leftPaddingTips = ref<string[]>([])

// 审查提示语库
const tipMessages = [
  '• 建议仔细核对合同各项条款，确保无遗漏。',
  '• 重点关注违约责任和争议解决条款。',
  '• 确认合同履行期限、付款条件及对应时间节点。',
  '• 检查知识产权归属约定是否清晰明确。',
  '• 核实双方权利义务是否对等，防范霸王条款。',
  '• 注意保密条款和竞业限制的有效期限及范围。',
  '• 确认争议解决方式（诉讼或仲裁）及管辖地。',
  '• 检查违约金的设定是否在合理比例区间。',
  '• 核对发票开具时间和税务相关条款是否规范。',
  '• 确认不可抗力条款的适用范围及通知义务。',
  '• 检查合同变更、解除和终止的触发条件。',
  '• 核实签约主体的资质、授权代表身份及用印。',
  '• 检查合同附件的完整性，确保与主合同一致。',
  '• 确认合同份数、原件保存方式及归档要求。',
  '• 注意合同生效条件（如签字盖章后或特定日期）。',
  '• 如涉及外币，需确认汇率计算方式和结算标准。',
  '• 审核免责条款是否过度免除一方的法定义务。',
  '• 确认所有金额大写与小写是否完全一致。'
]

// 核心计算逻辑：精准判断高低差，智能补齐留白
/* AI辅助生成：通义灵码qwen3-coder，2026年4月14日 19：03 */
const calculateHeights = async () => {
  if (!result.value || loading.value) return

  // 1. 先清空所有动态提示，以此获取最原本的内容高度
  rightPaddingTips.value = []
  leftPaddingTips.value = []
  await nextTick()

  if (!leftInnerRef.value) return

  // 获取左侧基础内容的真实高度
  const leftNaturalHeight = leftInnerRef.value.offsetHeight
  let rightNaturalHeight = 0

  if (riskListRef.value) {
    // 加上右侧风险卡片自带的 padding 和 title 的近似高度 (≈80px)
    rightNaturalHeight = riskListRef.value.offsetHeight + 80
  }

  // 计算高度差
  const diff = leftNaturalHeight - rightNaturalHeight

  // 高度差大于 120px，说明左侧更长，把提示填在右上方
  if (diff > 120) {
    const textSpace = diff - 100 // 扣去提示卡片外壳高度
    let count = Math.floor(textSpace / 28) // 每行约 28px
    count = Math.max(1, Math.min(count, tipMessages.length))
    rightPaddingTips.value = tipMessages.slice(0, count)
  }
  // 高度差小于 -80px，说明右侧更长，把提示填在左侧 2x2 网格下方
  else if (diff < -80) {
    const textSpace = Math.abs(diff) - 80
    let count = Math.floor(textSpace / 28)
    count = Math.max(1, Math.min(count, tipMessages.length))
    leftPaddingTips.value = tipMessages.slice(0, count)
  }
}

// 监听数据与窗口变化触发计算
watch(result, async (newVal) => {
  if (newVal) {
    await nextTick()
    calculateHeights()
    setTimeout(calculateHeights, 150) // 延迟确保字体/动画完全撑开
  }
}, { deep: true })

onMounted(() => {
  window.addEventListener('resize', calculateHeights)
})

onUnmounted(() => {
  window.removeEventListener('resize', calculateHeights)
})

const isFormValid = computed(() => {
  return form.value.contractType && uploadedFile.value
})

const getEffectBadgeClass = (legalEffect: any) => {
  if (!legalEffect) return 'unknown'
  if (legalEffect.isValid === true) return 'valid'
  if (legalEffect.isValid === false) {
    const analysis = legalEffect.analysis || ''
    if (analysis.includes('严重') || analysis.includes('程序违法') || analysis.includes('无效') || analysis.includes('强制')) {
      return 'invalid-severe'
    }
    if (analysis.includes('次要') || analysis.includes('轻微') || analysis.includes('可补正') || analysis.includes('效力待定')) {
      return 'invalid-minor'
    }
    return 'invalid'
  }
  return 'unknown'
}

// 获取风险标签颜色（智能匹配词汇呈现对应颜色，但不替换原始文案）
const getRiskTagClass = (level: string) => {
  if (!level) return 'risk-medium'
  if (level.includes('重大') || level.includes('严重') || level.includes('极高') || level.includes('高')) {
    return 'risk-high'
  }
  if (level.includes('中等') || level.includes('中') || level.includes('次要') || level.includes('轻微')) {
    return 'risk-medium'
  }
  if (level.includes('低')) {
    return 'risk-low'
  }
  return 'risk-medium'
}

// 获取风险项左侧边界颜色
const getBorderClass = (level: string) => {
  if (!level) return 'border-medium'
  if (level.includes('重大') || level.includes('严重') || level.includes('极高') || level.includes('高')) {
    return 'border-severe'
  }
  if (level.includes('中等') || level.includes('中') || level.includes('次要') || level.includes('轻微')) {
    return 'border-medium'
  }
  if (level.includes('低')) {
    return 'border-minor'
  }
  return 'border-medium'
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    await uploadFile(file)
  }
}

const handleDrop = async (e: DragEvent) => {
  isDragover.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) {
    await uploadFile(file)
  }
}

const uploadFile = async (file: File) => {
  const validTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
  ]
  if (!validTypes.includes(file.type)) {
    alert('请上传 PDF、Word 文档')
    return
  }

  uploadedFile.value = file
  fileLoading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)
    const res: any = await contractApi.upload(formData)
    if (res.code === 200) {
      form.value.content = res.data.content
      uploadedFileName.value = res.data.fileName || ''
    } else {
      alert(res.message || '文件上传失败')
      uploadedFile.value = null
    }
  } catch (e: any) {
    alert('文件上传失败：' + (e.message || '请稍后重试'))
    uploadedFile.value = null
  } finally {
    fileLoading.value = false
  }
}

const removeFile = () => {
  uploadedFile.value = null
  form.value.content = ''
  uploadedFileName.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const handleReview = async () => {
  loading.value = true
  result.value = null
  rightPaddingTips.value = []
  leftPaddingTips.value = []
  try {
    const res: any = await contractApi.review({
      contractName: uploadedFileName.value,
      contractType: form.value.contractType,
      content: form.value.content,
      reviewMode: reviewMode.value
    })
    if (res.code === 200) {
      result.value = res.data.reviewResult
    } else {
      alert(res.message || '审查失败')
    }
  } catch (e: any) {
    alert('审查失败：' + (e.message || '请稍后重试'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.contract-review-page {
  min-height: 100vh;
  color: #eef4fc;
  background:
    linear-gradient(120deg, rgba(181, 141, 69, 0.14), rgba(181, 141, 69, 0) 38%),
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
}

.review-container {
  display: flex;
  align-items: stretch; /* 触发左右同高 */
  gap: 1.5rem;
  max-width: 1400px;
  margin: 2.2rem auto;
  padding: 0 1rem;
}

/* ===== 左侧布局 ===== */
.input-section {
  flex: 7;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
}

.left-inner-wrapper {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

.result-grid .info-card,
.result-grid .result-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 1rem;
  padding: 1.2rem;
}

/* 填补空位的卡片横跨整个网格 */
.span-full {
  grid-column: 1 / -1;
}

.mt-gap {
  margin-top: 0.5rem;
}

/* ===== 右侧布局 ===== */
.result-section {
  flex: 3;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.result-section .result-card {
  max-width: 100%;
}

.risk-full-height {
  flex: 1; /* 撑满剩余高度，让底部平齐 */
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 1rem;
  padding: 1.2rem;
}

.risk-list-wrapper {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.risk-list-wrapper::-webkit-scrollbar {
  width: 4px;
}
.risk-list-wrapper::-webkit-scrollbar-thumb {
  background: rgba(222, 193, 136, 0.3);
  border-radius: 10px;
}

/* ===== 通用组件样式 ===== */
.section-title {
  font-size: 1.4rem;
  color: #f5e3bb;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: rgba(238, 244, 252, 0.88);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 0.8rem;
  font-size: 1rem;
  color: #eef4fc;
  background: rgba(5, 21, 38, 0.45);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(238, 244, 252, 0.5);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.22);
  border-radius: 0.8rem;
  padding: 2.5rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: rgba(5, 21, 38, 0.25);
}

.upload-area:hover,
.upload-area.dragover {
  border-color: #dec188;
  background: rgba(181, 141, 69, 0.08);
}

.upload-area.has-file {
  border-style: solid;
  border-color: rgba(222, 193, 136, 0.5);
  background: rgba(181, 141, 69, 0.1);
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
}

.upload-text {
  color: rgba(238, 244, 252, 0.8);
  font-size: 1rem;
  margin-bottom: 0.3rem;
}

.upload-hint {
  color: rgba(238, 244, 252, 0.45);
  font-size: 0.85rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.file-icon {
  font-size: 2rem;
}

.file-details {
  flex: 1;
}

.file-name {
  color: #eef4fc;
  font-size: 0.95rem;
  font-weight: 500;
  word-break: break-all;
}

.file-size {
  color: rgba(238, 244, 252, 0.5);
  font-size: 0.8rem;
  margin-top: 0.2rem;
}

.remove-btn {
  background: rgba(244, 67, 54, 0.15);
  border: 1px solid rgba(244, 67, 54, 0.3);
  color: #e57373;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-btn:hover {
  background: rgba(244, 67, 54, 0.3);
}

.mode-selector {
  display: flex;
  gap: 0.8rem;
}

.mode-btn {
  flex: 1;
  padding: 0.7rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 0.8rem;
  background: rgba(5, 21, 38, 0.45);
  color: rgba(238, 244, 252, 0.7);
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 0.95rem;
}

.mode-btn:hover {
  border-color: rgba(222, 193, 136, 0.5);
  color: #f5e8ca;
}

.mode-btn.active {
  background: rgba(181, 141, 69, 0.2);
  border-color: #dec188;
  color: #f5e8ca;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  border-radius: 999px;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state,
.loading-state {
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: 1rem;
  padding: 3rem 2rem;
  text-align: center;
  color: rgba(238, 244, 252, 0.5);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #dec188;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.info-card h3,
.result-card h3 {
  font-size: 1rem;
  color: #f5e3bb;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.4rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: rgba(238, 244, 252, 0.6);
  font-size: 0.9rem;
}

.info-row .value {
  color: #eef4fc;
  font-weight: 500;
}

.effect-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
}

.effect-badge.valid {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.effect-badge.invalid {
  background: rgba(244, 67, 54, 0.2);
  color: #e57373;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.effect-badge.unknown {
  background: rgba(158, 158, 158, 0.2);
  color: #bdbdbd;
  border: 1px solid rgba(158, 158, 158, 0.4);
}

.effect-badge.invalid-severe {
  background: rgba(220, 20, 60, 0.25);
  color: #ff6b6b;
  border: 1px solid rgba(220, 20, 60, 0.5);
}

.effect-badge.invalid-minor {
  background: rgba(255, 193, 7, 0.25);
  color: #ffd54f;
  border: 1px solid rgba(255, 193, 7, 0.5);
}

.effect-analysis {
  color: rgba(238, 244, 252, 0.8);
  line-height: 1.6;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
}

.risk-level {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.level-label {
  color: rgba(238, 244, 252, 0.6);
  font-size: 0.9rem;
}

.level-value {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.level-high {
  background: rgba(244, 67, 54, 0.2);
  color: #e57373;
}

.level-medium {
  background: rgba(255, 152, 0, 0.2);
  color: #ffb74d;
}

.level-low {
  background: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

/* ===== 风险点审查动态标签样式 ===== */
.risk-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 0.6rem;
  padding: 1rem;
  border-left: 3px solid #81c784;
}

.risk-item.border-severe {
  border-left-color: #ff6b6b;
}
.risk-item.border-medium {
  border-left-color: #ffd54f;
}
.risk-item.border-minor {
  border-left-color: #81c784;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.risk-index {
  width: 20px;
  height: 20px;
  background: rgba(222, 193, 136, 0.2);
  color: #dec188;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.risk-clause {
  flex: 1;
  color: #eef4fc;
  font-size: 0.9rem;
}

.risk-level-tag {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: 1.8rem;
  margin-bottom: 0.8rem;
}

.risk-level-tag.risk-high {
  background: rgba(220, 20, 60, 0.25);
  color: #ff6b6b;
  border: 1px solid rgba(220, 20, 60, 0.4);
}
.risk-level-tag.risk-medium {
  background: rgba(255, 193, 7, 0.25);
  color: #ffd54f;
  border: 1px solid rgba(255, 193, 7, 0.4);
}
.risk-level-tag.risk-low {
  background: rgba(76, 175, 80, 0.25);
  color: #81c784;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.risk-content {
  padding-left: 1.8rem;
  font-size: 0.85rem;
  line-height: 1.5;
}

.risk-desc {
  margin-bottom: 0.8rem;
}

.risk-suggestion {
  margin-bottom: 0;
}

.risk-desc,
.risk-suggestion {
  color: rgba(238, 244, 252, 0.75);
}

.risk-desc strong,
.risk-suggestion strong {
  color: rgba(238, 244, 252, 0.9);
}

.summary-content,
.suggestion-content {
  color: rgba(238, 244, 252, 0.8);
  line-height: 1.7;
  font-size: 0.9rem;
}

.tips-content {
  color: rgba(238, 244, 252, 0.75);
  line-height: 1.8;
  font-size: 0.9rem;
}

.tips-content p {
  margin-bottom: 0.15rem;
}

.padding-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 1rem;
  padding: 1.2rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .review-container {
    flex-direction: column;
  }

  .result-section {
    min-width: auto;
  }

  .form-row {
    flex-direction: column;
  }

  .result-grid {
    grid-template-columns: 1fr;
  }
}
</style>