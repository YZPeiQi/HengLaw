<template>
  <div class="document-generate-page">
    <TopNavBar />

    <main class="generate-container">
      <!-- 左侧面板 - 基础文书信息 -->
      <div class="left-panel">
        <h2 class="panel-title">文书生成</h2>

        <div class="form-group">
          <label>文书类型</label>
          <select v-model="form.docType">
            <option value="">请选择文书类型</option>
            <option value="起诉状">民事起诉状</option>
            <option value="答辩状">答辩状</option>
            <option value="上诉状">上诉状</option>
            <option value="申请书">申请书</option>
          </select>
        </div>

        <div class="form-group">
          <label>案件标题（可选）</label>
          <input v-model="form.title" type="text" placeholder="请输入案件标题" />
        </div>

        <div class="form-group">
          <label>案件描述</label>
          <textarea
            v-model="form.caseDescription"
            placeholder="请详细描述案件情况..."
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label>诉讼请求</label>
          <textarea
            v-model="form.claim"
            placeholder="请描述您的诉讼请求..."
            rows="3"
          ></textarea>
        </div>

        <button @click="handleGenerate" class="submit-btn btn-glow" :disabled="loading || !form.docType">
          {{ loading ? '生成中...' : '生成文书' }}
        </button>
      </div>

      <!-- 右侧面板 - 当事人信息卡片 -->
      <div class="right-panel">
        <!-- 大卡片包装器 -->
        <div class="info-cards-wrapper">
          <!-- 原告/甲方信息卡片 -->
          <div class="info-card">
            <h3 class="card-title">原告/甲方信息</h3>

            <div class="card-content">
              <div class="form-group">
                <label>姓名</label>
                <input v-model="form.partyAInfo.name" type="text" placeholder="请输入姓名" />
              </div>

              <div class="form-group">
                <label>证件类型</label>
                <select v-model="form.partyAInfo.idType">
                  <option value="身份证">身份证</option>
                  <option value="护照">护照</option>
                  <option value="营业执照">营业执照</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              <div class="form-group">
                <label>证件号</label>
                <input v-model="form.partyAInfo.idNumber" type="text" placeholder="请输入证件号码" />
              </div>

              <div class="form-group">
                <label>联系电话</label>
                <input v-model="form.partyAInfo.phone" type="tel" placeholder="请输入联系电话" />
              </div>

              <div class="form-group">
                <label>地址</label>
                <input v-model="form.partyAInfo.address" type="text" placeholder="请输入地址" />
              </div>
            </div>
          </div>

          <!-- 被告/乙方信息卡片 -->
          <div class="info-card">
            <h3 class="card-title">被告/乙方信息</h3>

            <div class="card-content">
              <div class="form-group">
                <label>姓名</label>
                <input v-model="form.partyBInfo.name" type="text" placeholder="请输入姓名" />
              </div>

              <div class="form-group">
                <label>证件类型</label>
                <select v-model="form.partyBInfo.idType">
                  <option value="身份证">身份证</option>
                  <option value="护照">护照</option>
                  <option value="营业执照">营业执照</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              <div class="form-group">
                <label>证件号</label>
                <input v-model="form.partyBInfo.idNumber" type="text" placeholder="请输入证件号码" />
              </div>

              <div class="form-group">
                <label>联系电话</label>
                <input v-model="form.partyBInfo.phone" type="tel" placeholder="请输入联系电话" />
              </div>

              <div class="form-group">
                <label>地址</label>
                <input v-model="form.partyBInfo.address" type="text" placeholder="请输入地址" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 生成结果弹窗 -->
    <div v-if="generatedContent" class="result-modal" @click.self="closeResult">
      <div class="result-section">
        <div class="result-header">
          <h2>生成的文书</h2>
          <div class="action-buttons">
            <button @click="copyContent" class="action-btn copy-btn">复制内容</button>
            <button @click="downloadWord" class="action-btn download-btn">下载为Word</button>
            <button @click="closeResult" class="action-btn close-btn">关闭</button>
          </div>
        </div>
        <div class="result-content">
          <pre>{{ generatedContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { documentApi } from '@/api'
import TopNavBar from '@/components/TopNavBar.vue'

const form = ref({
  docType: '',
  title: '',
  caseDescription: '',
  claim: '',
  partyAInfo: {
    name: '',
    idType: '身份证',
    idNumber: '',
    phone: '',
    address: ''
  },
  partyBInfo: {
    name: '',
    idType: '身份证',
    idNumber: '',
    phone: '',
    address: ''
  }
})
const generatedContent = ref('')
const loading = ref(false)

const normalizeDocumentText = (text: string) => {
  if (!text) return ''

  let cleaned = text
  cleaned = cleaned.replace(/```json/g, '')
  cleaned = cleaned.replace(/```/g, '')
  cleaned = cleaned.replace(/\*\*/g, '')
  cleaned = cleaned.replace(/__/g, '')
  cleaned = cleaned.replace(/`/g, '')
  cleaned = cleaned.replace(/^\s{0,3}#{1,6}\s*/gm, '')
  cleaned = cleaned.replace(/^\s{0,3}[*+-]\s+/gm, '')
  cleaned = cleaned.replace(/^\s{0,3}\d+[.)]\s+/gm, '')
  cleaned = cleaned.replace(/^\s*\*([^*\r\n]+)\*\s*$/gm, '$1')
  cleaned = cleaned.replace(/\uFFFD/g, '')
  cleaned = cleaned.replace(/[\u200B-\u200D\uFEFF]/g, '')
  cleaned = cleaned.replace(/[ \t]+(?=\r?\n)/g, '')
  cleaned = cleaned.replace(/(\r?\n){3,}/g, '\n\n')

  return cleaned.trim()
}

const escapeHtml = (text: string) =>
  text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const handleGenerate = async () => {
  loading.value = true
  try {
    // 构建完整表单数据，合并当事人信息
    const submitData = {
      docType: form.value.docType,
      title: form.value.title,
      caseDescription: form.value.caseDescription,
      claim: form.value.claim,
      partyA: form.value.partyAInfo.name,
      partyB: form.value.partyBInfo.name,
      partyAInfo: form.value.partyAInfo,
      partyBInfo: form.value.partyBInfo
    }

    const res: any = await documentApi.generate(submitData)
    if (res.code === 200) {
      generatedContent.value = normalizeDocumentText(res.data.content || '')
    } else {
      alert(res.message || '生成失败')
    }
  } catch (e: any) {
    alert('生成失败: ' + (e.response?.data?.message || e.message || '请稍后重试'))
  } finally {
    loading.value = false
  }
}

const closeResult = () => {
  generatedContent.value = ''
}

const copyContent = () => {
  navigator.clipboard.writeText(generatedContent.value)
  alert('已复制到剪贴板')
}

const downloadWord = () => {
  if (!generatedContent.value) return

  const formattedContent = escapeHtml(generatedContent.value).replace(/\n/g, '<br>')
  const htmlTemplate = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset='utf-8'><title>Export Info</title></head>
    <body>
      <div style="font-family: SimSun, serif; font-size: 14pt; line-height: 1.5;">
        ${formattedContent}
      </div>
    </body>
    </html>
  `

  const blob = new Blob([htmlTemplate], { type: 'application/msword;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url

  const fileName = form.value.title
    ? `${form.value.title}.doc`
    : `${form.value.docType || '法律文书'}.doc`

  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.document-generate-page {
  min-height: 100vh;
  color: #eef4fc;
  background: #0a0e17;
}

.generate-container {
  display: flex;
  gap: 1.5rem;
  max-width: 89%;
  margin: 2.2rem auto;
  padding: 0 1rem;
  min-height: calc(100vh - 120px);
}

/* ===== 左侧面板 ===== */
.left-panel {
  flex: 4;
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
}

.panel-title {
  font-size: 1.4rem;
  color: #f5e3bb;
  margin-bottom: 1.5rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* ===== 右侧面板 ===== */
.right-panel {
  flex: 4;
  display: flex;
  min-height: 500px;
}

/* ===== 大卡片包装器 ===== */
.info-cards-wrapper {
  flex: 1;
  display: flex;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
}

/* ===== 信息卡片（水平排列） ===== */
.info-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.8rem;
  padding: 1rem;
}

.card-title {
  font-size: 1.1rem;
  color: #f5e3bb;
  margin-bottom: 1rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

/* ===== 表单控件 ===== */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.4rem;
  font-weight: 500;
  color: rgba(238, 244, 252, 0.88);
  font-size: 0.85rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.7rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 0.6rem;
  font-size: 0.95rem;
  color: #eef4fc;
  background: rgba(5, 21, 38, 0.45);
  transition: all 0.25s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: rgba(222, 193, 136, 0.5);
  outline: none;
  box-shadow: 0 0 0 2px rgba(181, 141, 69, 0.15);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(238, 244, 252, 0.5);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.5;
}

/* ===== 提交按钮 ===== */
.submit-btn {
  width: 100%;
  padding: 1rem;
  border-radius: 999px;
  font-size: 1rem;
  margin-top: 1rem;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ===== 结果弹窗 ===== */
.result-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.result-section {
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 24px 65px rgba(0, 0, 0, 0.22);
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.result-header h2 {
  font-size: 1.2rem;
  color: #f5e3bb;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.26);
  color: #eef4fc;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.22s ease;
}

.action-btn:hover {
  border-color: rgba(222, 193, 136, 0.85);
  color: #f5e3bb;
}

.close-btn {
  background: rgba(244, 67, 54, 0.15);
  border-color: rgba(244, 67, 54, 0.3);
  color: #e57373;
}

.result-content {
  background: rgba(255, 255, 255, 0.08);
  padding: 1.5rem;
  border-radius: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.result-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  line-height: 1.8;
  color: rgba(238, 244, 252, 0.85);
  margin: 0;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .generate-container {
    flex-direction: column;
  }

  .right-panel {
    min-height: auto;
  }

  .info-cards-wrapper {
    flex-direction: column;
  }
}
</style>