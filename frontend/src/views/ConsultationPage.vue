<template>
  <div class="consultation-page">
    <!-- 顶部导航栏（带侧边栏控制） -->
    <TopNavBar />

    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newChat">
          <span class="icon">+</span>
          开启新对话
        </button>
      </div>

      <div class="history-section">
        <div class="history-date" v-for="(group, date) in groupedHistory" :key="date">
          <div class="date-label">{{ date }}</div>
          <div
            v-for="chat in group"
            :key="chat.id"
            class="history-item"
            :class="{ active: currentChatId === chat.id }"
            @click="loadChat(chat)"
          >
            <span class="chat-title">{{ chat.title }}</span>
            <button class="delete-btn" @click.stop="deleteChat(chat.id)" title="删除">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="Object.keys(groupedHistory).length === 0" class="no-history">
          暂无历史记录
        </div>
      </div>
    </aside>

    <!-- 右侧主内容区 -->
    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 侧边栏折叠按钮 -->
      <button class="sidebar-toggle-btn" @click="toggleSidebar" :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
        <span class="toggle-icon">{{ sidebarCollapsed ? '☰' : '✕' }}</span>
      </button>

      <!-- 状态A：无对话时 - 居中布局 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-state-content">
          <h2 class="welcome-title">您好，我是法研智谱法律智能助手</h2>
          <p class="welcome-desc">请描述您遇到的法律问题，LawIntelEmpower 将为您提供专业的法律建议。</p>
          <div class="quick-prompts">
            <button class="prompt-btn" @click="quickAsk('婚姻家庭纠纷如何处理？')">婚姻家庭纠纷如何处理？</button>
            <button class="prompt-btn" @click="quickAsk('劳动仲裁的流程是什么？')">劳动仲裁的流程是什么？</button>
            <button class="prompt-btn" @click="quickAsk('合同纠纷的诉讼时效？')">合同纠纷的诉讼时效？</button>
          </div>
        </div>

        <!-- 输入框也居中显示 -->
        <div class="input-area input-area-center">
          <div class="input-container">
            <div class="input-center">
              <textarea
                v-model="inputText"
                placeholder="输入您的法律问题..."
                rows="1"
                :disabled="loading"
                @keydown.enter.exact.prevent="sendMessage"
              ></textarea>
            </div>
            <div class="input-right">
              <button
                class="send-btn"
                :disabled="loading || !inputText.trim()"
                @click="sendMessage"
              >
                <span class="send-icon">➤</span>
              </button>
            </div>
          </div>
          <div class="input-tip">AI 生成内容仅供参考，不构成法律意见</div>
        </div>
      </div>

      <!-- 状态B：有对话时 - 聊天流布局 -->
      <div v-else class="chat-state">
        <div class="chat-content-wrapper">
          <div class="chat-messages" ref="messagesContainer">
            <!-- 消息列表 -->
            <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
              <div class="message-body">
                <div class="message-content">{{ msg.content }}</div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="loading" class="message assistant loading">
              <div class="message-body">
                <div class="message-content">AI正在思考中...</div>
              </div>
            </div>
          </div>

          <!-- 输入框固定在底部 -->
          <div class="input-area input-area-fixed">
          <div class="input-container">
            <div class="input-center">
              <textarea
                v-model="inputText"
                placeholder="输入您的法律问题..."
                rows="1"
                :disabled="loading"
                @keydown.enter.exact.prevent="sendMessage"
              ></textarea>
            </div>
            <div class="input-right">
              <button
                class="send-btn"
                :disabled="loading || !inputText.trim()"
                @click="sendMessage"
              >
                <span class="send-icon">➤</span>
              </button>
            </div>
          </div>
          <div class="input-tip">AI 生成内容仅供参考，不构成法律意见</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { consultationApi } from '@/api'
import TopNavBar from '@/components/TopNavBar.vue'

type ChatMessage = { role: string; content: string; time: string }
type ChatHistory = { id: string; title: string; messages: ChatMessage[]; time: Date }

// 状态管理
const sidebarCollapsed = ref(false)  // 侧边栏展开/收缩状态
const category = ref('')
const inputText = ref('')
const messages = ref<ChatMessage[]>([])
const loading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const currentChatId = ref<string | null>(null)
const chatHistory = ref<ChatHistory[]>([])

const CHAT_STATE_KEY = 'lexai-consultation-chat-state'
const CHAT_HISTORY_KEY = 'lexai-consultation-history'
const SIDEBAR_KEY = 'lexai-sidebar-collapsed'

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  sessionStorage.setItem(SIDEBAR_KEY, sidebarCollapsed.value.toString())
}

// 按日期分组历史记录
const groupedHistory = computed(() => {
  const groups: Record<string, ChatHistory[]> = {}
  chatHistory.value.forEach(chat => {
    const dateKey = formatDateGroup(chat.time)
    if (!groups[dateKey]) groups[dateKey] = []
    groups[dateKey].push(chat)
  })
  return groups
})

