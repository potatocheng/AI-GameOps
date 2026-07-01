<template>
  <div class="agent-chat">
    <div class="chat-header">
      <div class="header-content">
        <div class="agent-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="agent-info">
          <h1 class="agent-name">AI 智能助手</h1>
          <span class="agent-status">
            <span class="status-dot"></span>
            在线
          </span>
        </div>
      </div>
      <button class="clear-btn" @click="clearHistory">
        清空对话
      </button>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h2>欢迎使用 AI 智能助手</h2>
        <p>我可以帮助您：</p>
        <ul>
          <li>回答问题和提供信息</li>
          <li>协助处理反馈相关问题</li>
          <li>提供使用指导和帮助</li>
          <li>解答技术疑问</li>
        </ul>
      </div>

      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-avatar">
          <svg v-if="message.role === 'assistant'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="isTyping" class="message assistant">
        <div class="message-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <form @submit.prevent="sendMessage" class="input-form">
        <textarea
          v-model="inputMessage"
          class="message-input"
          placeholder="输入您的消息... (Enter发送, Shift+Enter换行)"
          rows="1"
          @keydown="handleKeydown"
          ref="inputRef"
        ></textarea>
        <button 
          type="submit" 
          class="send-btn"
          :disabled="!inputMessage.trim() || isTyping"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { sendMessage as sendChatMessage, clearChatHistory } from '@/api'
import type { ChatMessage } from '@/types'

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const isTyping = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)
const userId = ref(`user_${Date.now()}`)

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

async function sendMessage() {
  if (!inputMessage.value.trim() || isTyping.value) return

  const userMessage: ChatMessage = {
    id: Date.now(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString()
  }

  messages.value.push(userMessage)
  const messageToSend = inputMessage.value.trim()
  inputMessage.value = ''
  scrollToBottom()

  isTyping.value = true

  try {
    const response = await sendChatMessage({
      message: messageToSend,
      user_id: userId.value
    })

    if (response) {
      const assistantMessage: ChatMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp
      }
      messages.value.push(assistantMessage)
    } else {
      // 模拟响应
      const assistantMessage: ChatMessage = {
        id: Date.now(),
        role: 'assistant',
        content: '抱歉，我暂时无法连接到服务器。请稍后重试。',
        timestamp: new Date().toISOString()
      }
      messages.value.push(assistantMessage)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    const errorMessage: ChatMessage = {
      id: Date.now(),
      role: 'assistant',
      content: '抱歉，发生了错误。请稍后重试。',
      timestamp: new Date().toISOString()
    }
    messages.value.push(errorMessage)
  } finally {
    isTyping.value = false
    scrollToBottom()
  }
}

async function clearHistory() {
  if (confirm('确定要清空所有对话记录吗？')) {
    await clearChatHistory(userId.value)
    messages.value = []
  }
}

onMounted(() => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
})
</script>

<style scoped>
.agent-chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  background: #f5f7fa;
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.agent-avatar {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.agent-avatar svg {
  width: 24px;
  height: 24px;
  color: white;
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.agent-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.clear-btn {
  padding: 8px 16px;
  font-size: 13px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-btn:hover {
  background: #e0e0e0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  text-align: center;
  padding: 60px 24px;
  max-width: 600px;
  margin: auto;
}

.welcome-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.welcome-icon svg {
  width: 32px;
  height: 32px;
  color: white;
}

.welcome-message h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 16px;
}

.welcome-message p {
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
}

.welcome-message ul {
  text-align: left;
  display: inline-block;
  color: #666;
}

.welcome-message li {
  margin: 8px 0;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #10b981;
}

.message-avatar svg {
  width: 20px;
  height: 20px;
  color: white;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-time {
  font-size: 11px;
  color: #999;
  padding: 0 8px;
}

.message.user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 16px 24px;
}

.input-form {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 12px;
  resize: none;
  max-height: 120px;
  font-family: inherit;
  transition: all 0.3s;
  box-sizing: border-box;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.send-btn {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
  color: white;
}

@media (max-width: 768px) {
  .agent-chat {
    height: calc(100vh - 64px);
  }
  
  .chat-header {
    padding: 12px 16px;
  }
  
  .chat-messages {
    padding: 16px;
  }
  
  .message {
    max-width: 90%;
  }
  
  .chat-input-area {
    padding: 12px 16px;
  }
  
  .send-btn {
    width: 40px;
    height: 40px;
  }
}
</style>