const formatDateGroup = (date: Date) => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const chatDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.floor((today.getTime() - chatDate.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays === 0) return '今天'
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return '近7天'
  if (diffDays < 30) return '近30天'
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' })
}

const newChat = () => {
  messages.value = []
  currentChatId.value = null
  saveHistory()
}

const loadChat = (chat: ChatHistory) => {
  messages.value = [...chat.messages]
  currentChatId.value = chat.id
}

const deleteChat = (chatId: string) => {
  const idx = chatHistory.value.findIndex(c => c.id === chatId)
  if (idx !== -1) {
    chatHistory.value.splice(idx, 1)
    sessionStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory.value))
    if (currentChatId.value === chatId) {
      messages.value = []
      currentChatId.value = null
    }
  }
}

const saveHistory = () => {
  if (messages.value.length > 0) {
    const title = messages.value[0]?.content?.substring(0, 30) || '新对话'
    const chat: ChatHistory = {
      id: currentChatId.value || Date.now().toString(),
      title: title + (messages.value[0].content.length > 30 ? '...' : ''),
      messages: [...messages.value],
      time: new Date()
    }
    if (currentChatId.value) {
      const idx = chatHistory.value.findIndex(c => c.id === currentChatId.value)
      if (idx !== -1) chatHistory.value[idx] = chat
    } else {
      chatHistory.value.unshift(chat)
      currentChatId.value = chat.id
    }
    sessionStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory.value))
  }
}

const restoreChatState = () => {
  const raw = sessionStorage.getItem(CHAT_STATE_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed.messages)) messages.value = parsed.messages
    if (typeof parsed.category === 'string') category.value = parsed.category
  } catch {
    sessionStorage.removeItem(CHAT_STATE_KEY)
  }
}

const persistChatState = () => {
  sessionStorage.setItem(CHAT_STATE_KEY, JSON.stringify({ messages: messages.value, category: category.value }))
}

const restoreHistory = () => {
  const raw = sessionStorage.getItem(CHAT_HISTORY_KEY)
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    chatHistory.value = parsed.map((c: any) => ({ ...c, time: new Date(c.time) }))
  } catch {
    sessionStorage.removeItem(CHAT_HISTORY_KEY)
  }
}

const restoreSidebarState = () => {
  const raw = sessionStorage.getItem(SIDEBAR_KEY)
  if (raw !== null) sidebarCollapsed.value = raw === 'true'
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  })
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return
  const userMessage = {
    role: 'user',
    content: inputText.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  messages.value.push(userMessage)
  const question = inputText.value
  inputText.value = ''
  loading.value = true
  saveHistory()

  try {
    const res: any = await consultationApi.ask({ question, category: '' })
    if (res.code === 200) {
      messages.value.push({ role: 'assistant', content: res.data.answer, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
    } else {
      messages.value.push({ role: 'assistant', content: '抱歉，' + res.message, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
    }
  } catch (e: any) {
    const backendMessage = e?.response?.data?.message || e?.response?.data?.msg || e?.message || 'AI服务暂时不可用，请稍后再试。'
    messages.value.push({ role: 'assistant', content: `请求失败：${backendMessage}`, time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) })
  } finally {
    loading.value = false
    saveHistory()
  }
}

const quickAsk = (text: string) => { inputText.value = text; sendMessage() }

onMounted(() => { restoreChatState(); restoreHistory(); restoreSidebarState(); scrollToBottom() })
watch([messages, category], () => { persistChatState() }, { deep: true })
</script>

<style scoped>
/* ===== 整体布局 ===== */
.consultation-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  color: #eef4fc;
  background: #0a0e17;
}

/* ===== 侧边栏 ===== */
.sidebar {
  position: fixed;
  top: 85px;
  left: 0;
  width: 265px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #0d1520 0%, #0a1019 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 0.3s ease;
  z-index: 100;
}

.sidebar.collapsed {
  transform: translateX(-100%);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.new-chat-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(181, 141, 69, 0.25), rgba(181, 141, 69, 0.15));
  border: 1px solid rgba(222, 193, 136, 0.35);
  border-radius: 12px;
  color: #dec188;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.new-chat-btn:hover {
  background: linear-gradient(135deg, rgba(181, 141, 69, 0.35), rgba(181, 141, 69, 0.2));
  border-color: rgba(222, 193, 136, 0.6);
}

.new-chat-btn .icon { font-size: 1.1rem; font-weight: 700; }

/* 主内容区左上角的侧边栏折叠/展开按钮 */
.sidebar-toggle-btn {
  position: absolute;
  top: 45px;
  left: 16px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(238, 244, 252, 0.7);
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 60;
}

.sidebar-toggle-btn:hover {
  background: rgba(51, 65, 85, 0.95);
  border-color: rgba(181, 141, 69, 0.4);
  color: #dec188;
}

.toggle-icon {
  font-size: 0.9rem;
  line-height: 1;
}

.history-section {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.history-date { margin-bottom: 1rem; }

.date-label {
  font-size: 0.7rem;
  color: rgba(238, 244, 252, 0.4);
  padding: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05rem;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(238, 244, 252, 0.65);
}

.history-item:hover { background: rgba(255, 255, 255, 0.06); color: #eef4fc; }
.history-item:hover .delete-btn { opacity: 1; }
.history-item.active { background: rgba(181, 141, 69, 0.15); color: #dec188; }

.chat-title {
  flex: 1;
  font-size: 0.85rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(238, 244, 252, 0.35);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.delete-btn:hover { color: #ef4444; }

.no-history {
  text-align: center;
  color: rgba(238, 244, 252, 0.35);
  padding: 2rem 1rem;
  font-size: 0.85rem;
}

/* ===== 右侧主内容区 ===== */
.main-content {
  position: fixed;
  top: 60px;
  left: 260px;
  right: 0;
  bottom: 0;
  transition: left 0.3s ease;
  background: #0a0e17;
}

.main-content.sidebar-collapsed {
  left: 0;
}

/* ===== 状态A：空状态（居中布局） ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 60px);
  padding: 2rem;
}

.empty-state-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-icon { font-size: 3rem; margin-bottom: 1rem; }

.welcome-title {
  font-size: 1.75rem;
  color: #eef4fc;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.welcome-desc {
  color: rgba(238, 244, 252, 0.5);
  font-size: 1rem;
  margin-bottom: 2rem;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
}

.prompt-btn {
  padding: 0.6rem 1.2rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  color: rgba(238, 244, 252, 0.75);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.25s ease;
}

.prompt-btn:hover {
  background: rgba(181, 141, 69, 0.15);
  border-color: rgba(222, 193, 136, 0.4);
  color: #dec188;
}

/* 居中布局的输入框 */
.input-area-center {
  width: 100%;
  max-width: 600px;
}

.input-area-center .input-container {
  background: rgba(20, 28, 40, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 0.5rem 0.75rem;
}

/* ===== 状态B：聊天状态 ===== */
.chat-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: calc(100vh - 60px);
}

.chat-content-wrapper {
  width: 100%;
  max-width: 55%;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 隐藏滚动条但保持滚动功能 */
.chat-messages::-webkit-scrollbar {
  display: none;
}
/*AI辅助生成：通义灵码qwen3-coder，2026年4月14日
.chat-messages {
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex: 1;
  overflow-y: auto;
  padding: 2.5rem 0 100px;
}

/* ===== 消息气泡 ===== */
.message {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  max-width: 100%;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #ba9654, #d7bc86);
}

.message.assistant .message-avatar {
  background: linear-gradient(135deg, #1a3a5c, #2a4a6c);
  border: 1px solid rgba(181, 141, 69, 0.3);
}

.message-body {
  max-width: fit-content;
}

/* 用户消息 */
.message.user .message-body {
  max-width: 70%;
}

.message-content {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: fit-content;
  font-size: 0.95rem;
}

/* 用户消息：宽度自适应 */
.message.user .message-content {
  background: linear-gradient(135deg, #ba9654, #d7bc86);
  color: #1a1f29;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-content {
  background: rgba(255, 255, 255, 0.06);
  color: #eef4fc;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 0.7rem;
  color: rgba(238, 244, 252, 0.4);
  margin-top: 0.4rem;
  padding: 0 0.5rem;
}

.message.user .message-time { text-align: right; }

.message.loading .message-content {
  background: rgba(255, 255, 255, 0.04);
  font-style: italic;
}

/* ===== 底部输入框（固定） ===== */
.chat-content-wrapper .input-area-fixed {
  position: static;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem 0 1.5rem;
  background: transparent;
  border-top: none;
}

.input-area-fixed {
  position: fixed;
  bottom: 0;
  left: 260px;
  right: 0;
  background: #0a0e17;
  padding: 1rem 1.5rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  transition: left 0.3s ease;
  z-index: 50;
}

.main-content.sidebar-collapsed .input-area-fixed {
  left: 0;
}

.input-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(20, 28, 40, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 0.5rem 0.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.25s ease;
}

.input-container:focus-within {
  border-color: rgba(181, 141, 69, 0.4);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35), 0 0 0 2px rgba(181, 141, 69, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.input-center { flex: 1; }

.input-center textarea {
  width: 100%;
  padding: 0.6rem 0.5rem;
  background: transparent;
  border: none;
  color: #eef4fc;
  font-size: 0.95rem;
  resize: none;
  outline: none;
  line-height: 1.5;
  max-height: 120px;
  min-height: 24px;
}

.input-center textarea::placeholder { color: rgba(238, 244, 252, 0.4); }

.input-right { flex-shrink: 0; }

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ba9654, #d7bc86);
  border: none;
  color: #1a1f29;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(181, 141, 69, 0.4);
}

.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.send-icon { transform: rotate(-45deg); }

.input-tip {
  text-align: center;
  font-size: 0.7rem;
  color: rgba(238, 244, 252, 0.3);
  margin-top: 0.75rem;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .sidebar { display: none; }
  .main-content { margin-left: 0; }
  .input-area-fixed { left: 0; }
  .message-body { max-width: 85%; }
}
</style>